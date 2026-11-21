// GTA 6 gönderisini PNG'ye, Reels'i kare kare PNG'ye çevirir (ffmpeg ile birleştirilir).
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const dir = __dirname;
  const out = process.argv[2];
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();

  const p1 = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (let i = 1; i <= 5; i++) {
    await p1.goto('file://' + path.join(dir, `slide-${i}.html`), { waitUntil: 'load' });
    await p1.evaluate(() => document.fonts.ready);
    await p1.screenshot({ path: path.join(out, `gta6-gonderi-${i}-1080x1350.png`) });
  }

  const fps = 30, dur = 18;
  const frames = path.join(dir, 'frames');
  fs.mkdirSync(frames, { recursive: true });
  const p2 = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  await p2.goto('file://' + path.join(dir, 'reels.html'), { waitUntil: 'load' });
  await p2.evaluate(() => document.fonts.ready);
  for (let f = 0; f < fps * dur; f++) {
    await p2.evaluate((t) => window.render(t), f / fps);
    await p2.screenshot({ path: path.join(frames, `f${String(f).padStart(4, '0')}.jpg`), type: 'jpeg', quality: 94 });
  }
  await p2.evaluate(() => window.render(2.6));
  await p2.screenshot({ path: path.join(out, 'gta6-reels-kapak-1080x1920.png') });
  await browser.close();
})();
