# Filament Maliyet

Bambu Lab baskıları için maliyet hesaplayıcı ve filament stok takibi. Tek bir HTML dosyası; internet gerekmez.

## Ne yapar?
- **Hesapla:** Bambu Studio'dan dışa aktardığın `.gcode.3mf` (veya `.gcode`) dosyasını bırak. Her renk için kullanılan gram ve baskı süresi otomatik okunur, renkler stoktaki en yakın filamentle eşleşir. Maliyet şu kalemlerden oluşur: filament, elektrik, makine yıpranması/bakım, fire payı ve ek masraf. Parça başı maliyet ve önerilen satış fiyatı da hesaplanır.
- **Filamentler:** Marka, seri, renk, fiyat ve kalan gram bilgileri. “+1 makara” ile stok eklenir.
- **Geçmiş:** Kaydedilen baskılar ve aylık/toplam harcama. Excel'e (CSV) aktarılabilir.
- **Ayarlar:** Elektrik fiyatı, güç, makine fiyatı, fire ve kâr oranı. Yedekleme (.json) de buradan yapılır.

## .gcode.3mf nasıl alınır?
Bambu Studio → **Dilimle** → sağ üstteki ok → **Dışa aktar → Plaka dilimlenmiş dosyasını dışa aktar**.

## Kurulum
- **Bilgisayarda program gibi:** GitHub Pages adresini Chrome veya Edge ile aç, adres çubuğundaki **“Uygulamayı yükle”** simgesine tıkla. Uygulama kendi penceresinde açılır, Başlat menüsüne ve masaüstüne eklenir, internet olmadan da çalışır.
- **iPhone:** Safari ile aç → Paylaş → **Ana Ekrana Ekle**.
- **İnternetsiz / Drive:** `index.html` dosyasını indirip çift tıklaman yeterli.

Veriler her cihazın kendi tarayıcısında saklanır. Cihazlar arasında taşımak için Ayarlar → **Yedeği indir** ile aldığın dosyayı Drive'a koy, diğer cihazda **Yedeği yükle** de.
