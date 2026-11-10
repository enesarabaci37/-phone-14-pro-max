# Ders Bahçesi: Proje Notları ve Devir Belgesi

> Yeni oturumdaki Claude için: Bu dosya, önceki sohbette kullanıcıyla (veli) konuşulan her şeyi özetler. Konuşma Türkçe; kullanıcıya Türkçe, sade ve sıcak bir dille cevap ver. Kararlar aşağıda **kesinleşti**. Kullanıcı "başla" dediğinde doğrudan yapmaya geç, aynı soruları tekrar sorma.

## Kim için, ne yapıyoruz

- Kullanıcının **8 yaşında, 2. sınıfa giden kızı** için eğitici oyunlar.
- **1. aşama bitti:** `akil-bahcesi.html` (ve onun bağımsız hali `index.html`): 5 zeka oyunu (Hafıza Kartları, Sıradaki Ne?, Meyve Sudoku, Kaydır Diz, Renk Sırası). Seviye ve yıldız sistemi var, ilerleme `localStorage`'da saklanıyor.
  - Claude linki: https://claude.ai/artifact/9bSS26YNrkhahnhHQLCTLX
- **2. aşama (yapılacak):** 2. sınıf müfredatına göre **4 dersin hepsini** kapsayan tek bir ders uygulaması. Akıl Bahçesi oyunları da bunun içine girecek.

## Kesinleşen kararlar

1. **Dört ders birden:** Matematik, Türkçe, Hayat Bilgisi, İngilizce.
2. **Sesli okuma olacak:** Talimatlar ve sorular okunacak (Web Speech API `speechSynthesis`, `tr-TR`; İngilizce kelimeler için `en-US`/`en-GB`). Ses yoksa veya çalışmazsa sayfa yine sorunsuz çalışmalı. Sesi açıp kapatan bir düğme olmalı. iPad Safari'de ses ancak bir dokunuştan sonra başlar.
3. **Akıl Bahçesi'nin 5 oyunu** yeni uygulamanın içinde bir bölüm olarak yer alacak.
4. **Cihaz: Apple iPad (Safari).** Büyük dokunma alanları olmalı; hem yatay hem dikey çalışmalı. Hover'a dayanan bir etkileşim olmamalı.
5. **Yayınlama:**
   - Önce **Claude linki** (Artifact). Veli kendi telefonundan deneyecek.
   - Sonra **GitHub Pages** (ücretsiz). Veli ayrı ve **herkese açık** bir depo açacak (ad önerisi: `ders-bahcesi`). iPad'de Safari'den "Ana Ekrana Ekle" ile uygulama gibi kullanılacak. Veliye GitHub Pages ayarını adım adım göster.
   - Ücretli GitHub planına gerek olmadığı konuşuldu: ücretli plan Pages sitesini gizli yapmıyor, sadece kodu gizliyor.
   - Kızın tabletinde Claude'a giriş **yapılmayacak**.
6. **Gizlilik:** Uygulamada kızın adı, fotoğrafı veya kişisel bilgisi olmayacak. İlerleme sadece cihazda (`localStorage`) tutulacak, hiçbir şey internete gönderilmeyecek.
7. **Henüz cevaplanmamış (isteğe bağlı) sorular:**
   - Veli ekranı (hangi konuda kaç doğru/yanlış) isteniyor mu? Sorulmuştu ama cevap gelmedi. Basit bir veli özeti eklemek mantıklı, sonra sorulabilir.
   - Kitabın içindekiler sayfasının fotoğrafı: gelirse öğretmenin işlediği sıraya göre öncelik verilir.

## Müfredat özeti (MEB Türkiye Yüzyılı Maarif Modeli, 2. sınıf)

Kaynak: tymm.meb.gov.tr'deki resmi öğretim programları. Dikkat: arama sonuçlarında çıkan bazı belgeler özel eğitim programına ait; onlar kullanılmamalı.

### Matematik (180 saat, haftada ~5). İşleniş sırası:
1. **Nesnelerin Geometrisi (1)** (25 saat): nesneleri geometrik şekillere göre sınıflama, cisimlerle yapı kurma, şekillerle model oluşturma, yön/konum/büyüklük değişince ne değişir, standart olmayan araçlarla sıvı ölçümü tahmini
2. **Sayılar ve Nicelikler (1)** (41 saat): 100'e kadar sayılar, onluk-birlik çözümleme, sayı doğrusu, sıralama, onluğa yuvarlama. **Ritmik sayma:** 20 içinde ikişer, 30 içinde üçer, 40 içinde dörder, 100 içinde beşer ve onar (ileri ve geri), yüzlük tablo. Sayı ve şekil örüntüleri (3 = üçgen, 4 = kare…). 50'ye kadar nesne sayısını tahmin etme.
3. **İşlemlerden Cebirsel Düşünmeye** (55 saat): toplamı 100'ü geçmeyen eldeli toplama (iki ve üç sayı), 100 içinde çıkarma, günlük yaşam problemleri, tahmin ve zihinden işlem, toplama-çıkarma ilişkisi. **Çarpma:** tekrarlı toplama, 1-2-3-4-5 ile çarpma, **5'e kadar çarpım tablosu**, değişme özelliği. **Bölme:** eşit paylaştırma ve ardışık çıkarma (bölünen, bölen, bölüm, kalan). Eşitliğin anlamı. Kavramlar: deste vb.
4. **Sayılar ve Nicelikler (2)** (30 saat): bütün-yarım-çeyrek; paralar (madenî paralar, kuruş-lira); zaman: **tam, yarım ve çeyrek saat** (analog saat), dakika-saat, saat-gün, gün-hafta-ay, ay-mevsim-yıl; metre, santimetre, kilogram, gram (tahmin ve ölçme).
5. **Nesnelerin Geometrisi (2)** (11 saat): mesafe ve yön kullanarak hedefe ulaşma stratejisi (kodlama benzeri), simetrik şekilleri ayırt etme
6. **Veriye Dayalı Araştırma** (10 saat): en çok iki kategorik veri grubu, nesne grafiği ve tablo

