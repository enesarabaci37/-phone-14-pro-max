const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const OUT = path.join(__dirname, 'pins');
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2000, height: 1600 } });
  await p.goto('file://' + path.join(__dirname, 'pins.html'));
  await p.waitForSelector('body[data-ready="1"]', { timeout: 60000 });
  await p.waitForTimeout(500);
  const ids = await p.$$eval('.pin', els => els.map(e => e.id));
  await (await p.$('#pin_cover')).screenshot({ path: path.join(OUT, 'pinterest_kapak_1920x1080.png') });
  for (const id of ids) await (await p.$('#' + id)).screenshot({ path: path.join(OUT, id + '.png') });
  // overview
  const html = '<html><body style="margin:0;background:#333;display:grid;grid-template-columns:repeat(6,250px);gap:8px;padding:8px">' +
    ids.map(i => `<img src="${path.join(OUT, i + '.png')}" width="250">`).join('') + '</body></html>';
  const f = path.join(OUT, '_o.html'); fs.writeFileSync(f, html);
  const q = await b.newPage({ viewport: { width: 1560, height: 800 } });
  await q.goto('file://' + f); await q.waitForTimeout(800);
  await q.screenshot({ path: path.join(OUT, '_overview.png'), fullPage: true });
  fs.unlinkSync(f);
  await b.close();
  console.log(ids.join(' '));
})();
