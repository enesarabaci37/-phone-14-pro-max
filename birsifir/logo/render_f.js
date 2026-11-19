const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 1200 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, 'family.html'));
  await p.waitForSelector('body[data-ready="1"]');
  await p.waitForTimeout(400);
  await (await p.$('#sheet')).screenshot({ path: path.join(__dirname, 'birsifir_renk_ailesi.png') });
  await b.close();
})();
