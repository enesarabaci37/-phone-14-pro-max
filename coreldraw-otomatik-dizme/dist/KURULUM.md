# CorelDRAW Otomatik Dizme (Montaj) Makrosu

Seçtiğiniz nesneleri, girdiğiniz malzeme ölçüsüne en az fire ile otomatik dizer.

## Özellikler
- Malzeme genişliği ve yüksekliği (mm)
- Nesneler arası boşluk ve malzeme kenar payı ayarı
- Her nesneden istenen adet kadar kopya (ör. 1 logo × 50 adet)
- 90° döndürme izni (açık/kapalı)
- Sığmayan parçalar için otomatik olarak yeni plaka açılır. Plakalar sayfanın sağına doğru yan yana dizilir.
- İsteğe bağlı kırmızı malzeme çerçevesi
- Her plaka için doluluk ve fire yüzdesi raporu
- Tek seferde **Ctrl+Z** ile tamamen geri alınabilir
- Girdiğiniz son değerler hatırlanır

> Nesneler dış sınır kutularına göre (kontur kalınlığı dahil) dizilir. Yuvarlak veya düzensiz şekiller de kapladıkları dikdörtgene göre yerleştirilir.

## Kurulum (bir kez yapılır)
1. CorelDRAW'u açın, **Alt+F11** ile Makro Düzenleyiciyi (VBA) açın.
2. Sol üstteki *Project* penceresinde **GlobalMacros (GlobalMacros.gms)** projesine tıklayın.
3. **File → Import File...** ile `modDizme.bas` dosyasını içe aktarın.
4. **Insert → UserForm** ile boş bir form ekleyin.
5. *Properties* penceresinde (görünmüyorsa F4) formun **(Name)** değerini `frmDizme` yapın.
6. Forma sağ tıklayıp **View Code** seçin. Oradaki her şeyi silin ve `frmDizme_kod.txt` dosyasının tamamını yapıştırın.
7. **Ctrl+S** ile kaydedin ve düzenleyiciyi kapatın.

## Kullanım
1. Dizilecek nesneleri seçin. Gruplu nesneler tek parça sayılır.
2. **Araçlar → Makrolar → Makroyu Çalıştır** menüsünden `modDizme.OtomatikDizme` makrosunu çalıştırın.
3. Ölçüleri girip **DİZ** düğmesine basın.

### Araç çubuğuna düğme eklemek
**Araçlar → Seçenekler → Özelleştirme → Komutlar** bölümünde listeden **Makrolar**ı seçin. `OtomatikDizme` öğesini sürükleyip bir araç çubuğuna bırakın.

## Sorun giderme
- **"Compile error / User-defined type not defined"**: VBA düzenleyicide **Tools → References** bölümünde *Microsoft Forms 2.0 Object Library* seçili olmalıdır. UserForm eklediğinizde bu kütüphane genellikle otomatik seçilir.
- **Türkçe karakterler bozuk görünüyorsa**: Windows'ta *Unicode olmayan programların dili* Türkçe olmalıdır. Program bozuk karakterlerle de çalışır, yalnızca yazılar düzgün görünmez.
- **Makrolar çalışmıyorsa**: CorelDRAW kurulumunda *VBA* bileşeninin kurulu olduğundan emin olun.
