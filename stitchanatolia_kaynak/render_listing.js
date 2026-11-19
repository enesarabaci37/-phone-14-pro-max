const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 2100, height: 1700 } });
  await p.goto('file://' + path.join(__dirname, 'listing.html'));
  await p.waitForSelector('body[data-ready="1"]');
  await p.waitForTimeout(500);
  await (await p.$('#m1')).screenshot({ path: path.join(__dirname, 'out', 'etsy_gorsel_1_kapak.png') });
  await (await p.$('#m2')).screenshot({ path: path.join(__dirname, 'out', 'etsy_gorsel_2_icerik.png') });
  await b.close();
})();
