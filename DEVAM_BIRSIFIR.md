# Birsıfır Teknoloji: yeni oturum devir notu

Yeni oturumda Claude'a ilk mesaj olarak şunu yaz:
> "DEVAM_BIRSIFIR.md dosyasını oku, Birsıfır Teknoloji Instagram hesabına oradan devam edelim."

## Kullanıcı
- Taşköprü, Kastamonu. Türkçe konuşur, samimi ("kanka").
- Tüm işi Claude yapar (plan, metin, görsel, takvim). Kullanıcı sadece paylaşır.
- Talimatlar sohbette, adım adım, alan alan verilir.
- Tasarım profesyonel ve temiz olmalı, "yapay zeka yapmış" gibi durmamalı.
- Dosyalar zip olarak paketlenir. Metin dosyaları .txt (UTF-8 BOM + CRLF) olmalı. .md, kullanıcının Windows görüntüleyicisinde bozuk görünüyor.

## Marka
- **Ad:** Birsıfır Teknoloji. Instagram kullanıcı adı `birsifirteknoloji`. Bu ad boştaydı, **hesap henüz açılmadı.** `birsifir` alınmış.
- **Konsept:** Herkesin anlayacağı dilde teknoloji. Pratik ipuçları, dolandırıcılık uyarıları, yapay zeka, "Kısa Kısa" haberler.
- **Logo:** Seçilen taslak `logo/birsifir_logos.html` içindeki 2. seçenek, mavi tonunda. Profil fotoğrafı: `brand/out/profil_fotografi.png`.
- **Renkler:**
  - Mavi `#0A5CFF`, koyu mavi `#0847C7`, açık mavi `#E8EFFF`
  - Mürekkep `#0B0F1A`, gri `#6B7280`, kağıt `#F6F7F9`
  - Sarı vurgu `#FFC300`
- **Yazı tipi:** Inter / Inter Display (800, sıkı harf aralığı).
- **Boyutlar:** Gönderi 1080x1350, story ve reels kapağı 1080x1920.
- Gönderilerde sağ altta marka ve kullanıcı adı yer alır. Kopyalamaya karşı hafif filigran kullanılır (`brand/out/koruma_karsilastirma.png`).

## Hazır olanlar (`birsifir/` klasörü)
- `logo/`: logo taslakları (HTML ve PNG), renk aileleri.
- `brand/templates.html` ve `style.css`: şablonlar (carousel kapak, iç sayfa, son sayfa, uyarı, reels kapak, story).
- `brand/posts.html`: ilk 9 gönderinin kaynağı. `art.js` illüstrasyon kütüphanesidir.
- `brand/ilk9/`: **ilk 9 gönderi hazır.** Toplam 42 slayt. Paylaşım rehberi ve açıklamalar `PAYLASIM_REHBERI.md` içinde.
  - Sıra: 1 tanışma · 2 WhatsApp 5 özellik · 3 kargo SMS uyarısı · 4 pil 5 ayar · 5 banka araması uyarısı · 6 yapay zeka nedir · 7 telefon yavaşladı · 8 yapay zeka ile CV · 9 güçlü şifre.
- `brand/news.html` ve `kisa_kisa/`: 3 haber (GTA 6, Nvidia, Voyager). Haberler eskimiş olabilir, **paylaşmadan önce güncelle.**
- Çizim: `node render_posts.js` ve `node render_news.js` (Playwright + Chromium).

## Durum ve sıradaki adımlar
1. Kullanıcı Instagram'da `birsifirteknoloji` hesabını açar. Profesyonel hesap, kategori "Dijital içerik üreticisi". Profil fotoğrafı ve biyografi Claude'dan alınır. 2FA açılır.
2. İlk 9 gönderi tek seferde, vitrin gibi paylaşılır. Sıra ve açıklamalar rehberde.
3. Haftalık içerik takvimi hazırlanır: haftada 3–4 gönderi, güncel "Kısa Kısa" haberleri, reels kapakları.
4. Paralel proje: StitchAnatolia (Etsy kanaviçe deseni mağazası). Kaynak kodu `stitchanatolia_kaynak/` klasöründe. O proje kendi akışıyla devam ediyor.
