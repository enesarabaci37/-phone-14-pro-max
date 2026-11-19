const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
(async () => {
  const slugs = ['tree_of_life', 'elibelinde', 'bereket', 'mini_nazar'];
  let html = '<html><body style="margin:0;background:#ddd;display:flex;gap:20px;padding:20px;align-items:flex-start">';
  for (const s of slugs) {
    const js = fs.readFileSync(path.join(__dirname, 'designs', s, 'pattern.js'), 'utf8').replace(/^const P=/, '').replace(/;$/, '');
    const P = JSON.parse(js);
    const c = 7;
    let svg = `<svg width="${P.W * c}" height="${P.H * c}" style="background:#F4EEE2">`;
    for (let y = 0; y < P.H; y++) for (let x = 0; x < P.W; x++) { const k = P.grid[y][x]; if (k) svg += `<rect x="${x * c}" y="${y * c}" width="${c}" height="${c}" fill="${P.colors[k].hex}"/>`; }
    html += `<div><div style="font:bold 16px sans-serif">${s}</div>${svg}</svg></div>`;
  }
  html += '</body></html>';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1900, height: 700 } });
  await p.setContent(html);
  await p.screenshot({ path: path.join(__dirname, 'out', 'onizleme_4_desen.png'), fullPage: true });
  await b.close();
})();
