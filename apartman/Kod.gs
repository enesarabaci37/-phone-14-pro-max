/**
 * Apartman Yönetimi - Google Apps Script sunucu kodu.
 *
 * Veriler bu betiğin bağlı olduğu Google E-Tablo'da, her tablo ayrı bir sayfada tutulur.
 * Sayfa.html arayüzü bu fonksiyonları google.script.run ile çağırır.
 * Kurulum: KURULUM.md
 */

var SURUM = '1.0';
var SIFRE_TUZ = 'apartman-yonetimi::';
var OTURUM_SURESI = 6 * 60 * 60; // saniye

// Tablo adı -> sütunlar. Sayısal sütunlar 'n:' ile, mantıksal sütunlar 'b:' ile başlar.
var TABLOLAR = {
  Daireler: ['id', 'no', 'kat', 'b:aktif', 'baslangic_donem', 'n:ozel_aidat', 'n:pay_orani',
             'ev_sahibi_ad', 'ev_sahibi_tel', 'not'],
  Sakinler: ['id', 'daire_id', 'tip', 'ad', 'tel', 'giris', 'cikis', 'not'],
  AidatTarifesi: ['id', 'baslangic_donem', 'n:tutar', 'aciklama'],
  Borclar: ['id', 'daire_id', 'sakin_id', 'donem', 'tur', 'baslik', 'n:tutar', 'ek_id', 'tarih'],
  Odemeler: ['id', 'daire_id', 'sakin_id', 'tarih', 'n:tutar', 'yontem', 'aciklama'],
  Giderler: ['id', 'tarih', 'donem', 'kategori', 'aciklama', 'n:tutar', 'odeme', 'fis_url', 'duzenli_id'],
  EkToplamalar: ['id', 'tarih', 'donem', 'baslik', 'aciklama', 'n:toplam', 'dagitim', 'daireler'],
  DuzenliGiderler: ['id', 'kategori', 'aciklama', 'n:tutar', 'odeme', 'n:gun', 'b:aktif'],
  Kategoriler: ['id', 'ad'],
  Ayarlar: ['anahtar', 'deger']
};

// ---------------------------------------------------------------- web uygulaması

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Sayfa')
    .setTitle('Apartman Yönetimi')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, maximum-scale=1')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.DEFAULT);
}

// ---------------------------------------------------------------- tablo yardımcıları

function tablo_(ad) {
  var ss = SpreadsheetApp.getActive();
  var sh = ss.getSheetByName(ad);
  if (!sh) {
    sh = ss.insertSheet(ad);
    var basliklar = TABLOLAR[ad].map(sutunAdi_);
    sh.getRange(1, 1, 1, basliklar.length).setValues([basliklar]).setFontWeight('bold');
    sh.setFrozenRows(1);
    sh.getRange('A:Z').setNumberFormat('@');
  }
  return sh;
}

function sutunAdi_(s) { return s.replace(/^[nb]:/, ''); }

function deger_(sutun, v) {
  if (sutun.indexOf('n:') === 0) {
    if (v === '' || v === null || v === undefined) return '';
    var n = Number(String(v).replace(',', '.'));
    return isNaN(n) ? '' : n;
  }
  if (sutun.indexOf('b:') === 0) return v === true || v === 'true' || v === 'TRUE';
  return v === null || v === undefined ? '' : String(v);
}

function oku_(ad) {
  var sh = tablo_(ad);
  var son = sh.getLastRow();
  if (son < 2) return [];
  var sutunlar = TABLOLAR[ad];
  var degerler = sh.getRange(2, 1, son - 1, sutunlar.length).getValues();
  var sonuc = [];
  for (var i = 0; i < degerler.length; i++) {
    if (degerler[i][0] === '' || degerler[i][0] === null) continue;
    var k = {};
    for (var j = 0; j < sutunlar.length; j++) k[sutunAdi_(sutunlar[j])] = deger_(sutunlar[j], degerler[i][j]);
    sonuc.push(k);
  }
  return sonuc;
}

function satir_(ad, kayit) {
  return TABLOLAR[ad].map(function (s) {
    var v = deger_(s, kayit[sutunAdi_(s)]);
    return typeof v === 'boolean' ? String(v) : (typeof v === 'number' ? String(v) : v);
  });
}

