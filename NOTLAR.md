# Enes ile çalışma notları

Yeni bir Claude oturumu bu dosyayı okuyarak kaldığımız yerden devam edebilir.

## Enes hakkında
- Enes Arabacı, 32 yaşında, Kastamonu / Taşköprü'de yaşıyor.
- 2017'den beri **Arabacı Reklam** işletmesini yürütüyor: reklam, dijital baskı, araç kaplama, cam filmi, plotter kesim, cam yazıları.
- Instagram: arabacireklam · Telefon: 0534 080 26 79
- Yeni bir **Bambu Lab X2D + AMS Pro 2** 3D yazıcısı var. 3D çizim bilmiyor, modelleri Claude kodla hazırlıyor.
- Hedefi: internetten, kargoyla uğraşmadan, olabildiğince pasif gelir.
- Türkçe, sade ve dürüst anlatım tercih ediyor.

## Şimdiye kadar yapılanlar (bu repoda)
- `haber-videolari/`: Kastamonu sarı kod haber videosu ve Bambu Lab H3C tanıtım videosu (PIL + ffmpeg, müzik `muzik.py` ile koddan üretiliyor).
- `instagram/oto-cam-filmi/`: Logolu 10 görsellik oto cam filmi Instagram gönderisi (`carousel.py`).
- `instagram/logo-arabaci-reklam.png`: İşletme logosu.
- `3d-modeller/anahtarlik/`: Logolu çok renkli anahtarlık modelleri (3MF + STL, `anahtarlik.py`).

## Konuşulan gelir fikirleri ve durum
- **Önerilen ana yol:** 3D baskı YouTube kanalı + STL dosyası satışı (Cults3D, Etsy; MakerWorld ücretsiz vitrin).
- **STL nişi önerisi:** Kutu oyunu düzenleyicileri (board game insert). Sonraki adım: popüler ve düzenleyicisi az olan 3 oyunu araştırmak.
- Fiziksel ürünü yurt dışına satmak, kargo ve ABD/AB gümrük kuralları (2026'da DDP zorunluluğu, AB 3 € vergi) yüzünden şimdilik rafa kalktı.
- Çocuk animasyon kanalı: yapay zekâ çocuk içeriği 2026'da yoğun denetim altında, önerilmedi.
- Enes'in eski bir Etsy hesabı var (durumu kontrol edilecek).

## Ortam ayarları (Enes yapıyor)
- ElevenLabs API anahtarı ortam değişkeni olarak eklenecek: `ELEVENLABS_API_KEY`
- Allowed domains'e eklenecekler: `api.elevenlabs.io`, yerel haber siteleri, Etsy, Cults3D, MakerWorld, Printables, `huggingface.co`.
- Ayarlar yapıldıktan sonra ilk iş: 3–4 Türkçe ses örneği hazırlayıp Enes'e seçtirmek.
