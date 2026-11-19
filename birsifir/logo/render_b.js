const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const dir = __dirname;
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 1400 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(dir, 'birsifir_logos.html'));
  await p.waitForSelector('body[data-ready="1"]', { timeout: 30000 });
  await p.waitForTimeout(500);
  await (await p.$('#sheet')).screenshot({ path: path.join(dir, 'birsifir_logo_taslaklari.png') });
  // individual avatars at 1080
  for (const n of [1, 2, 3]) {
    const svg = await p.$eval('#av' + n, e => e.outerHTML.replace(/width="260" height="260"/, 'width="1080" height="1080"'));
    const q = await b.newPage({ viewport: { width: 1080, height: 1080 } });
    await q.setContent(`<html><body style="margin:0;background:transparent">${svg}</body></html>`);
    await q.addStyleTag({ url: 'https://fonts.googleapis.com/css2?family=Sora:wght@800&family=Orbitron:wght@900&display=block' });
    await q.evaluate(() => document.fonts.ready);
    await q.waitForTimeout(400);
    await q.screenshot({ path: path.join(dir, `birsifir_profil_${n}.png`), omitBackground: true });
    await q.close();
  }
  await b.close();
})();
