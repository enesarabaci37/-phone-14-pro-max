const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const FILE = {
  tree_of_life: 'Anatolian_Kilim_Tree_of_Life_Cross_Stitch_Pattern.pdf',
  elibelinde: 'Anatolian_Kilim_Elibelinde_Cross_Stitch_Pattern.pdf',
  bereket: 'Anatolian_Kilim_Bereket_Cross_Stitch_Pattern.pdf',
  mini_nazar: 'Mini_Nazar_Evil_Eye_Cross_Stitch_Set.pdf',
};
(async () => {
  const b = await chromium.launch();
  for (const slug of Object.keys(FILE)) {
    const OUT = path.join(__dirname, 'out', slug);
    fs.mkdirSync(OUT, { recursive: true });
    const p = await b.newPage({ viewport: { width: 900, height: 1300 }, deviceScaleFactor: 1.5 });
    await p.goto('file://' + path.join(__dirname, 'pattern2.html') + '#' + slug);
    await p.waitForSelector('body[data-ready="1"]');
    await p.waitForTimeout(400);
    await p.pdf({ path: path.join(OUT, FILE[slug]), format: 'A4', printBackground: true, preferCSSPageSize: true });
    const pages = await p.$$('.page');
    for (let i = 0; i < pages.length; i++) await pages[i].screenshot({ path: path.join(OUT, 'page_' + (i + 1) + '.png') });
    await p.close();
    const q = await b.newPage({ viewport: { width: 2100, height: 1700 } });
    await q.goto('file://' + path.join(__dirname, 'listing2.html') + '#' + slug);
    await q.waitForSelector('body[data-ready="1"]');
    await q.waitForTimeout(400);
    await (await q.$('#m1')).screenshot({ path: path.join(OUT, 'etsy_gorsel_1_kapak.png') });
    await (await q.$('#m2')).screenshot({ path: path.join(OUT, 'etsy_gorsel_2_icerik.png') });
    await q.close();
    console.log('done', slug);
  }
  await b.close();
})();
