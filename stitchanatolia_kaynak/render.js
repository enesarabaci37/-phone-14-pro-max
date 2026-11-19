const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const OUT = path.join(__dirname, 'out');
  fs.mkdirSync(OUT, { recursive: true });
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 900, height: 1300 }, deviceScaleFactor: 1.5 });
  await p.goto('file://' + path.join(__dirname, 'pattern.html'));
  await p.waitForSelector('body[data-ready="1"]');
  await p.waitForTimeout(500);
  await p.pdf({ path: path.join(OUT, 'Anatolian_Kilim_Nazar_Cross_Stitch_Pattern.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true });
  const pages = await p.$$('.page');
  for (let i = 0; i < pages.length; i++) await pages[i].screenshot({ path: path.join(OUT, 'page_' + (i + 1) + '.png') });
  await b.close();
})();