Kasım ayında çoğu sınıf 2. temada (100'e kadar sayılar, ritmik sayma) olur.

### Türkçe (haftada ~8 saat). 8 tema:
Değerlerimizle Varız · Atatürk ve Çocuk · Doğada Neler Oluyor? · Okuma Serüvenimiz · Yeteneklerimizi Tanıyoruz · Mucit Çocuk · Kültür Hazinemiz · Haklarımızı Biliyoruz

Beceriler: vurgu, tonlama ve noktalamaya dikkat ederek okuma; okuduğunu anlama (karakter, olay sırası, neden-sonuç, başlık ve görselden konuyu tahmin etme); **zıt anlamlı sözcükler**; bilinmeyen sözcüğün anlamını resimli sözlük ve bağlamdan bulma; yazımda **büyük harf**, **noktalama** ve **kısaltmalar**; anlamlı ve kurallı cümle kurma.

### Hayat Bilgisi (144 saat, haftada 4). 6 öğrenme alanı:
1. **Ben ve Okulum:** planlı olmak, öğretmen ve arkadaşlarla iletişim, arkadaşlık, sınıf içi karar alma
2. **Sağlığım ve Güvenliğim:** sağlıklı büyüme ve alışkanlıklar, **çevrim içi güvenlik**, **temel trafik işaret levhaları**, acil durumda yetkililerle iletişim (112)
3. **Ailem ve Toplum:** ailenin önemi, nezaket ve görgü kuralları, görev ve sorumluluklar
4. **Yaşadığım Yer ve Ülkem:** tarihî mekânlar ve doğal güzellikler, yönetim birimleri (il, ilçe, muhtarlık), **Atatürk'ün öğrencilik hayatı**, millî ve dinî gün ve bayramlar
5. **Doğa ve Çevre:** **hava olayları ve mevsimler**, doğadan yararlanarak yön bulma, afetlere karşı önlemler, doğal kaynakları tasarruflu kullanma
6. **Bilim, Teknoloji ve Sanat:** bilim insanları, teknolojik ürünlerin değişimi, sanatın günlük yaşamdaki yeri

### İngilizce (A1.1, haftada 2 saat). 6 tema:
1. **School Life:** selamlaşma ve tanışma, okuldaki kişiler ve yerler, haftanın günleri, bayramlar
2. **Classroom Life:** sınıf komutları, sınıf eşyaları, **renkler** (red, white, black, pink, blue, purple, yellow, brown, green, orange)
3. **Personal Life:** **vücut bölümleri** ve fiziksel özellikler, kıyafetler, yaş ve doğum günü, hava durumu
4. **Family Life:** aile üyeleri ve görünüşleri (big, small, tall…)
5. **Homes & Houses & Neighbourhoods:** evin bölümleri, odalar, eşyalar, **evcil hayvanlar**
6. **Life in the City & the World:** temel yiyecekler, öğünler, **meyveler** (tomatoes, bananas, apples, oranges, pears, strawberries, grapes, cherries)

Sayılar 1-20. Odak dinleyip tanıma; yazma çok az.

## Önerilen oyun fikirleri (veliyle konuşuldu)

- **Matematik:** onluk-birlik blokları, yüzlük tabloda ritmik sayma, analog saati parmakla kurma (tam/yarım/çeyrek), market ve para üstü (kuruş-lira), pizza ile yarım/çeyrek, çarpmayı gruplarla gösterme (3 sepet × 4 elma), simetri tamamlama, yön oklarıyla robotu hedefe götürme, nesne grafiği okuma, sayı doğrusu.
- **Türkçe:** kısa hikaye ve anlama soruları (sesli okumalı), zıt anlamlı eşleştirme, karışık olayları sıraya dizme, büyük harf ve noktalama hatasını bulma, kısaltmalar, resimli sözlük.
- **Hayat Bilgisi:** trafik işaretleri, mevsim ve hava olayları eşleştirme, sağlıklı/sağlıksız ayırma, internette doğru davranış, bayramlar, Atatürk'ün öğrencilik hayatı, tasarruf.
- **İngilizce:** dokununca sesli okunan resimli kelime kartları, "Dinle, doğru resmi seç", renk ve sayı oyunları.

## Pedagojik ilkeler (konuşuldu)

- Önce **görerek** anlatım (somut model), sonra alıştırma.
- Yanlışta önce **ipucu** ver ("Önce birlikleri topla"), cevabı hemen söyleme.
- Zorlandığı sorular daha sık tekrar gelsin (basit aralıklı tekrar).
- Kısa oturumlar (günde 10-15 dakika), 1-3 yıldız, kaybedince cesaretlendirici dil ("Az kaldı!").

## Teknik notlar (1. aşamadan öğrenilenler)

- Artifact dosyasında `<!doctype>`, `<html>`, `<head>` ve `<body>` yok; yayınlarken iskelet ekleniyor. GitHub Pages için `index.html` bağımsız sürüm olmalı (doctype, viewport meta ve `apple-mobile-web-app-capable` ile).
- CSS'de `[hidden]{display:none!important}` **şart**. Yoksa `display:grid` olan gizli modal bağımsız sürümde dokunmaları engelliyor (bu hata yaşandı).
- Sınıf adı çakışmasına dikkat: kart arka yüzü için `.back` kullanmak "Oyunlar" geri düğmesini boyamıştı; `.cback` olarak değiştirildi.
- Fontlar: Baloo 2 (başlık) ve Nunito (metin), Google Fonts'tan.
- Test: Playwright ile 390 px ve iPad genişliğinde (~820 px) açıp her oyunu tıklayarak konsol hatasına bak.
- Dal: `claude/happy-feynman-ga17g5`. Commit ve push sonrası veliye linki ver.

## Durum (2. aşama)

- **Ders Bahçesi yapıldı:** `ders-bahcesi.html` (Artifact) ve `index.html` (bağımsız, `tools/build_index.py` ile üretilir). 4 ders + Akıl Bahçesi, toplam 42 konu.
- Veli ekranı eklendi (6-9 arası iki sayının çarpımı ile açılıyor).
- Akıl Bahçesi'nin eski kayıtları (`akil-bahcesi-v1`) ilk açılışta yeni kayda taşınıyor.
- Test: Playwright ile 390 px ve 820 px'te her konunun her seviyesi baştan sona oynandı (ipucu ve cevap gösterme dahil), konsol hatası yok.

## Akıl Bahçesi'ne eklenecek 4 yeni oyun (veli onayladı)

**Aynı linke** eklenecek: `akil-bahcesi.html` dosyası güncellenip https://claude.ai/artifact/9bSS26YNrkhahnhHQLCTLX adresine yeniden yayınlanacak (yeni oturumda `url` parametresiyle; önce `action: "read"` ile oku). `index.html` de güncellenecek. Mevcut ilerleme (`localStorage` anahtarı `akil-bahcesi-v1`) korunmalı. Hepsi bölüm bölüm ilerleyecek ve 1-3 yıldız verecek.

1. **Labirent:** Yol, **Apple Pencil veya parmakla çizilir** (Pointer Events, `touch-action:none`). Çizgi duvardan geçemez. Labirentler her seferinde yeni üretilir ve bölüm geçtikçe büyür. İleri bölümlerde önce anahtar, sonra kapı.
2. **Robot Yolu (kodlama):** Ok komutlarını sıraya dizer, "Çalıştır" ile robotun hareketini izler. Zorluk sırası: düz yol → dönüşler → engeller → birden fazla yıldız → **"tekrarla" bloğu** (döngü). 3 yıldız için en az komut.
3. **Terazi Bulmacası:** tek terazi (1 karpuz = 3 elma) → iki terazi zinciri → üç terazi ve sayılar. Sorular her seferinde yeniden üretilir.
4. **Hanoi Kulesi:** 3 → 4 → 5 → 6 halka. 3 yıldız için en az hamle (2^n − 1). Sonraki bölümlerde karışık başlangıç ve farklı hedef direk.

✅ Bu 4 oyun hem Akıl Bahçesi linkine hem de **Ders Bahçesi**'nin Akıl Bahçesi bölümüne eklendi (Ders Bahçesi linki: https://claude.ai/artifact/W2hwKHmJX7xmV5pv5S8Eaj). Veli kızının iPad'inde **Ders Bahçesi**'ni kullanıyor; bundan sonraki değişiklikler öncelikle ders-bahcesi.html'e yapılmalı.

## Sıradaki adımlar

0. ✅ YAPILDI: Akıl Bahçesi'ne 4 yeni oyun (Labirent, Robot Yolu, Terazi, Hanoi Kulesi) eklendi ve aynı linke yayınlandı. Toplam 9 oyun.
1. Veli "başla" deyince: tek dosyalık **Ders Bahçesi** uygulamasını yap (4 ders + Akıl Bahçesi + sesli okuma + iPad uyumu).
2. Test et, commit ve push yap, Claude Artifact olarak yayınla, linki veliye gönder.
3. Veli beğenince: GitHub'da herkese açık `ders-bahcesi` deposu, `index.html` ve Pages ayarı (adım adım). Ardından iPad'de Ana Ekrana Ekle.
