# Apartman Yönetimi

Tek yöneticinin kullandığı, iPhone ve bilgisayardan açılan apartman aidat / gider takip programı.
Google Apps Script web uygulaması; veriler Google E-Tablo'da. Kurulum: [KURULUM.md](KURULUM.md)

## Neler var
- **Daireler:** istenen sayıda daire (ekle / çıkar), kiracı veya ev sahibi, telefon, kiracı değişimi (eski kiracının hesabı ayrı kalır), daireye özel aidat, ek toplama pay oranı.
- **Aidat:** sabit aylık aidat; tutar değiştirilebilir (hangi aydan geçerli olacağı seçilir). Her ay program açılınca dairelere kendiliğinden yazılır.
- **Ön ödeme:** fazla ödeme bakiyede "alacak" olarak durur, sonraki aidat ve ek toplama paylarından kendiliğinden düşer.
- **Tahsilat:** havale / nakit, iade; ödeme sonrası WhatsApp teşekkür mesajı ve makbuz PDF.
- **Giderler:** kategori, banka / nakit, fiş fotoğrafı; düzenli giderler (temizlikçi, asansör bakımı) için aylık hatırlatma.
- **Ek toplama:** asansör tamiri gibi işler; toplam ya da daire başı tutar, eşit ya da pay oranına göre; sonradan değiştirilebilir.
- **Kasa:** banka ve nakit bakiyesi.
- **Raporlar (PDF):** aylık, yıllık, daire hesap dökümü, borç durumu, makbuz, ek toplama duyurusu — sade dille.
- **WhatsApp:** borç hatırlatma, teşekkür, gruba duyuru metinleri.
- **Güvenlik:** Google hesabı ("Yalnızca ben") + program şifresi.

## Dosyalar
- `Kod.gs` – sunucu (E-Tablo okuma/yazma, oturum, PDF, dosya yükleme)
- `Sayfa.html` – arayüz ve hesaplar
