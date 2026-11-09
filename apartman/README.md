# Apartman Yönetimi (Windows)

Tek yöneticinin kullandığı apartman aidat / gider takip programı. Şifreli giriş.

## İndirme
GitHub deposunun **Releases** bölümünden en son `Apartman-Yonetimi.zip` dosyasını indirin, "Tümünü ayıkla" ile açın ve klasördeki `Apartman-Yonetimi.exe` dosyasını çalıştırın. (Virüs programlarının yanlış alarmını azaltmak için tek dosya yerine klasör olarak paketlenir.)
İlk açılışta kurulum ekranı gelir (apartman adı, IBAN, daire sayısı, aylık aidat, şifre).

## Neler var
- **Daireler:** istenen sayıda daire (ekle / çıkar), kiracı veya ev sahibi, telefon, kiracı değişimi (eski kiracının hesabı ayrı kalır), daireye özel aidat, ek toplama pay oranı.
- **Aidat:** sabit aylık aidat; tutar değiştirilebilir (hangi aydan geçerli olacağı seçilir). Her ay program açılınca dairelere kendiliğinden yazılır.
- **Ön ödeme:** fazla ödeme "ön ödeme" olarak durur, sonraki aidat ve ek toplama paylarından kendiliğinden düşer.
- **Tahsilat:** havale / nakit, iade; ödeme sonrası WhatsApp teşekkür mesajı ve makbuz PDF.
- **Giderler:** kategori, banka / nakit, fiş dosyası; düzenli giderler (temizlikçi, asansör bakımı) için aylık hatırlatma.
- **Ek toplama:** toplam ya da daire başı tutar, eşit ya da pay oranına göre; sonradan değiştirilebilir.
- **Kasa:** banka ve nakit bakiyesi.
- **Raporlar (PDF):** aylık, yıllık, daire hesap dökümü, borç durumu, makbuz, ek toplama duyurusu — sade dille.
- **WhatsApp:** borç hatırlatma, teşekkür, gruba duyuru metinleri.

## Veriler
`%APPDATA%\ApartmanYonetimi\apartman.json` (varsayılan). Ayarlar → **Ortak klasör seç** ile Google Drive klasörüne taşınabilir; iki bilgisayar aynı verileri kullanır, kayıtlar birleştirilir.
PDF'ler: `Belgeler\Apartman Yonetimi`.

## Geliştirme
`python apartman.py` (Python 3, tkinter, reportlab). `.exe` her değişiklikte GitHub Actions ile derlenir (`.github/workflows/apartman.yml`).
