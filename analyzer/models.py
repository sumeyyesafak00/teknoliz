from django.db import models

class Kategori(models.Model):
    kategori_id = models.AutoField(primary_key=True, db_column='kategori_id')
    kategori_adi = models.CharField(max_length=255, db_column='kategori_adi')

    class Meta:
        db_table = 'KATEGORILER'

    def __str__(self):
        return self.kategori_adi

class Marka(models.Model):
    marka_id = models.AutoField(primary_key=True, db_column='marka_id')
    marka_adi = models.CharField(max_length=255, db_column='marka_adi')

    class Meta:
        db_table = 'MARKALAR'

    def __str__(self):
        return self.marka_adi

class Platform(models.Model):
    platform_id = models.AutoField(primary_key=True, db_column='platform_id')
    platform_adi = models.CharField(max_length=100, db_column='platform_adi')
    base_url = models.CharField(max_length=500, db_column='base_url', blank=True, null=True)

    class Meta:
        db_table = 'PLATFORMLAR'

    def __str__(self):
        return self.platform_adi

class Urun(models.Model):
    urun_id = models.AutoField(primary_key=True, db_column='urun_id')
    marka = models.ForeignKey(Marka, on_delete=models.CASCADE, db_column='marka_id')
    kategori = models.ForeignKey(Kategori, on_delete=models.CASCADE, db_column='kategori_id')
    model_adi = models.CharField(max_length=255, db_column='model_adi')
    model_kodu = models.CharField(max_length=100, db_column='model_kodu', blank=True, null=True)

    class Meta:
        db_table = 'URUNLER'

    def __str__(self):
        return f"{self.marka.marka_adi} {self.model_adi}"

class UrunPlatformHaritasi(models.Model):
    harita_id = models.AutoField(primary_key=True, db_column='harita_id')
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE, db_column='urun_id')
    platform = models.ForeignKey(Platform, on_delete=models.CASCADE, db_column='platform_id')
    platform_urun_url = models.TextField(db_column='platform_urun_url', blank=True, null=True)
    platform_urun_id = models.CharField(max_length=100, db_column='platform_urun_id', blank=True, null=True)

    class Meta:
        db_table = 'URUN_PLATFORM_HARITASI'

    def __str__(self):
        return f"{self.urun.model_adi} - {self.platform.platform_adi}"

class AiUrunOzeti(models.Model):
    ozet_id = models.AutoField(primary_key=True, db_column='ozet_id')
    urun = models.OneToOneField(Urun, on_delete=models.CASCADE, db_column='urun_id')
    genel_ozet_metni = models.TextField(db_column='genel_ozet_metni', blank=True, null=True)
    genel_duygu_ortalamasi = models.FloatField(db_column='genel_duygu_ortalamasi', blank=True, null=True)
    son_guncelleme_tarihi = models.DateField(auto_now=True, db_column='son_guncelleme_tarihi')

    class Meta:
        db_table = 'AI_URUN_OZETLERI'

    def __str__(self):
        return f"Özet: {self.urun.model_adi}"

class UrunAnalizDetayi(models.Model):
    detay_id = models.AutoField(primary_key=True, db_column='detay_id')
    urun = models.ForeignKey(Urun, on_delete=models.CASCADE, db_column='urun_id')
    analiz_konusu = models.CharField(max_length=255, db_column='analiz_konusu', blank=True, null=True)
    konu_puani = models.FloatField(db_column='konu_puani', blank=True, null=True)
    konu_ozeti = models.TextField(db_column='konu_ozeti', blank=True, null=True)

    class Meta:
        db_table = 'URUN_ANALIZ_DETAYLARI'

    def __str__(self):
        return f"{self.urun.model_adi} - {self.analiz_konusu}"

class Yorum(models.Model):
    yorum_id = models.AutoField(primary_key=True, db_column='yorum_id')
    harita = models.ForeignKey(UrunPlatformHaritasi, on_delete=models.CASCADE, db_column='harita_id')
    yorum_metni = models.TextField(db_column='yorum_metni', blank=True, null=True)
    verilen_puan = models.IntegerField(db_column='verilen_puan', blank=True, null=True)
    yorum_tarihi = models.DateField(db_column='yorum_tarihi', blank=True, null=True)
    duygu_skoru = models.FloatField(db_column='duygu_skoru', blank=True, null=True)

    class Meta:
        db_table = 'YORUMLAR'

    def __str__(self):
        return f"Yorum {self.yorum_id} - {self.harita.urun.model_adi}"
