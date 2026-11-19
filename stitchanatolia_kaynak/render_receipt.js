const { chromium } = require('playwright'); const path = require('path');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 900, height: 300 } });
 await p.goto('file://' + path.join(__dirname, 'receipt.html')); await p.waitForSelector('body[data-ready="1"]'); await p.waitForTimeout(300);
 await (await p.$('#b')).screenshot({ path: path.join(__dirname, 'out', 'makbuz_seridi_760x100.png') }); await b.close(); })();
