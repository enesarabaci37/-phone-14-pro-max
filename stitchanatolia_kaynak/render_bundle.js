const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const OUT = path.join(__dirname, 'bundle_out');
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2100, height: 1800 } });
  await p.goto('file://' + path.join(__dirname, 'bundle.html'));
  await p.waitForSelector('body[data-ready="1"]', { timeout: 60000 });
  await p.waitForTimeout(500);
  await (await p.$('#e1')).screenshot({ path: path.join(OUT, 'etsy_gorsel_1_kapak.png') });
  await (await p.$('#e2')).screenshot({ path: path.join(OUT, 'etsy_gorsel_2_icerik.png') });
  await (await p.$('#pin')).screenshot({ path: path.join(OUT, 'pin_bundle_dikey.png') });
  await (await p.$('#p_cover')).screenshot({ path: path.join(OUT, '_prev_cover.png') });
  await (await p.$('#p_contents')).screenshot({ path: path.join(OUT, '_prev_contents.png') });
  // pdf with only the two A4 pages
  await p.evaluate(() => { document.querySelectorAll('.img,.pin').forEach(e => e.remove()); document.body.style.background = '#fff'; });
  await p.pdf({ path: path.join(OUT, '_front.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
