// Kullanım: node render_reels.js <html> <süre_sn> <kare_klasörü> <kapak_zamanı> <kapak.png>
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [html, dur, frames, coverT, coverOut] = process.argv.slice(2);
  const fps = 30;
  fs.rmSync(frames, { recursive: true, force: true });
  fs.mkdirSync(frames, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.resolve(html), { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const n = Math.round(parseFloat(dur) * fps);
  for (let f = 0; f < n; f++) {
    await page.evaluate((t) => window.render(t), f / fps);
    await page.screenshot({ path: path.join(frames, `f${String(f).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 94 });
  }
  await page.evaluate((t) => window.render(t), parseFloat(coverT));
  await page.screenshot({ path: coverOut });
  await browser.close();
  console.log('kare:', n);
})();
