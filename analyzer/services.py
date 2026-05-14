import os
import requests
import json
import google.generativeai as genai
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .models import Kategori, Marka, Platform, Urun, UrunPlatformHaritasi, Yorum, AiUrunOzeti, UrunAnalizDetayi
from dotenv import load_dotenv
from duckduckgo_search import DDGS

load_dotenv(override=True)

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_product_image(query):
    try:
        # Timeout ekleyerek çok beklemesini engelliyoruz
        ddgs = DDGS(timeout=2)
        results = [r for r in ddgs.images(f"{query} png transparent", max_results=1)]
        if results and 'image' in results[0]:
            return results[0]['image']
    except Exception as e:
        print(f"DuckDuckGo Image Error: {e}")
    return None

def search_youtube_video(query):
    if not YOUTUBE_API_KEY:
        print("YouTube API Key is missing.")
        return None
        
    search_url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'part': 'snippet',
        'q': f"{query} inceleme",
        'type': 'video',
        'relevanceLanguage': 'tr',
        'maxResults': 1,
        'key': YOUTUBE_API_KEY
    }
    
    response = requests.get(search_url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get('items'):
            video = data['items'][0]
            return {
                'video_id': video['id']['videoId'],
                'title': video['snippet']['title'],
                'url': f"https://www.youtube.com/watch?v={video['id']['videoId']}"
            }
    else:
        print(f"YouTube Search API Error: {response.status_code} - {response.text}")
    return None

def fetch_youtube_comments(video_id, max_results=50):
    if not YOUTUBE_API_KEY:
        return []
        
    comments_url = "https://www.googleapis.com/youtube/v3/commentThreads"
    params = {
        'part': 'snippet',
        'videoId': video_id,
        'maxResults': max_results,
        'order': 'relevance',
        'key': YOUTUBE_API_KEY
    }
    
    response = requests.get(comments_url, params=params)
    comments = []
    
    if response.status_code == 200:
        data = response.json()
        for item in data.get('items', []):
            snippet = item['snippet']['topLevelComment']['snippet']
            comments.append({
                'text': snippet['textOriginal'],
                'author': snippet['authorDisplayName'],
                'published_at': snippet['publishedAt'],
                'like_count': snippet['likeCount']
            })
    else:
        print(f"YouTube Comments API Error: {response.status_code} - {response.text}")
    return comments

def analyze_comments_with_gemini(comments, product_name):
    if not GEMINI_API_KEY:
        print("Gemini API Key is missing.")
        return None
        
    # Yorumları birleştir
    comments_text = "\n---\n".join([c['text'] for c in comments[:50]])
    
    prompt = f"""
    Sen teknolojik ürünleri inceleyen bir yapay zeka uzmanısın. Aşağıda "{product_name}" ürünü için YouTube videolarına yapılmış gerçek kullanıcı yorumları bulunmaktadır.
    Bu yorumları analiz et ve BİREBİR aşağıdaki JSON formatında bir çıktı üret.

    İstenen Çıktı Formatı:
    {{
        "genel_skor": 85,
        "pozitif_yorum_orani": 70,
        "ozet": "Ürünün genel özelliklerini ve kullanıcıların düşüncelerini özetleyen metin.",
        "analizler": [
            {{"konu": "Performans", "puan": 90, "ozet": "Performansla ilgili kısa değerlendirme"}},
            {{"konu": "Tasarım", "puan": 80, "ozet": "Tasarım ile ilgili kısa değerlendirme"}},
            {{"konu": "Fiyat/Performans", "puan": 75, "ozet": "Fiyat performans değerlendirmesi"}}
        ],
        "one_cikan_yorumlar": [
            "Kullanıcıların genel olarak değindiği 1. ana fikir",
            "Kullanıcıların genel olarak değindiği 2. ana fikir",
            "Kullanıcıların genel olarak değindiği 3. ana fikir"
        ]
    }}
    
    Yorumlar:
    {comments_text}
    """
    
    model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
    try:
        response = model.generate_content(prompt)
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini API Error: {e}")
        return None

def process_product_analysis(query):
    # --- ZEKİ CACHING MANTIĞI ---
    urun = Urun.objects.filter(model_adi__iexact=query).first()
    if urun:
        ozet = AiUrunOzeti.objects.filter(urun=urun).first()
        if ozet and ozet.son_guncelleme_tarihi:
            zaman_farki = timezone.now().date() - ozet.son_guncelleme_tarihi
            if zaman_farki.days < 1:
                # Veritabanından Cache'i getir
                detaylar = UrunAnalizDetayi.objects.filter(urun=urun)
                harita = UrunPlatformHaritasi.objects.filter(urun=urun, platform__platform_adi="YouTube").first()
                yorum_sayisi = Yorum.objects.filter(harita=harita).count() if harita else 0
                
                analysis_data = {
                    "genel_skor": ozet.genel_duygu_ortalamasi,
                    "pozitif_yorum_orani": ozet.genel_duygu_ortalamasi,
                    "ozet": ozet.genel_ozet_metni,
                    "analizler": [{"konu": d.analiz_konusu, "puan": d.konu_puani, "ozet": d.konu_ozeti} for d in detaylar],
                    "one_cikan_yorumlar": ["💡 Teknoliz Zeka Motoru bu veriyi Singapur sunucularımızdan anında getirdi! (Önbellekten Yüklendi)"]
                }
                return {
                    "success": True,
                    "product_name": urun.model_adi,
                    "video_url": harita.platform_urun_url if harita else "#",
                    "product_image_url": get_product_image(urun.model_adi),
                    "analysis": analysis_data,
                    "comment_count": yorum_sayisi,
                    "cached": True
                }
    # ----------------------------

    # 1. Varsayılan Kategori, Marka ve Platform
    kategori, _ = Kategori.objects.get_or_create(kategori_adi="Genel Kategori")
    marka, _ = Marka.objects.get_or_create(marka_adi="Belirtilmemiş")
    platform, _ = Platform.objects.get_or_create(platform_adi="YouTube", defaults={'base_url': 'https://www.youtube.com'})
    
    # 2. YouTube'dan videoyu bul
    video_info = search_youtube_video(query)
    if not video_info:
        return {"error": "Görünüşe göre bir fırtınaya tutulduk, bağlantı kesildi veya YouTube'da bu ürünün fırtınası henüz kopmamış."}
        
    # 3. Yorumları çek
    comments = fetch_youtube_comments(video_info['video_id'])
    if not comments:
        return {"error": "Bu ürün hakkında henüz yapay zekayı besleyecek kadar yorum bulunmuyor. Erken erişimde misin?"}
        
    # 4. Gemini Analizi
    analysis_data = analyze_comments_with_gemini(comments, query)
    if not analysis_data:
        return {"error": "Gemini şu an biraz yorgun, yapay zeka analiz motoru cevap vermedi. Birazdan tekrar dene."}
        
    # 5. Veritabanına Kaydetme İşlemleri
    urun, _ = Urun.objects.get_or_create(
        model_adi=query,
        defaults={'marka': marka, 'kategori': kategori}
    )
    
    harita, _ = UrunPlatformHaritasi.objects.get_or_create(
        urun=urun,
        platform=platform,
        defaults={
            'platform_urun_url': video_info['url'],
            'platform_urun_id': video_info['video_id']
        }
    )
    
    # Eski yorumları temizleyip yenilerini ekleyelim
    Yorum.objects.filter(harita=harita).delete()
    yorumlar_to_create = []
    for c in comments:
        # Tarih formatı: '2023-11-20T12:00:00Z' -> '2023-11-20'
        yorumlar_to_create.append(
            Yorum(
                harita=harita,
                yorum_metni=c['text'][:1000], # max_length güvenlik önlemi
                yorum_tarihi=c['published_at'][:10]
            )
        )
    if yorumlar_to_create:
        Yorum.objects.bulk_create(yorumlar_to_create)
        
    AiUrunOzeti.objects.update_or_create(
        urun=urun,
        defaults={
            'genel_ozet_metni': analysis_data.get('ozet', ''),
            'genel_duygu_ortalamasi': analysis_data.get('genel_skor', 0)
        }
    )
    
    UrunAnalizDetayi.objects.filter(urun=urun).delete()
    detaylar_to_create = []
    for analiz in analysis_data.get('analizler', []):
        detaylar_to_create.append(
            UrunAnalizDetayi(
                urun=urun,
                analiz_konusu=analiz.get('konu', ''),
                konu_puani=analiz.get('puan', 0),
                konu_ozeti=analiz.get('ozet', '')
            )
        )
    if detaylar_to_create:
        UrunAnalizDetayi.objects.bulk_create(detaylar_to_create)
        
    return {
        "success": True,
        "product_name": urun.model_adi,
        "video_url": video_info['url'],
        "product_image_url": get_product_image(query),
        "analysis": analysis_data,
        "comment_count": len(comments)
    }
