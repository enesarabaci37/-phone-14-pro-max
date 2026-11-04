# Enes ile çalışma notları

Yeni bir Claude oturumu bu dosyayı okuyarak kaldığımız yerden devam edebilir.

## Enes hakkında
- Enes Arabacı, 32 yaşında, Kastamonu / Taşköprü'de yaşıyor.
- 2017'den beri **Arabacı Reklam** işletmesini yürütüyor: reklam, dijital baskı, araç kaplama, cam filmi, plotter kesim, cam yazıları.
- Instagram: arabacireklam · Telefon: 0534 080 26 79
- Yeni bir **Bambu Lab X2D + AMS Pro 2** 3D yazıcısı var. 3D çizim bilmiyor, modelleri Claude kodla hazırlıyor.
- Hedefi: internetten, kargoyla uğraşmadan, olabildiğince pasif gelir.
- Türkçe, sade ve dürüst anlatım tercih ediyor.
- **Adobe Creative Cloud üyeliği var (ücretli):** Photoshop, Premiere Pro, Illustrator, After Effects vb.
  - Adobe bağlayıcısı henüz bağlı değil (claude.ai/customize/connectors > Adobe). Bağlanınca yeni oturumda araçları test et.
  - Bağlayıcısız yol: düzenlenebilir dosya üret (Photoshop/Illustrator/AE için .jsx script, katmanlı PSD, vektör SVG/PDF, Premiere için XML).

## Şimdiye kadar yapılanlar (bu repoda)
- `haber-videolari/`: Kastamonu sarı kod haber videosu ve Bambu Lab H3C tanıtım videosu (PIL + ffmpeg, müzik `muzik.py` ile koddan üretiliyor).
- `instagram/oto-cam-filmi/`: Logolu 10 görsellik oto cam filmi Instagram gönderisi (`carousel.py`).
- `instagram/logo-arabaci-reklam.png`: İşletme logosu.
- `3d-modeller/anahtarlik/`: Logolu çok renkli anahtarlık modelleri (3MF + STL, `anahtarlik.py`).
- `3d-modeller/magnet-taskopru/`: Taşköprü sarımsağı buzdolabı magneti (3 renk, 79x64x6.2 mm, arkada 2x 10x3 mm mıknatıs yuvası, `magnet.py`).
  - Enes beğenmedi ("çok basit"), bu iş rafa kalktı. Ders: düz ekstrüzyon tasarımlar sticker gibi duruyor; 3D işlerde baştan hacim/kabartma ve yerel detay hedefle.
- **kastamonuhaber.com haftalık haber videosu (4 Kasım 2026):** Tek video, 5 haber x ~11 sn, 1080x1920, ~71 sn.
  - Enes'in tercihleri: haberler tek videoda (ayrı ayrı değil), her biri ~10 sn; logo beyaz zemin üstünde OLMASIN (koyu zemin için beyaz+kırmızı logo versiyonu kullanıldı); "Kaynak: İHA/AA" yazmasın; bilgiler kastamonuhaber.com'dan alınsın; arka plan halkası ortalı olsun.
  - Yöntem: HTML/CSS şablon + Playwright ile kare kare render + ffmpeg; seslendirme edge-tts (tr-TR-AhmetNeural, +15%), müzik numpy ile üretildi. Betikler bu oturumun geçici klasöründeydi, repoya alınmadı.
- **Ediz Özcan röportajı (İyilik Var, Cide/Kastamonu) Instagram videosu:** 5 dk ham çekimden 55 sn dikey video (kastamonuhaber için).
  - Enes'in tercihleri: Instagram videoları 45–60 sn, uzun olmasın; isim bandında sadece isim (EDİZ ÖZCAN), unvan yok.
  - Yöntem: Drive paylaşım linkinden `drive.usercontent.google.com/download?id=...&export=download&confirm=t` ile curl (1.5 GB sorunsuz indi) → faster-whisper `large-v3-turbo` ile kelime zamanlı transkript (PyAV uyumsuzluğu yüzünden ses numpy dizisi olarak verilir) → ffmpeg kesim + kesimlerde %12 yakınlaştırma (jump cut gizleme) → Playwright ile şeffaf PNG grafik katmanı (logo, isim bandı, kelime kelime altyazı, kapanış) → ses: afftdn + sidechain müzik + loudnorm −14 LUFS.
  - Uzun ffmpeg işlerini arka planda çalıştır; tpad yerine `color` arka plan + `overlay=eof_action=repeat` kullan (tpad son kareyi uzatmadı).
- **Yeni iş fikri:** Enes'in eşi günlük hayat (vlog) Reels'i paylaşıyor. 10 civarı parça video verilecek; Claude içerikleri anlayıp sıralayacak, kesip hızlandıracak, Reels yapacak. Müzik: telifli trend şarkı eklenmez, eşi Instagram'da seçer. Eşinin tarzı/hesabı sorulacak.
- **Bekleyen:** Instagram (arabacireklam) analizi. Instagram dışarıdan erişimi engelliyor; Enes'ten profil + İstatistikler ekran görüntüleri ya da "Bilgilerini indir" JSON'u istendi.

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

## Canva tasarımları
- **Oto cam filmi kaydırmalı gönderi (10 sayfa, 1080x1350):** Canva tasarım id `DAHZ9qmmB5Y`
  - Düzenleme: https://www.canva.com/d/5AZMksP_aZe5DpK
  - Canva'ya yüklenen logolar: renkli `MAHZ9l7Bu2Q`, beyaz yazılı `MAHZ9jrn9As`. Kapak araç fotoğrafı `MAHZ9nFSnNQ`.
  - Yöntem: `canva/oto-cam-filmi/` içindeki betikler Canva edit-design işlemlerini üretir (önce add_text/insert_shape, sonra format_text). Yazılar Canva'da düzenlenebilir.
