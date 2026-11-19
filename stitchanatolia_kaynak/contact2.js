const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const which = process.argv[2] || 'etsy_gorsel_1_kapak.png';
  const out = process.argv[3] || 'ozet_kapaklar.png';
  const slugs = ['tree_of_life', 'elibelinde', 'bereket', 'mini_nazar'];
  const html = '<html><body style="margin:0;background:#bbb;display:grid;grid-template-columns:1fr 1fr;gap:10px;padding:10px">' +
    slugs.map(s => `<img src="${path.join(__dirname, 'out', s, which)}" style="width:100%">`).join('') + '</body></html>';
  const f = path.join(__dirname, 'out', '_c.html');
  fs.writeFileSync(f, html);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1600, height: 900 } });
  await p.goto('file://' + f);
  await p.waitForTimeout(800);
  await p.screenshot({ path: path.join(__dirname, 'out', out), fullPage: true });
  await b.close();
  fs.unlinkSync(f);
})();
