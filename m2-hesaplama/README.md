# Arabacı Reklam - m² Hesaplama

Windows için m² fiyat, malzeme maliyeti, kazanç, KDV ve indirim hesaplama programı.

## İndirme
GitHub deposunun **Releases** bölümünden en son `Arabaci-M2-Hesaplama.exe` dosyasını indirin ve çift tıklayın. Kurulum gerekmez.
İlk açılışta "Windows bilgisayarınızı korudu" uyarısı çıkarsa **Ek bilgi → Yine de çalıştır** deyin.

## Ekranlar
- **m² Fiyat Hesaplama (müşteri ekranı):** müşteri adı, malzeme, ölçü birimi (cm / mm / m), en, boy, adet, KDV → toplam m², KDV hariç, KDV, KDV dahil fiyat. Alış fiyatı ve kâr bu ekranda görünmez.
  - **PDF Teklif:** logolu müşteri teklifi oluşturur, `Belgeler\Arabaci Reklam` klasörüne kaydeder ve kaydı yönetime ekler.
  - **WhatsApp için kopyala:** teklif özetini panoya kopyalar.
- **KDV ve İndirim:** KDV (hariç / dahil fiyattan) ve indirim hesapları (indirimli fiyat, normal fiyat, indirim oranı).
- **🔒 Yönetim (şifreli):**
  - **Malzemeler:** malzeme ekle / düzenle / sil; alış fiyatı TL, Dolar ya da Euro; satış fiyatı; fire payı. Dolar ve Euro fiyatlar TCMB kuruyla otomatik TL'ye çevrilir.
  - **Bu Hesabın Kârı:** müşteri ekranındaki hesabın maliyeti ve kazancı.
  - **Kayıtlar ve Kâr Raporu:** verilen teklifler, toplam satış / maliyet / kâr, PDF kâr raporu.
  - **Ayarlar:** alış KDV oranı, şifre değiştirme.

Veriler `%APPDATA%\ArabaciM2\veriler.json` dosyasında saklanır. Şifre bu dosyada özet (hash) olarak tutulur. Bu, ekranı müşteriden gizlemek içindir; bilgisayara erişen biri veri dosyasını yine de açabilir.

## Geliştirme
`python m2_hesaplama.py` (Python 3, tkinter, reportlab). `.exe` her değişiklikte GitHub Actions ile derlenir (`.github/workflows/m2-hesaplama.yml`).
PDF yazı tipi: DejaVu Sans (`fonts/`, serbest lisans).
