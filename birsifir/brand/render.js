const { chromium } = require('playwright');
const path = require('path');
const out = (n) => path.join(__dirname, 'out', n);
(async () => {
  require('fs').mkdirSync(path.join(__dirname, 'out'), { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1800, height: 2000 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'templates.html'));
  await p.waitForSelector('body[data-ready="1"]');
  await p.waitForTimeout(300);
  const map = {
    t1: '01_carousel_kapak.png', t2: '02_carousel_ic_sayfa.png', t3: '03_carousel_son_sayfa.png',
    t4: '04_uyari_gonderisi.png', t5: '05_reels_kapak.png', t6: '06_story.png',
    l1: 'logo_acik_zemin.png', l2: 'logo_koyu_zemin.png',
  };
  for (const [id, name] of Object.entries(map)) await (await p.$('#' + id)).screenshot({ path: out(name) });
  await (await p.$('#p1')).screenshot({ path: out('profil_fotografi.png'), omitBackground: true });
  // overview sheet
  const q = await b.newPage({ viewport: { width: 1800, height: 1400 } });
  const f = (n) => 'file://' + out(n);
  require('fs').writeFileSync(path.join(__dirname,'out','overview.html'),`<html><head><style>
    body{margin:0;background:#E9EBEF;font-family:Inter,sans-serif;color:#0B0F1A}
    .s{width:1800px;padding:56px}
    h1{font-family:'Inter Display';font-weight:800;font-size:46px;letter-spacing:-.02em;margin:0 0 6px}
    p{margin:0 0 34px;color:#6B7280;font-size:20px}
    .r{display:flex;gap:26px;align-items:flex-end;margin-bottom:34px}
    figure{margin:0;display:flex;flex-direction:column;gap:10px}
    img{display:block;border-radius:14px;box-shadow:0 6px 24px rgba(11,15,26,.12)}
    figcaption{font-size:16px;font-weight:600;color:#1F2633}
  </style></head><body><div class="s" id="s">
    <h1>Birsıfır Teknoloji · Marka Şablonları</h1>
    <p>Elektrik mavisi #0A5CFF · Vurgu sarısı #FFC300 · Yazı tipi: Inter</p>
    <div class="r">
      <figure><img src="${f('01_carousel_kapak.png')}" width="300"><figcaption>1 · Kaydırmalı gönderi kapağı</figcaption></figure>
      <figure><img src="${f('02_carousel_ic_sayfa.png')}" width="300"><figcaption>2 · İç sayfa (adım adım)</figcaption></figure>
      <figure><img src="${f('03_carousel_son_sayfa.png')}" width="300"><figcaption>3 · Son sayfa (kaydet/takip)</figcaption></figure>
      <figure><img src="${f('04_uyari_gonderisi.png')}" width="300"><figcaption>4 · Sarı vurgulu uyarı</figcaption></figure>
      <figure><img src="${f('05_reels_kapak.png')}" width="222"><figcaption>5 · Reels kapağı</figcaption></figure>
    </div>
    <div class="r">
      <figure><img src="${f('06_story.png')}" width="222"><figcaption>6 · Story (anket)</figcaption></figure>
      <figure><img src="${f('logo_acik_zemin.png')}" width="560"><figcaption>Logo · açık zemin</figcaption></figure>
      <figure><img src="${f('logo_koyu_zemin.png')}" width="560"><figcaption>Logo · koyu zemin</figcaption></figure>
      <figure><img src="${f('profil_fotografi.png')}" width="200"><figcaption>Profil fotoğrafı</figcaption></figure>
    </div>
  </div></body></html>`);
  await q.goto('file://'+path.join(__dirname,'out','overview.html'));
  await q.waitForTimeout(800);
  await (await q.$('#s')).screenshot({ path: out('00_genel_bakis.png') });
  await b.close();
})();
