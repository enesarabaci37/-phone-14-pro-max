# Ders Bahçesi

2. sınıf öğrencisi için tek dosyalık eğitim uygulaması (MEB Türkiye Yüzyılı Maarif Modeli). iPad Safari için tasarlandı; telefonda da çalışır.

**Dersler**
- **Matematik** (15 konu): şekiller ve cisimler, onluk-birlik blokları, ritmik sayma (yüzlük tablo), sayı doğrusu ve karşılaştırma, eldeli toplama, onluk bozarak çıkarma, çarpma (gruplarla), bölme, bütün-yarım-çeyrek, paralar (kasaya ödeme), saat kurma (parmakla), ölçme ve zaman, simetri, robot kodlama, grafik okuma
- **Türkçe** (8 konu): okuma-anlama hikâyeleri, zıt anlamlılar, olay sıralama, cümle kurma, büyük harf, noktalama, kısaltmalar, sözcük anlamı
- **Hayat Bilgisi** (8 konu): trafik işaretleri, mevsimler ve hava, sağlıklı yaşam, güvenlik ve internet, ailem ve nezaket, ülkem ve Atatürk, doğa ve çevre, bilim-teknoloji-sanat
- **İngilizce** (6 konu): sesli kelime kartları, dinle ve seç, resim-kelime, renkler, sayılar, selamlaşma ve günler
- **Akıl Bahçesi** (5 zeka oyunu): hafıza kartları, sıradaki ne, meyve sudoku, kaydır diz, renk sırası

**Özellikler**
- Sesli okuma (Türkçe ve İngilizce). 🗣️ düğmesi otomatik okumayı açar/kapatır, 🔊 düğmeleri tekrar okutur.
- Yanlışta önce ipucu, ikinci yanlışta açıklamalı doğru cevap. Zorlanılan sorular sonra tekrar gelir.
- Her konuda seviyeler ve 1-3 yıldız; günlük hedef (3 etkinlik); 15 dakika sonra mola önerisi.
- Veli bölümü (basit bir çarpma ile korunur): konu bazında doğru/yanlış ve tekrar edilecek sorular.
- Hiçbir kişisel bilgi yok. İlerleme yalnızca cihazda (`localStorage`) tutulur.

**Dosyalar**
- `ders-bahcesi.html`: Claude Artifact sürümü (kaynak dosya).
- `index.html`: GitHub Pages için bağımsız sürüm. `python3 tools/build_index.py` ile kaynak dosyadan üretilir.
- `apple-touch-icon.png`: iPad "Ana Ekrana Ekle" ikonu.
- `akil-bahcesi.html`: 1. aşamanın eski hâli (oyunları artık Ders Bahçesi'nin içinde).
