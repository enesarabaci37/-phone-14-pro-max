# Filament Maliyet

3D baskı projelerinin maliyetini hesaplayan ve filament stoğunu takip eden program. Tek bir HTML dosyasından oluşur ve internet olmadan çalışır.

## Kullanım
1. **Filamentler:** Elindeki makaraları ekle: marka, seri, malzeme (PLA, PETG, ABS, ASA, TPU, PA, PC…), renk, makara fiyatı ve stokta kalan gram.
2. **Projeler → + Yeni proje:** Projeye isim ve parça adedi ver.
3. Her **tabla** içine renkleri ekle; her rengin kaç gram ve kaç saat/dakika basıldığını yaz. Tablanın süresi bu satırların toplamıdır. Tabla eklenebilir, çoğaltılabilir ve silinebilir.
4. Tabla basılınca **“Basıldı · stoktan düş”** düğmesine bas; kullanılan gram stoktan düşer. Yanlışlıkla bastıysan **“Basılmadı yap”** ile gram stoğa geri eklenir.
5. Sağdaki özette şunlar görünür: filament, elektrik, makine yıpranması, fire payı, ek masraf, toplam maliyet, parça başı maliyet ve önerilen satış fiyatı.

## Ayarlar
Burada elektrik fiyatı (vergiler dahil TL/kWh), makinenin gücü, makine fiyatı ve ömrü, bakım, fire payı ve kâr marjı ayarlanır. Ayarlar sekmesinden yedek indirip yükleyebilirsin; cihazlar arasında veri taşımak için yedeği Google Drive'a koy.

## Windows
GitHub Releases sayfasındaki `Filament-Maliyet.zip` dosyasını indir ve ayıkla, ardından `Filament-Maliyet.exe`'yi çalıştır. Program, Microsoft Edge ile kendi penceresinde açılır.
