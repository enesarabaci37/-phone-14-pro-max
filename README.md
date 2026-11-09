# ✨ VektörSihirbazı

Bitmap görselleri (PNG, JPG, GIF, WebP…) **tam otomatik** olarak temiz vektör çiziminde
(SVG, PDF, EPS) yeniden oluşturan, Vector Magic tarzı bir dönüştürücü.
Tamamen tarayıcıda çalışır: görseller hiçbir sunucuya yüklenmez. iPhone'da da çalışır.

## Kullanım

**Tarayıcı:** `index.html` dosyasını bir web sunucusundan açın, görseli sürükleyip bırakın
(veya dokunup seçin / yapıştırın), sonra SVG / PDF / EPS / PNG olarak indirin.

```bash
python3 -m http.server 8000
```

Ardından tarayıcıda `http://localhost:8000` adresini açın. GitHub Pages açılırsa
(Settings → Pages → `main` dalı) telefondan doğrudan bağlantıyla da kullanılabilir.

**Komut satırı (PNG):**

```bash
node cli.js logo.png -o logo.svg
```

```bash
node cli.js logo.png -o logo.pdf --mode bw --tolerance 0.4
```

## Nasıl çalışır (Vector Magic'e benzer yaklaşım)

| Aşama | Ne yapar |
|---|---|
| Alt-piksel büyütme | Küçük görseller 2–4× büyütülür; anti-aliasing'deki ara tonlar sayesinde kenarlar piksel ızgarasına değil **gerçek konumlarına** oturur. |
| Akıllı palet | Renkler Lab uzayında, yalnızca düz (kenar olmayan) alanlardan örneklenerek bulunur; kenar karışımları sahte renk üretmez. Renk sayısı otomatik bulunur. |
| Kenar karışımı düzeltme | İki renk arasındaki anti-aliasing pikselleri, üçüncü bir renge (ör. siyah–beyaz arasında gri) yanlışlıkla atanmaz. |
| İnce detay koruma | 1 px çizgiler ve küçük yazılar basit %50 eşiğinde kaybolmaz. |
| Leke temizleme | Belirlenen alandan küçük bölgeler en uzun sınırı paylaştığı komşuya katılır. |
| Paylaşılan kenarlar | İki bölgeyi ayıran her sınır yalnızca **bir kez** eğriye çevrilir; şekiller arasında boşluk veya üst üste binme olmaz. |
| Köşe tespiti + keskinleştirme | Köşeler yumuşatılmış sınırda bulunur; yuvarlanmış köşeler iki kenar doğrusunun kesişimine taşınır. |
| Eğri uydurma | Merdiven basamakları koşu-ortası noktalarına indirgenir, yumuşatılır; düz kısımlar çizgi, kalanlar Schneider algoritmasıyla kübik Bezier olur. |

## Ayarlar

- **Görsel türü:** Logo/Çizim (varsayılan), Fotoğraf (çok renk, posterize), Siyah-Beyaz (Otsu eşiği).
- **Renkler:** otomatik veya sabit sayı; paletteki bir renge dokunup değiştirin, × ile kaldırıp yeniden işleyin.
- **Detay / Eğri toleransı / Köşe hassasiyeti / Yumuşatma** kaydırıcıları.
- **Görünüm:** Karşılaştır (kaydırıcılı), Vektör, Orijinal, Çizgiler; fare tekerleği / iki parmakla yakınlaştırma.

## Dosyalar

- `vectorizer.js` – dönüştürme motoru (tarayıcı, Web Worker ve Node.js'te çalışır, bağımlılık yok)
- `index.html`, `app.js` – arayüz
- `cli.js` – komut satırı aracı
