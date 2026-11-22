# Pro Video – Lightroom Video Presetleri (Normal Çekim)

**Normal / Standart renk profiliyle** (Log değil) çekilmiş 4K videolar için 22 preset.
DJI Mini 5 Pro · DJI Osmo Pocket 3 · Insta360 X5

Tüm DNG'lerin üzerinde preset adı yazılıdır. Her kamera için ayrı ayarlanmıştır: kameranın kendi renk karakteri (DJI'ın doygun rengi, Pocket 3'ün sert keskinliği, X5'in düz görüntüsü) önce düzeltilir, mevsim görünümü onun üstüne eklenir.

## Dosyalar
- `Pro-Video-Presets-DNG.zip` → 22 DNG (Lightroom Mobile ücretsiz sürüm dahil, klasik yöntem)
- `Pro-Video-Gece-DNG.zip` → 18 gece preseti
- `Pro-Video-Presets-XMP.zip` → 40 presetin hepsi, tek seferde içe aktarma için

## 📱 DNG ile kurulum (iPhone)
1. `Pro-Video-Presets-DNG.zip`'i Dosyalar uygulamasına kaydet ve üstüne dokunarak aç.
2. Lightroom → **+** → **Dosyalardan** → 22 DNG'yi seç ve içe aktar.
3. Bir DNG'yi aç → sağ üst **⋯** → **Ön Ayar Oluştur**
   - Ad: dosya adıyla aynı (ör. `M5P 03 Yaz`)
   - Grup: ör. `Pro Video - Mini 5 Pro`
   - Tüm kutular işaretli kalsın → ✓
4. Her DNG için tekrarla. Sonra videoyu aç → **Ön Ayarlar** → presetini seç.

Hızlı yol: DNG'de **⋯ → Ayarları Kopyala**, videoda **⋯ → Ayarları Yapıştır**.

**XMP ile (daha hızlı):** Videoyu aç → Ön Ayarlar → **⋯ → Ön Ayarları İçe Aktar** → `Pro-Video-Presets-XMP.zip`. 22 preset tek seferde gruplarıyla gelir.

## 🎬 Presetler (her kamera için 6 adet)

| # | Preset | Görünüm | En iyi sahne |
|---|---|---|---|
| 01 | **Clean Natural** | Temiz, doğal, net | Her çekim, güvenli başlangıç |
| 02 | **İlkbahar** | Taze yeşil, çiçek tonları, parlak-pastel | Park, doğa, çiçek, bahçe |
| 03 | **Yaz** | Turkuaz deniz, derin mavi gök, sıcak ten | Plaj, tekne, havuz, şehir gündüz |
| 04 | **Sonbahar** | Altın yaprak, turuncu-kahve, sıcak & derin | Orman, bağ, yaprak dökümü |
| 05 | **Kış** | Bembeyaz kar, soğuk ve kristal net | Kar, dağ, kayak, sisli sabah |
| 06 | **Golden Hour** | Sıcak, ışıltılı, sinematik | Gün batımı / doğumu |

Ön ekler: `M5P` = Mini 5 Pro · `OP3` = Osmo Pocket 3 · `X5` = Insta360 X5

**Her kamerada çalışan (UNI):** Cinematic Teal Orange · Gece Şehir · Moody Dark · Siyah Beyaz Sinema

## 🌃 Gece Seti (`Pro-Video-Gece-DNG.zip`)
Her kamera için 6 gece preseti (toplam 18). DNG'lerin üstünde preset adı yazılıdır.

| Preset | Görünüm | En iyi sahne |
|---|---|---|
| **Gece 01 Doğal** | Temiz siyah, kontrollü lambalar, gerçekçi | Her gece çekimi |
| **Gece 02 Altın Şehir** | Altın sokaklar + derin mavi gök | Drone ile şehir, köprü, otoyol |
| **Gece 03 Mavi Saat** | Koyu mavi gök + sıcak ışıklar | Gün batımından 20-40 dk sonra |
| **Gece 04 Neon Şehir** | Mor-pembe-camgöbeği neon, modern | Cadde, AVM, tabelalar, yağmurlu gece |
| **Gece 05 Sinematik** | Teal gölgeler, film havası | Sokak, araba, hikaye anlatımı |
| **Gece 06 Beyaz Işık** | Turuncu sokak lambası rengini temizler | Turuncu lambalı sokaklar |

**Gece çekim ipuçları (normal profil):**
- ISO'yu olabildiğince düşük tut: Mini 5 Pro ≤ 1600, Pocket 3 ≤ 3200, X5 ≤ 800 (X5 gecede gürültülü).
- Pozlamayı **ışıklara göre** ayarla (-0.7 EV). Patlayan ışık geri gelmez, karanlık biraz açılabilir.
- 4K **30fps** gece için daha temizdir (60fps'te ışık yarıya iner). Hareketli çekimde 60 kullan.
- Beyaz denge: 4000-4500K sabit. Turuncu lambalar fazlaysa "Gece 06 Beyaz Işık".
- Lightroom videoda gürültü azaltma yok; bu yüzden presetler gölgeleri fazla açmaz.

## 🎥 Bu presetler için önerilen çekim ayarları
| | Mini 5 Pro | Osmo Pocket 3 | Insta360 X5 |
|---|---|---|---|
| Renk profili | **Normal** (8-bit veya 10-bit) | **Normal** | **Standard** (Vivid değil) |
| Çözünürlük | 4K 60fps | 4K 60fps | 8K 30 / 5.7K 60 |
| Enstantane | 1/120 (ND filtre ile) | 1/120 (ND ile) veya otomatik | Otomatik |
| Beyaz denge | Manuel 5500K (gün ışığı) | Manuel 5500K | Manuel / sabit |
| Keskinlik | 0 veya -1 | -1 | Düşük |
| Pozlama | Gökyüzü patlamasın, -0.3 EV | Yüze göre | -0.3 EV |

Beyaz dengeyi **sabit** çekmek, presetlerin klipten klibe aynı görünmesini sağlayan en önemli adımdır.

## ✨ Profesyonel sonuç için ince ayar
1. Preseti uygula → üstteki kaydırıcıyla **şiddeti %60–100** arası ayarla.
2. Sadece **Pozlama** ve **Sıcaklık** ile sahneye uydur (genelde ±0.3 EV, ±5 sıcaklık yeter).
3. Aynı sahnedeki tüm klipleri tek tek yapmak yerine birinde ayarla → **Ayarları Kopyala/Yapıştır**.
4. Dışa aktarırken: 4K, en yüksek kalite.

Not: Lightroom video düzenlemede maske, keskinlik ve gürültü azaltma yok; presetler yalnızca videoda çalışan ayarları kullanır. Beyaz denge değeri presetlere konmadı (her çekimde farklı olduğu için); mevsim sıcaklığı renk derecelendirmesiyle verilir.

## 🔧 Düzenleme
`generate_presets.py` içinde kamera düzeltmeleri (`CAMERAS`) ve görünümler (`LOOKS`) ayrı tanımlıdır. Değiştirip `python3 generate_presets.py . && python3 generate_dng.py .` çalıştır.
