# Filament Maliyet

3D baskı projelerinin maliyetini hesaplayan ve filament stoğunu takip eden program. Tek bir HTML dosyasından oluşur ve internet olmadan çalışır.

## Kullanım
1. **Filamentler:** Elindeki makaraları ekle: marka, seri/ürün adı (ör. Matte-Dark Red), malzeme (PLA, PETG, ABS, ASA, TPU, PA, PC…), renk adı, renk, makara fiyatı ve stokta kalan gram. Liste kart ya da satır görünümünde gösterilebilir.
2. **Gruplar:** Müşteri veya kurum için grup aç (ör. Taşköprü Belediyesi, Seda) ve projeleri içine koy. Her grubun toplam maliyeti ve satış tutarı ayrıca görünür.
3. **Projeler → + Yeni proje:** Proje adını yaz ve grubunu seç.
4. **Tablalar:** Her tabla bir parçadır: parça adını ve tabladan çıkan adedi yaz. Satırlara filament seçip gram, saat ve dakika gir. Her satırın maliyeti ve açıklaması yanında yazar; tabla toplamına fire payı da eklenir.
5. Tabla basılınca **“Basıldı · stoktan düş”** düğmesine bas; yanlışlıkla bastıysan **“Basılmadı yap”** ile gram stoğa geri eklenir.
6. Sağdaki özette proje toplamı ve **her parçanın ayrı ayrı** adet başı maliyeti ile satış fiyatı görünür.
7. Projeye müşteriden aldığın parayı **Alınan ücret** alanına yaz; kâr buna göre hesaplanır. Boş bırakılırsa önerilen satış fiyatı tahmini gelir olarak kullanılır.

## PDF raporlar
- **Proje raporu:** projeyi açıp **📄 PDF rapor** düğmesine bas. Raporda giderler, gelir, kâr, parçalar, baskı detayı ve kullanılan filamentler yer alır.
- **Grup raporu:** gruba girip **📄 Grup raporu** düğmesine bas. O gruptaki bütün işler ve grubun toplam gideri, geliri ve kârı listelenir.
- **Genel rapor:** Projeler sayfasındaki **📄 Genel rapor** düğmesine bas ve dönemi seç (tüm zamanlar, bu ay, geçen ay, son 30 gün, bu yıl). Rapor, gruplara göre ve iş iş toplamları gösterir.
- Açılan yazdırma penceresinde yazıcı olarak **“PDF olarak kaydet”** seç.

## Ayarlar
Burada elektrik fiyatı (vergiler dahil TL/kWh), makinenin gücü, makine fiyatı ve ömrü, bakım, fire payı ve kâr marjı ayarlanır. Ayarlar sekmesinden yedek indirip yükleyebilirsin; cihazlar arasında veri taşımak için yedeği Google Drive'a koy.

## Windows
GitHub Releases sayfasındaki `Filament-Maliyet.zip` dosyasını indir ve ayıkla, ardından `Filament-Maliyet.exe`'yi çalıştır. Program, Microsoft Edge ile kendi penceresinde açılır.