function satirBul_(sh, id) {
  var son = sh.getLastRow();
  if (son < 2) return -1;
  var idler = sh.getRange(2, 1, son - 1, 1).getValues();
  for (var i = 0; i < idler.length; i++) if (String(idler[i][0]) === String(id)) return i + 2;
  return -1;
}

function yaz_(ad, kayit) {
  if (!TABLOLAR[ad] || ad === 'Ayarlar') throw new Error('Geçersiz tablo: ' + ad);
  var sh = tablo_(ad);
  if (!kayit.id) kayit.id = Utilities.getUuid().slice(0, 8);
  var satir = satir_(ad, kayit);
  var r = satirBul_(sh, kayit.id);
  if (r === -1) sh.appendRow(satir);
  else sh.getRange(r, 1, 1, satir.length).setValues([satir]);
  var temiz = {};
  TABLOLAR[ad].forEach(function (s) { temiz[sutunAdi_(s)] = deger_(s, kayit[sutunAdi_(s)]); });
  return temiz;
}

function sil_(ad, id) {
  var sh = tablo_(ad);
  var r = satirBul_(sh, id);
  if (r !== -1) sh.deleteRow(r);
}

function ayarlar_() {
  var sonuc = {};
  oku_('Ayarlar').forEach(function (s) { sonuc[s.anahtar] = s.deger; });
  return sonuc;
}

function ayarYaz_(nesne) {
  var sh = tablo_('Ayarlar');
  var mevcut = {};
  var son = sh.getLastRow();
  if (son >= 2) {
    sh.getRange(2, 1, son - 1, 1).getValues().forEach(function (r, i) { mevcut[r[0]] = i + 2; });
  }
  Object.keys(nesne).forEach(function (a) {
    var v = nesne[a] === null || nesne[a] === undefined ? '' : String(nesne[a]);
    if (mevcut[a]) sh.getRange(mevcut[a], 2).setValue(v);
    else { sh.appendRow([a, v]); mevcut[a] = sh.getLastRow(); }
  });
}

// ---------------------------------------------------------------- oturum ve şifre

function ozet_(sifre) {
  var b = Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, SIFRE_TUZ + sifre, Utilities.Charset.UTF_8);
  return b.map(function (x) { return ('0' + (x & 0xff).toString(16)).slice(-2); }).join('');
}

function kontrol_(jeton) {
  if (!jeton || CacheService.getUserCache().get('oturum_' + jeton) !== '1') {
    throw new Error('OTURUM: Oturum süresi doldu, lütfen tekrar giriş yapın.');
  }
  CacheService.getUserCache().put('oturum_' + jeton, '1', OTURUM_SURESI);
}

function yeniOturum_() {
  var j = Utilities.getUuid();
  CacheService.getUserCache().put('oturum_' + j, '1', OTURUM_SURESI);
  return j;
}

function kilitle_(fonk) {
  var kilit = LockService.getScriptLock();
  kilit.waitLock(20000);
  try { return fonk(); } finally { kilit.releaseLock(); }
}

/** Uygulama açılınca: kurulum yapılmış mı? */
function durum() {
  var p = PropertiesService.getScriptProperties();
  return { kurulu: !!p.getProperty('sifre'), surum: SURUM };
}

function giris(sifre) {
  var kayitli = PropertiesService.getScriptProperties().getProperty('sifre');
  if (!kayitli) throw new Error('Kurulum yapılmamış.');
  Utilities.sleep(300);
  if (ozet_(sifre) !== kayitli) throw new Error('Şifre yanlış.');
  return yeniOturum_();
}

