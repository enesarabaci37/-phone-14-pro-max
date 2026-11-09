# Kira Takip (Windows)

Binalar, daireler, kiracılar, sözleşmeler ve kira takibi. Şifreli giriş.

## İndirme
GitHub deposunun **Releases** bölümünden en son `Kira-Takip.zip` dosyasını indirin, "Tümünü ayıkla" ile açın, klasörü kalıcı bir yere koyun ve klasördeki `Kira-Takip.exe` için masaüstüne kısayol oluşturun.

## Neler var
- **Binalar ve daireler:** bina / daire ekle-çıkar; daire başına ev sahibi (ad, TC, telefon), tapu ve DASK belgeleri, abonelik numaraları, DASK bitiş tarihi, eşya notu. Ev sahibi ve tapu daireye bağlıdır, kiracı değişince yerinde kalır.
- **Kiracılar:** ad soyad, TC, telefon, e-posta, acil durumda aranacak kişi; kimlik fotoğrafı / fotokopisi, taranmış sözleşme gibi belgeler; taşınma tarihi, ilk kira, güncel kira, depozito, sözleşme başlangıç / bitiş, ödeme günü, eşya notu. Çıkan kiracılar arşivde kalır (depozito iadesi kaydıyla).
- **TÜFE ile kira artışı:** oran girilir, yeni kira hesaplanır, artış geçmişi tutulur.
- **Kira ödeme takibi** (isteğe bağlı): her ay kira borcu yazılır, ödemeler, gecikmeler, WhatsApp mesajı.
- **Hatırlatmalar:** sözleşme bitişi, kira artış zamanı, DASK bitişi, geciken kira.
- **Raporlar (PDF):** yıllık kira geliri (ay ay), kiracı kartı, kiracı listesi.

## Veriler
`%APPDATA%\KiraTakip\kira.json` ve `belgeler\` klasörü. Ayarlar → **Ortak klasör seç** ile Google Drive'a taşınabilir.
Kimlik ve sözleşme gibi kişisel bilgiler içerir; Drive klasörünü başkalarıyla paylaşmayın.

## Geliştirme
`python kira_takip.py` (Python 3, tkinter, reportlab). `.exe` GitHub Actions ile derlenir (`.github/workflows/kira-takip.yml`).
