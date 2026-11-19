const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 3500, height: 2400 } });
  await p.goto('file://' + path.join(__dirname, 'brand.html'));
  await p.waitForSelector('body[data-ready="1"]');
  await p.waitForTimeout(400);
  const o = (n) => path.join(__dirname, 'out', n);
  await (await p.$('#icon')).screenshot({ path: o('magaza_logosu_1000x1000.png') });
  await (await p.$('#banner')).screenshot({ path: o('magaza_kapak_buyuk_3360x840.png') });
  await (await p.$('#mini')).screenshot({ path: o('magaza_kapak_mini_1200x300.png') });
  await b.close();
})();
