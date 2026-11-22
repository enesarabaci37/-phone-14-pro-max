# Video Pro – Lightroom Video Presetleri

DJI Mini 5 Pro, DJI Osmo Pocket 3 ve Insta360 X5 için 16 video preseti. **Lightroom Mobile** (iPhone/Android) ve Lightroom Desktop ile çalışır.

## 📱 Lightroom Mobile'a yükleme (iPhone)
1. `Video-Pro-Presets.zip` dosyasını iPhone'a indir (Dosyalar uygulamasına kaydet).
2. Lightroom'da herhangi bir videoyu aç, alttan **Ön Ayarlar (Presets)** sekmesine gir.
3. Sağ üstteki **⋯** menüsü → **Ön Ayarları İçe Aktar (Import Presets)**.
4. ZIP dosyasını seç. Presetler şu gruplarda görünür:
   - `Video Pro - DJI Mini 5 Pro`
   - `Video Pro - DJI Osmo Pocket 3`
   - `Video Pro - Insta360 X5`
   - `Video Pro - Universal`

> Desktop'ta: Geliştir (Edit) → Ön Ayarlar paneli → **+** → Ön Ayarları İçe Aktar → ZIP'i seç. Adobe hesabın açıksa mobilde de otomatik senkronize olur.

## 🎬 Preset listesi

| Kamera | Preset | Ne zaman? | Çekim profili |
|---|---|---|---|
| Mini 5 Pro | M5P 01 – D-Log M Natural | Her şeyin temeli, doğal renk | D-Log M |
| Mini 5 Pro | M5P 02 – Cinematic Teal Orange | Sinematik hava çekimi | D-Log M |
| Mini 5 Pro | M5P 03 – Golden Hour | Gün batımı / doğumu | D-Log M |
| Mini 5 Pro | M5P 04 – Epic Landscape | Dağ, deniz, şehir panoraması | D-Log M |
| Mini 5 Pro | M5P 05 – Normal Profile Punch | Normal profilde çekilmiş video | Normal |
| Pocket 3 | OP3 01 – D-Log M Natural | Doğal, ten renklerini koruyan | D-Log M |
| Pocket 3 | OP3 02 – Vlog Warm Skin | Yüz/vlog çekimleri | D-Log M |
| Pocket 3 | OP3 03 – Moody Film | Sokak, gece, karamsar hava | Normal / HLG |
| Pocket 3 | OP3 04 – Clean Travel | Seyahat vlogu | D-Log M |
| X5 | X5 01 – I-Log Natural | 360/reframe temel düzeltme | I-Log |
| X5 | X5 02 – Action Vivid | Motor, kayak, bisiklet, su | I-Log |
| X5 | X5 03 – Standard Clean Bright | Standart/Vivid profilde çekim | Standart |
| X5 | X5 04 – Snow & Sky | Kar, gökyüzü, deniz | I-Log |
| Hepsi | UNI 01 – Night City | Gece şehir, neon | Normal |
| Hepsi | UNI 02 – Faded Film | Retro/analog his | Normal |
| Hepsi | UNI 03 – B&W Cinema | Sinematik siyah-beyaz | Hepsi |

## ⚙️ Önemli notlar
- **Log presetleri (D-Log M / I-Log) sadece Log ile çekilmiş videolarda doğru görünür.** Normal çekilmiş videoya uygularsan aşırı kontrastlı olur → onun yerine “Normal/Standard” presetlerini kullan.
- Presetler **Miktar (Amount)** kaydırıcısını destekler: Mobilde preseti seçtikten sonra üstteki kaydırıcıyla %0–200 arası şiddet ayarlayabilirsin.
- Her sahnenin ışığı farklıdır. Preset sonrası genelde yalnızca **Pozlama** ve **Sıcaklık** ile ince ayar yeter.
- Lightroom video düzenlemede maske, detay (keskinlik/gürültü) ve optik ayarları desteklenmez; presetler yalnızca videoda çalışan ayarları kullanır (Işık, Ton Eğrisi, Renk, Renk Karışımı, Renk Derecelendirme, Efektler).
- Log → Rec.709 dönüşümü ton eğrisi ile yapılan bir yaklaşımdır, resmi DJI/Insta360 LUT'u değildir. En iyi sonuç için doğru pozlanmış (histogram sağa yakın, patlamamış) çekim yap.

## 🎥 Önerilen çekim ayarları
- **Mini 5 Pro:** D-Log M, 10-bit, ISO mümkün olduğunca düşük, enstantane ≈ 2× FPS (ND filtre ile), pozlamayı +0.3/+0.7 EV.
- **Pocket 3:** D-Log M, 10-bit, Beyaz dengesi manuel (gün ışığı 5600K), yüz pozlaması için +0.3 EV.
- **Insta360 X5:** I-Log, 8K/30 veya 5.7K/60, beyaz dengesi sabit; reframe işlemini Insta360 uygulamasında yapıp dışa aktardıktan sonra Lightroom'da preset uygula.

## 🔧 Değiştirme
`generate_presets.py` içindeki değerleri düzenleyip `python3 generate_presets.py .` çalıştırarak presetleri yeniden üretebilirsin.
