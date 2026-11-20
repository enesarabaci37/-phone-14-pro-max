# StitchAnatolia: yeni oturum devir notu

Yeni oturumda Claude'a ilk mesaj olarak şunu yaz:
> "claude/epic-curie-gddtn0 dalını çek, DEVAM_STITCHANATOLIA.md dosyasını oku, StitchAnatolia'ya oradan devam edelim."

## Kullanıcı
- Taşköprü, Kastamonu. Türkçe konuşur, samimi ("kanka").
- Tüm işi Claude yapar: tasarım, PDF, görsel, video, metin, takvim. Kullanıcı sadece yükler ve paylaşır.
- Talimatlar **sohbette, adım adım, alan alan** verilir. Örnek: "Title kutusuna şunu yaz, Tags kısmına şunları ekle".
- Tasarım profesyonel ve temiz olmalı, "yapay zeka yapmış" gibi durmamalı.
- Dosyalar zip olarak paketlenir. Metin dosyaları **.txt (UTF-8 BOM + CRLF)** olmalı. .md, kullanıcının Windows görüntüleyicisinde bozuk görünüyor.

## İş modeli
Etsy'de dijital ürün mağazası **StitchAnatolia** (stitchanatolia.etsy.com). Türk kilim motifli kanaviçe (cross stitch) PDF desenleri satılıyor. Trafik Pinterest ve Instagram @stitchanatolia üzerinden geliyor.

## Yayındaki 6 ürün
| # | Ürün | Boyut | SKU |
|---|------|-------|-----|
| 1 | Nazar Madalyonu | 71×91 | SA-001 |
| 2 | Hayat Ağacı (Tree of Life) | 61×85 | SA-002 |
| 3 | Elibelinde | 57×89 | SA-003 |
| 4 | Bereket (kare yastık) | 71×71 | SA-004 |
| 5 | Mini Nazar Seti (4 mini desen) | 53×53 | SA-005 |
| 6 | Kilim Koleksiyonu: 5'li paket (27 sayfalık PDF) | – | – |

- Her ürünün videosu var.
- Mağazanın bölümleri, öne çıkan ürünleri, logosu, kapağı, makbuz şeridi, duyurusu ve hakkında yazısı tamam.
- Ayarlar: Share & Save açıklandı, "With an AI generator" beyanı yapıldı.
- Kategori: "A supply or tool to make things".
- Mother's Day, "Occasion" altında değil, **"Holiday"** altında.

Tüm bitmiş dosyalar `StitchAnatolia_TUM_DOSYALAR/` klasöründe. Her ürünün PDF'i, Etsy görselleri, Pinterest görselleri ve URUN_BILGILERI.txt dosyası orada.

## Pinterest
- İşletme hesabı açıldı. Kişisel hesap dönüştürülmedi; "Ücretsiz işletme hesabı oluştur" yolu kullanıldı.
- Profil ve kapak hazır, **6 pin yayında**.
- Panolar:
  - Turkish Kilim Cross Stitch Patterns
  - Evil Eye Cross Stitch
  - Boho Cross Stitch Ideas
  - Anatolian Symbols & Meanings
- Kurallar:
  - Pin başlığı en fazla 100 karakter. Etsy başlığı Pinterest'e uzun gelir, kısa başlık kullanılır.
  - Pin 1000x1500, kapak 1920x1080.
  - "Yapay zeka ile değiştirildi" seçeneği AÇIK olmalı.
  - ✏️ kalem editörüne ASLA basılmaz, görseli kırpıyor.
  - Etsy'yi Pinterest'te sahiplenme (claim) özelliği Türkiye'de yok.
- **Günlük pin takvimi:** her akşam 2 pin, saat 21:00–01:00 arası. Kullanıcı "bugünün pinlerini söyle" der, Claude başlık, açıklama, pano ve link alanlarını verir. Kalan sıra:
  1. Motiflerin anlamı (pin_meanings) + Nazar videosu
  2. Koleksiyon pini + Hayat Ağacı videosu
  3. Nazar b + Mini Nazar videosu
  4. Hayat Ağacı b + Elibelinde b
  5. Bereket b + Elibelinde videosu
  6. Mini Nazar b + Bereket videosu
  7. Paket videosu

## Instagram @stitchanatolia
- Profil hazır.
  - Ad: "StitchAnatolia • Kilim Cross Stitch"
  - Biyografi: 4 satır
  - Link: stitchanatolia.etsy.com
  - Profesyonel hesap
- **0 gönderi.** 3. haftada ilk 9 gönderi tek seferde hazırlanıp paylaşılacak.
- 2FA açılmalı. Pinterest için de aynısı geçerli.

## Teknik akış (`stitchanatolia_kaynak/`)
- `designs.py`: desen üreticileri (`G` sınıfı: put, mirx, stamp, diamond, frame). Çıktı `designs/<slug>/pattern.js` dosyalarına, toplu hali `all_patterns.js`'e yazılır.
- `pattern2.html#slug` ve `render_all.js`: 5 sayfalık A4 PDF (kapak, motifler ve DMC anahtarı, renkli şema, siyah-beyaz şema, rehber).
- `listing2.html`: Etsy görselleri (2000x1600).
- `video.html` ve `render_video.js`: 12 saniyelik video (1080x1080, ffmpeg libx264).
- `pins.html` ve `render_pins.js`: Pinterest pinleri.
- `bundle.html` ve `render_bundle.js`: paket ürün.
- `listings.py`: ilan metinleri. Başlık en fazla 140 karakter; 13 etiket, her biri en fazla 20 karakter.
- Yazı tipleri: Cormorant Garamond + Inter; şema sembolleri DejaVu Sans. Çizim Playwright Chromium ile yapılır.
- **DMC paleti:**

| Kod | DMC | Renk |
|-----|-----|------|
| RD | 347 | #B8312F |
| NV | 311 | #1F3B5C |
| GD | 729 | #CFA14A |
| CR | 712 | #F3EBD3 |
| BR | 938 | #3A2214 |
| TQ | 3809 | #3A7C82 |
| GN | 3363 | #5E7A4E |
| RB | 820 | #123A8C |
| LB | 3846 | #2EC1D6 |
| WH | Blanc | #FFFFFF |
| BK | 310 | #111111 |

## Son durum
İlk 7 günde 5 görüntülenme, 1 ziyaret, 0 sipariş. Bu normal; mağaza yeni ve ürün sayısı az.

## Sıradaki işler
1. **ŞİMDİ, 1. hafta:** 3 yeni desen, SKU'ları SA-006, SA-007, SA-008.
   - 🧿 Göz Seti
   - 🐺 Kurt İzi (Kurt Ağzı)
   - ⭐ Yıldız

   Her biri için hazırlanacaklar: PDF, Etsy görselleri, video, Pinterest pini, ilan metni (.txt) ve sohbette adım adım yükleme talimatı.
2. Her akşam 2 pin (yukarıdaki takvime göre).
3. 2. hafta: 2 Noel deseni + 2 kilim deseni.
4. 3. hafta: Instagram'ın ilk 9 gönderisi ve haftalık paket.
5. 4. hafta: Google Sheets takip tablosu, 2. paket ürün, genel değerlendirme.
6. 2. ay:
   - Etsy ilanlarının Almanca ve Fransızca çevirileri.
   - 20'den fazla ürün olunca Etsy API ile otomasyon.
7. Her pazar Etsy istatistikleri incelenir.
