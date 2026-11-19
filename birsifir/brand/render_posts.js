const { chromium } = require('playwright');
const path = require('path'); const fs = require('fs');
(async () => {
  const OUT = path.join(__dirname, 'ilk9');
  fs.rmSync(OUT, { recursive: true, force: true }); fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 1500 } });
  await p.goto('file://' + path.join(__dirname, 'posts.html'));
  await p.waitForSelector('body[data-ready="1"]'); await p.waitForTimeout(400);
  const ids = await p.$$eval('.tpl', els => els.map(e => [e.id, e.dataset.post]));
  const names = { p1: '1_tanisma', p2: '2_whatsapp_5_ozellik', p3: '3_uyari_kargo_sms', p4: '4_pil_5_ayar', p5: '5_uyari_banka_aramasi', p6: '6_yapay_zeka_nedir', p7: '7_telefon_yavasladi', p8: '8_yapay_zeka_cv', p9: '9_guclu_sifre' };
  for (const [id, post] of ids) {
    const dir = path.join(OUT, names[post]); fs.mkdirSync(dir, { recursive: true });
    const slide = id.split('_')[1];
    await (await p.$('#' + id)).screenshot({ path: path.join(dir, `sayfa_${slide}.png`) });
  }
  // grid preview (profile: newest top-left => 9,8,7 / 6,5,4 / 3,2,1), 3:4 crop like Instagram grid
  const order = ['p9','p8','p7','p6','p5','p4','p3','p2','p1'];
  const cells = order.map(k => `<div class="c"><img src="${path.join(OUT, names[k], 'sayfa_1.png')}"><span>${names[k].split('_')[0]}</span></div>`).join('');
  const prof = path.join(__dirname, 'out', 'profil_fotografi.png');
  fs.writeFileSync(path.join(OUT, '_grid.html'), `<html><body style="margin:0;background:#fff;font-family:Inter">
  <div id="s" style="width:1080px;padding:40px 0 0">
   <div style="display:flex;align-items:center;gap:40px;padding:0 40px 30px">
     <img src="${prof}" width="170" height="170">
     <div style="flex:1"><div style="font-weight:700;font-size:30px">birsifirteknoloji</div>
     <div style="display:flex;gap:46px;margin-top:14px;font-size:24px"><div><b>9</b> gönderi</div><div><b>0</b> takipçi</div><div><b>0</b> takip</div></div></div>
   </div>
   <div style="padding:0 40px 26px;font-size:24px;line-height:1.45"><b>Birsıfır | Teknoloji</b><br><span style="color:#6B7280">Bilim ve teknoloji</span><br>Teknolojiyi herkesin anlayacağı dille anlatıyoruz 📱<br>Her gün 1 ipucu · Yapay zekâ · Dolandırıcılık uyarıları ⚠️<br>Kaydet, ailene gönder 👇</div>
   <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:4px">${cells}</div></div>
   <style>.c{position:relative;aspect-ratio:3/4;overflow:hidden}.c img{width:100%;height:100%;object-fit:cover}.c span{position:absolute;left:10px;top:10px;background:rgba(0,0,0,.6);color:#fff;font-weight:700;font-size:20px;border-radius:8px;padding:2px 10px}</style>
  </body></html>`);
  const q = await b.newPage({ viewport: { width: 1080, height: 1800 } });
  await q.goto('file://' + path.join(OUT, '_grid.html')); await q.waitForTimeout(700);
  await (await q.$('#s')).screenshot({ path: path.join(OUT, '00_profil_onizleme.png') });
  fs.rmSync(path.join(OUT, '_grid.html'));
  await b.close();
})();
