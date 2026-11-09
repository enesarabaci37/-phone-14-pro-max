# Arabacı Reklam - m² Hesaplama

Windows için m² fiyat, malzeme maliyeti, kazanç, KDV ve indirim hesaplama programı.

## İndirme
GitHub deposunun **Releases** bölümünden en son `Arabaci-M2-Hesaplama.exe` dosyasını indirin ve çift tıklayın. Kurulum gerekmez.
İlk açılışta "Windows bilgisayarınızı korudu" uyarısı çıkarsa **Ek bilgi → Yine de çalıştır** deyin.

## Ekranlar
- **Teklif Hazırla (müşteri ekranı):** müşteri adı; teklife istediğiniz kadar **kalem** eklenir:
  - **Malzeme (m²):** malzeme, ölçü birimi (cm / mm / m), en, boy, adet, m² fiyatı (malzemenin kayıtlı satış fiyatı gelir). Malzemenin minimum m²'si varsa uygulanır.
  - **Hizmet:** montaj, tasarım, söküm, nakliye… (sabit, adet başına ya da m² başına).
  - Toplam: KDV oranı, minimum teklif tutarı, genel toplamı 1 / 5 / 10 / 50 / 100 TL'ye yuvarlama.
  - **PDF Teklif:** logolu, kalem kalem müşteri teklifi; teklif notları ve IBAN ile. `Belgeler\Arabaci Reklam` klasörüne kaydedilir.
  - **WhatsApp için kopyala:** teklif metnini panoya kopyalar.
  - Alış fiyatı, maliyet ve kâr bu ekranda görünmez.
- **KDV ve İndirim:** KDV (hariç / dahil fiyattan) ve indirim hesapları (indirimli fiyat, normal fiyat, indirim oranı).
- **🔒 Yönetim (şifreli):**
  - **Malzemeler:** alış fiyatı TL / Dolar / Euro (TCMB kuru), satış fiyatı, fire payı, minimum m².
  - **Hizmetler:** fiyatlama türü, satış fiyatı, isteğe bağlı maliyet (boşsa tamamı kâr).
  - **Bu Teklifin Kârı:** kalem kalem satış, maliyet ve kâr.
  - **Kayıtlar ve Kâr Raporu:** verilen teklifler, toplamlar, PDF kâr raporu, teklifi yeniden yazdırma.
  - **Firma ve Teklif:** firma bilgileri, IBAN, logo, teklif notları, minimum teklif tutarı.
  - **Ayarlar:** alış KDV oranı, şifre, veri klasörü (Google Drive).

Yönetim şifresi ilk girişte belirlenir ve veri dosyasında özet (hash) olarak tutulur. Bu, ekranı müşteriden gizlemek içindir; bilgisayara erişen biri veri dosyasını yine de açabilir.
Eski sürümlerin (v2, v3) verileri ve kayıtları otomatik olarak yeni yapıya çevrilir.

## Veriler ve birden fazla bilgisayar
Varsayılan olarak veriler `%APPDATA%\ArabaciM2\veriler.json` dosyasındadır (sadece o bilgisayar).
Birden fazla bilgisayarda ortak kullanmak için her bilgisayara Google Drive masaüstü uygulamasını aynı hesapla kurun,
sonra **Yönetim → Ayarlar → Ortak klasör seç** ile Google Drive'daki aynı klasörü seçin. Program içinde `ArabaciM2` klasörünü oluşturur.
Teklif kayıtları bilgisayarlar arasında birleştirilir; malzeme ve fiyat değişiklikleri birkaç saniye içinde diğer bilgisayara geçer.
Her bilgisayarın ekran tercihleri ve seçtiği klasör `%APPDATA%\ArabaciM2\bu_bilgisayar.json` dosyasında durur.

## Geliştirme
`python m2_hesaplama.py` (Python 3, tkinter, reportlab). `.exe` her değişiklikte GitHub Actions ile derlenir (`.github/workflows/m2-hesaplama.yml`).
PDF yazı tipi: DejaVu Sans (`fonts/`, serbest lisans).
