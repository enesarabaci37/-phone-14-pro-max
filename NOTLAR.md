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
- ElevenLabs ücretli olduğu için vazgeçildi. Seslendirme için **Azure Speech (Free F0)** kuruldu.
  - Kaynak: `enes-ses-servisi`, kaynak grubu `enes-ses`, bölge **North Europe** (West Europe yeni müşteri almıyordu).
  - Ortam değişkenleri: `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION=northeurope`
  - Erişim adresi: `northeurope.tts.speech.microsoft.com`
- İsteğe bağlı: `PEXELS_API_KEY` (stok video).
- Ağ erişimi geniş seviyeye çevrilecek ya da gerekli siteler Allowed domains'e eklenecek.
- Anahtarları asla ekrana yazdırma; sadece var olup olmadıklarını ve çalıştıklarını kontrol et.
- Ayarlar yapıldıktan sonra ilk iş: 3–4 Türkçe ses örneği hazırlayıp Enes'e seçtirmek.

## Bağlayıcılar (bağlandı ve test edildi, 4 Kasım 2026)
- **Google Drive, Google Sheets, Canva** bağlı ve çalışıyor (Drive hesabı: arabacienes0@gmail.com).
- Drive'da sadece şu klasörle çalış, Enes'in diğer dosyalarına bakma:
  - `Arabacı Reklam - Claude` (id: `1R31ZVvUQWrOfuxQDUtq276jh-osCWn5X`)
    - `Ham Çekimler` (id: `1RUpWKblJ9iq_Y4--KQqeprfu_1AkteWi`) Enes'in yüklediği videolar ve fotoğraflar
    - `Instagram` (id: `1GnWRu15IF6fwJn2LucH40YdldyjkjhBl`)
    - `YouTube` (id: `1VTXDydq0iamQD4Met453H1ImCSc7fWCz`)
    - `3D Modeller` (id: `1R3pSws9MsYxAU6H8lskDXDS0NPsZcrnW`)
- Canva'da **ARABACI REKLAM** marka kiti var (id: `kAFsNPNzV8c`). Diğer marka kitleri Enes'in müşterilerine ait, izinsiz kullanma.
- Canva akışı: tasarımı Claude yapar → Canva'ya aktarır → küçük düzenlemeleri Enes yapar.
