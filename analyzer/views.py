import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import process_product_analysis

@csrf_exempt
def analyze_product(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            query = data.get('query')
            
            if not query:
                return JsonResponse({'error': 'Lütfen aranacak bir ürün adı girin.'}, status=400)
                
            result = process_product_analysis(query)
            
            if result.get('error'):
                return JsonResponse(result, status=400)
                
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Geçersiz veri formatı.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
            
    return JsonResponse({'error': 'Sadece POST istekleri kabul edilir.'}, status=405)
