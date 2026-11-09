# ✨ VektörSihirbazı

Bitmap görselleri (PNG, JPG, GIF, WebP…) **tam otomatik** olarak temiz vektör çiziminde
(SVG, PDF, EPS) yeniden oluşturan, Vector Magic tarzı bir dönüştürücü.
Tamamen tarayıcıda çalışır: görseller hiçbir sunucuya yüklenmez. iPhone'da da çalışır.

## Kullanım (bilgisayar)

1. **`VektorSihirbazi.html`** dosyasını indirin.
2. Çift tıklayın; Chrome, Edge veya Firefox'ta açılır. Kurulum ve internet gerekmez.
3. JPG/PNG görseli pencereye sürükleyin (ya da **Görsel aç** düğmesine basın veya Ctrl+V ile yapıştırın).
4. **İndir** bölümünden SVG, PDF, EPS veya PNG olarak kaydedin.

Logo, çizim ve ikon için **Logo / Çizim** türü en iyi sonucu verir. Fotoğraflar için
**Fotoğraf** türünü seçin; fotoğraflar az renkli, afiş tarzı bir vektöre dönüşür.

**Komut satırı (yalnızca PNG):**

```bash
node cli.js logo.png -o logo.svg
```

Kaynak dosyalar değiştirilirse tek dosya sürümü yeniden üretilir:

```bash
python3 build.py
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
- `VektorSihirbazi.html` – her şey tek dosyada (çift tıklayıp kullanın)
- `index.html`, `app.js` – arayüz kaynakları
- `build.py` – tek dosya sürümünü üretir
- `cli.js` – komut satırı aracı
