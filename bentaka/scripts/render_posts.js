// Tuvaldeki gönderi şablonlarını (dc.html) 1080x1350 PNG'ye çevirir.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [srcDir, outDir, tmpDir] = process.argv.slice(2);
  fs.mkdirSync(tmpDir, { recursive: true });
  const groups = { Haber: 'Haber', Kiyas: 'Kiyas', Alinti: 'Alinti' };
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  for (const f of fs.readdirSync(srcDir).filter((n) => n.endsWith('.dc.html')).sort()) {
    let html = fs.readFileSync(path.join(srcDir, f), 'utf8');
    html = html
      .replace('<script src="./support.js"></script>', '')
      .replace(/<\/?x-dc>/g, '')
      .replace(/<\/?helmet>/g, '')
      .replace(/<script type="text\/x-dc"[\s\S]*?<\/script>/, '');
    const tmp = path.join(tmpDir, f.replace('.dc.html', '.html'));
    fs.writeFileSync(tmp, html);
    await page.goto('file://' + tmp, { waitUntil: 'networkidle' });
    await page.evaluate(() => document.fonts.ready);
    const stem = f.replace('.dc.html', '');
    const group = groups[stem.split('-')[0]];
    const dir = path.join(outDir, group);
    fs.mkdirSync(dir, { recursive: true });
    const out = path.join(dir, `bentaka-${stem.toLowerCase()}-1080x1350.png`);
    await page.screenshot({ path: out, clip: { x: 0, y: 0, width: 1080, height: 1350 } });
    console.log(out);
  }
  await browser.close();
})();
