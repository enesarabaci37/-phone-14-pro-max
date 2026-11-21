// Yazı/grafik katmanını şeffaf PNG kareler olarak çeker (arka plan videosu ffmpeg ile alta konur).
// Kullanım: node render_overlay.js reels.html <süre_sn> <kare_klasörü> [t1 t2 ...  (sadece bu anlar)]
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [html, dur, frames, ...only] = process.argv.slice(2);
  const fps = 30;
  fs.mkdirSync(frames, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on('pageerror', e => console.log('ERR', e.message));
  await page.goto('file://' + path.resolve(html) + '#overlay', { waitUntil: 'load' });
  await page.evaluate(() => document.fonts.ready);
  const list = only.length ? only.map(t => Math.round(+t * fps)) : [...Array(Math.round(+dur * fps)).keys()];
  for (const f of list) {
    await page.evaluate((t) => window.render(t), f / fps);
    await page.screenshot({ path: path.join(frames, `o${String(f).padStart(4, '0')}.png`), omitBackground: true });
  }
  await browser.close();
  console.log('kare:', list.length);
})();