/** İlk kurulum: şifre, ayarlar, aidat tutarı ve daireler. */
function kurulumYap(v) {
  return kilitle_(function () {
    var p = PropertiesService.getScriptProperties();
    if (p.getProperty('sifre')) throw new Error('Kurulum zaten yapılmış.');
    if (!v.sifre || String(v.sifre).length < 4) throw new Error('Şifre en az 4 karakter olmalı.');
    Object.keys(TABLOLAR).forEach(tablo_);
    var ilk = SpreadsheetApp.getActive().getSheetByName('Sayfa1') || SpreadsheetApp.getActive().getSheetByName('Sheet1');
    if (ilk && SpreadsheetApp.getActive().getSheets().length > 1) SpreadsheetApp.getActive().deleteSheet(ilk);
    ayarYaz_({
      apartman_adi: v.apartman_adi || 'Apartman', adres: v.adres || '', yonetici_ad: v.yonetici_ad || '',
      yonetici_tel: v.yonetici_tel || '', iban: v.iban || '', iban_ad: v.iban_ad || '',
      baslangic_donem: v.baslangic_donem, son_odeme_gunu: v.son_odeme_gunu || '10',
      acilis_banka: '0', acilis_nakit: '0', rapor_borc_tablosu: 'true'
    });
    yaz_('AidatTarifesi', { baslangic_donem: v.baslangic_donem, tutar: v.aidat, aciklama: 'İlk aidat' });
    var n = Math.max(1, Math.min(200, Number(v.daire_sayisi) || 8));
    for (var i = 1; i <= n; i++) {
      yaz_('Daireler', { no: String(i), aktif: true, baslangic_donem: v.baslangic_donem, pay_orani: 1 });
    }
    ['Temizlikçi', 'Asansör bakımı', 'Asansör tamiri', 'Ortak elektrik', 'Ortak su', 'Temizlik malzemesi',
     'Tamirat', 'Diğer'].forEach(function (k) { yaz_('Kategoriler', { ad: k }); });
    p.setProperty('sifre', ozet_(v.sifre));
    return yeniOturum_();
  });
}

function sifreDegistir(jeton, eski, yeni) {
  kontrol_(jeton);
  var p = PropertiesService.getScriptProperties();
  if (ozet_(eski) !== p.getProperty('sifre')) throw new Error('Mevcut şifre yanlış.');
  if (!yeni || String(yeni).length < 4) throw new Error('Yeni şifre en az 4 karakter olmalı.');
  p.setProperty('sifre', ozet_(yeni));
  return true;
}

// ---------------------------------------------------------------- veri işlemleri

/** Bütün tabloları ve ayarları döner. */
function hepsiniGetir(jeton) {
  kontrol_(jeton);
  var sonuc = { ayarlar: ayarlar_(), surum: SURUM, tablo_adresi: SpreadsheetApp.getActive().getUrl() };
  Object.keys(TABLOLAR).forEach(function (t) { if (t !== 'Ayarlar') sonuc[t] = oku_(t); });
  return sonuc;
}

/**
 * Birden fazla kayıt işlemini tek seferde yapar.
 * islemler: [{tablo, kayit}] (ekle / güncelle) ya da [{tablo, sil: id}]
 */
function islemYap(jeton, islemler) {
  kontrol_(jeton);
  return kilitle_(function () {
    return islemler.map(function (i) {
      if (i.sil) { sil_(i.tablo, i.sil); return { tablo: i.tablo, silindi: i.sil }; }
      return { tablo: i.tablo, kayit: yaz_(i.tablo, i.kayit) };
    });
  });
}

function ayarKaydet(jeton, nesne) {
  kontrol_(jeton);
  return kilitle_(function () { ayarYaz_(nesne); return ayarlar_(); });
}

// ---------------------------------------------------------------- dosyalar

function klasor_(ad) {
  var dosya = DriveApp.getFileById(SpreadsheetApp.getActive().getId());
  var ust = dosya.getParents().hasNext() ? dosya.getParents().next() : DriveApp.getRootFolder();
  var it = ust.getFoldersByName('Apartman Yönetimi');
  var ana = it.hasNext() ? it.next() : ust.createFolder('Apartman Yönetimi');
  var it2 = ana.getFoldersByName(ad);
  return it2.hasNext() ? it2.next() : ana.createFolder(ad);
}

/** HTML raporu PDF'e çevirip Drive'a kaydeder, bağlantısını döner. */
function pdfOlustur(jeton, html, dosyaAdi) {
  kontrol_(jeton);
  var blob = Utilities.newBlob(html, 'text/html', 'rapor.html').getAs('application/pdf').setName(dosyaAdi + '.pdf');
  var f = klasor_('Raporlar').createFile(blob);
  return { url: f.getUrl(), indir: 'https://drive.google.com/uc?export=download&id=' + f.getId(), ad: f.getName() };
}

/** Fiş / fatura fotoğrafını Drive'a kaydeder. */
function dosyaYukle(jeton, base64, ad, tur) {
  kontrol_(jeton);
  var blob = Utilities.newBlob(Utilities.base64Decode(base64), tur || 'image/jpeg', ad || 'fis.jpg');
  var f = klasor_('Fişler').createFile(blob);
  return f.getUrl();
}
