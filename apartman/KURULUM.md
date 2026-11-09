# Apartman Yönetimi – Kurulum

Program Google E-Tablolar üzerinde çalışır. Veriler `arabacireklam37@gmail.com` hesabının Google Drive'ında bir E-Tablo'da durur.
iPhone'da Safari'den, bilgisayarda tarayıcıdan açılır. Kurulum bir kez, **bilgisayardan** yapılır (yaklaşık 10 dakika).

## 1. E-Tablo'yu oluştur
1. Bilgisayarda Chrome'da `arabacireklam37@gmail.com` ile Google'a giriş yap.
2. Adres çubuğuna `sheets.new` yaz. Boş bir E-Tablo açılır.
3. Sol üstte "Adsız e-tablo" yazan yere tıkla, adını **Apartman Yönetimi** yap.

## 2. Kodu yapıştır
1. Üst menüden **Uzantılar → Apps Script**. Yeni sekmede kod düzenleyici açılır.
2. Soldaki **Kod.gs** dosyası açık. İçindeki her şeyi sil.
3. GitHub'da `apartman/Kod.gs` dosyasını aç, sağ üstteki **"Copy raw file"** (kopyala) düğmesine bas, Apps Script'e yapıştır.
4. Soldaki **Dosyalar** yanındaki **＋** → **HTML** seç, adını tam olarak **Sayfa** yaz (".html" yazma, kendisi ekler).
5. İçindeki her şeyi sil. GitHub'da `apartman/Sayfa.html` dosyasını aç, **"Copy raw file"** ile kopyala, buraya yapıştır.
6. Üstteki **💾 Kaydet** simgesine bas.

## 3. Yayınla
1. Sağ üstte **Dağıt → Yeni dağıtım**.
2. "Tür seçin" yanındaki ⚙ simgesi → **Web uygulaması**.
3. Ayarlar:
   - Açıklama: `Apartman`
   - **Yürütme sahibi: Ben**
   - **Erişimi olan kullanıcılar: Yalnızca ben**
4. **Dağıt**'a bas. Google izin ister:
   - **Erişimi yetkilendir** → hesabını seç.
   - "Google bu uygulamayı doğrulamadı" uyarısı çıkarsa: **Gelişmiş** → **Apartman Yönetimi (güvenli değil) sayfasına git** → **İzin ver**.
     (Bu uyarı, kodu kendin yazıp kendin kullandığın için çıkar; uygulama sadece senin E-Tablo'na erişir.)
5. Çıkan **Web uygulaması URL'sini** kopyala (`https://script.google.com/macros/s/.../exec`). Bu senin program adresin.

## 4. İlk açılış
URL'yi aç. Kurulum ekranı gelir: apartman adı, IBAN, daire sayısı, aylık aidat, şifre. Doldur, **Kurulumu tamamla**.
Sonra **Daireler** sekmesinden her daireye kiracıyı (ad ve telefon) ekle.

## 5. iPhone'a ekle
1. iPhone'da **Safari**'de Google'a `arabacireklam37@gmail.com` ile giriş yap.
2. Program URL'sini Safari'de aç (kendine WhatsApp'tan gönderebilirsin).
3. Alttaki **Paylaş** düğmesi → **Ana Ekrana Ekle** → **Ekle**.

Not: Safari'de aynı anda birden fazla Google hesabı açıksa Google bazen "dosya açılamıyor" hatası verir.
Böyle olursa Safari'de sadece `arabacireklam37@gmail.com` hesabıyla giriş yapılı kalsın.

## Güncelleme (yeni sürüm geldiğinde)
1. E-Tablo → **Uzantılar → Apps Script**.
2. Değişen dosyayı (Kod.gs ve/veya Sayfa) yukarıdaki gibi silip yenisini yapıştır, **Kaydet**.
3. **Dağıt → Dağıtımları yönet** → kalem ✏ simgesi → **Sürüm: Yeni sürüm** → **Dağıt**.

Program adresi değişmez, verilere dokunulmaz.

## Veriler nerede?
- Bütün kayıtlar E-Tablo'nun sayfalarında: Daireler, Sakinler, Borclar, Odemeler, Giderler, EkToplamalar, ... Bu sayfaları elle **değiştirme**; bakmak serbest.
- PDF raporlar ve fiş fotoğrafları Drive'da **Apartman Yönetimi** klasöründe.
- Şifre E-Tablo'da değil, betiğin gizli ayarlarında özet (hash) olarak tutulur.
