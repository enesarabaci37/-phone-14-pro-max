# Pro Video – Lightroom Video Presetleri (Normal Çekim)

**Normal / Standart renk profiliyle** (Log değil) çekilmiş 4K videolar için 22 preset.
DJI Mini 5 Pro · DJI Osmo Pocket 3 · Insta360 X5

Her kamera için ayrı ayarlanmıştır: kameranın kendi renk karakteri (DJI'ın doygun rengi, Pocket 3'ün sert keskinliği, X5'in düz görüntüsü) önce düzeltilir, mevsim görünümü onun üstüne eklenir.

## Dosyalar
- `Pro-Video-Presets-DNG.zip` → 22 DNG (Lightroom Mobile ücretsiz sürüm dahil, klasik yöntem)
- `Pro-Video-Presets-XMP.zip` → aynı 22 preset, tek seferde içe aktarma için

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
