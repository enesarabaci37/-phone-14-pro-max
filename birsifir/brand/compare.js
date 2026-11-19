const { chromium } = require('playwright');
const path = require('path'); const fs=require('fs');
const out = (n) => path.join(__dirname, 'out', n);
(async () => {
  const b = await chromium.launch();
  for (const [mode, suffix] of [['mode-a','A'],['mode-b','B']]) {
    const p = await b.newPage({ viewport: { width: 1800, height: 2000 } });
    await p.goto('file://' + path.join(__dirname, 'templates.html') + '#' + mode);
    await p.waitForSelector('body[data-ready="1"]'); await p.waitForTimeout(300);
    for (const id of ['t1','t2']) await (await p.$('#'+id)).screenshot({ path: out(`cmp_${id}_${suffix}.png`) });
    await p.close();
  }
  fs.writeFileSync(out('cmp.html'), `<html><body style="margin:0;background:#E9EBEF;font-family:Inter"><div id="s" style="width:1760px;padding:56px">
  <h1 style="font-family:'Inter Display';font-size:44px;margin:0 0 8px;letter-spacing:-.02em">Koruma: hangisi?</h1>
  <p style="color:#6B7280;font-size:20px;margin:0 0 30px">Aynı iki gönderi, iki farklı filigran yöntemiyle</p>
  <div style="display:flex;gap:60px">
   <div><div style="font-weight:800;font-size:26px;margin-bottom:6px">A · Ortada büyük filigran</div><div style="color:#6B7280;font-size:18px;margin-bottom:16px">İçeriğin üstünde, yarı saydam</div>
     <div style="display:flex;gap:18px"><img src="cmp_t1_A.png" width="380" style="border-radius:12px"><img src="cmp_t2_A.png" width="380" style="border-radius:12px"></div></div>
   <div><div style="font-weight:800;font-size:26px;margin-bottom:6px;color:#0A5CFF">B · Kesik köşe + yan imza (önerilen)</div><div style="color:#6B7280;font-size:18px;margin-bottom:16px">Sağ altta taşan simge, sağ kenarda dikey kullanıcı adı, altta şerit</div>
     <div style="display:flex;gap:18px"><img src="cmp_t1_B.png" width="380" style="border-radius:12px"><img src="cmp_t2_B.png" width="380" style="border-radius:12px"></div></div>
  </div></div></body></html>`);
  const q = await b.newPage({ viewport: { width: 1800, height: 1200 } });
  await q.goto('file://' + out('cmp.html')); await q.waitForTimeout(600);
  await (await q.$('#s')).screenshot({ path: out('koruma_karsilastirma.png') });
  await b.close();
})();
