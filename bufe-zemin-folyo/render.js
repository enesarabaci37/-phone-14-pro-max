const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const b = await chromium.launch();
  const url = 'file://' + path.resolve(__dirname, 'zemin_folyo.html');
  const mm = 96 / 25.4, W = Math.round(1020 * mm), H = Math.round(4020 * mm);
  // Vektör PDF (gerçek ölçü)
  let p = await b.newPage();
  await p.goto(url, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
  await p.pdf({ path: 'zemin_folyo_102x402cm_PRINT.pdf', width: '1020mm', height: '4020mm', printBackground: true, pageRanges: '1' });
  await p.close();
  for (const [name, dsf] of [['onizleme.png', 0.12], ['zemin_folyo_100dpi.png', 100/96]]) {
    const ctx = await b.newContext({ viewport: { width: W, height: H }, deviceScaleFactor: dsf });
    p = await ctx.newPage(); await p.goto(url, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
    await p.waitForTimeout(500);
    await p.screenshot({ path: name, fullPage: false }); await ctx.close();
  }
  await b.close();
})();
