# Arabacı Reklam - m² Hesaplama

Windows için m² fiyat, malzeme maliyeti, kazanç, KDV ve indirim hesaplama programı.

## İndirme
GitHub deposunun **Releases** bölümünden en son `Arabaci-M2-Hesaplama.exe` dosyasını indirin ve çift tıklayın. Kurulum gerekmez.

İlk açılışta "Windows bilgisayarınızı korudu" uyarısı çıkarsa **Ek bilgi → Yine de çalıştır** deyin (imzasız küçük programlarda normaldir).

## Özellikler
- **m² Fiyat ve Kâr:** ölçü birimi (cm / mm / m), en, boy, adet → toplam m²; müşteri fiyatı (KDV hariç, KDV, KDV dahil); malzeme maliyeti TL / Dolar / Euro (TCMB kuru otomatik), fire payı; kazanç, kâr oranı, m² başına kazanç; müşteri teklifini panoya kopyalama (WhatsApp için).
- **KDV Hesaplama:** KDV hariç ya da dahil fiyattan hesap.
- **İndirim / İskonto Hesaplama**

Son kullanılan fiyatlar, KDV oranları ve kur `%APPDATA%\ArabaciM2\ayarlar.json` dosyasında saklanır.

## Geliştirme
Sadece Python standart kütüphanesi (tkinter) kullanılır: `python m2_hesaplama.py`.
`.exe` dosyası her değişiklikte GitHub Actions ile otomatik derlenir (`.github/workflows/m2-hesaplama.yml`).
