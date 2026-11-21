const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { execFileSync } = require('child_process');
const NAMES = { nazar: '1_Nazar_Madalyonu', tree_of_life: '2_Hayat_Agaci', elibelinde: '3_Elibelinde', bereket: '4_Bereket', mini_nazar: '5_Mini_Nazar_Seti', goz_seti: '7_Goz_Seti', kurt_agzi: '8_Kurt_Agzi', yildiz: '9_Yildiz', noel_susleri: '10_Noel_Susleri', noel_agaci: '11_Noel_Agaci' };
const only = process.argv[2];
const previewOnly = process.argv[3] === 'preview';
(async () => {
  const b = await chromium.launch();
  for (const slug of Object.keys(NAMES)) {
    if (only && only !== 'all' && slug !== only) continue;
    const p = await b.newPage({ viewport: { width: 1080, height: 1080 } });
    await p.goto('file://' + path.join(__dirname, 'video.html') + '#' + slug);
    await p.waitForSelector('body[data-ready="1"]', { timeout: 60000 });
    const OUT = path.join(__dirname, 'video_out');
    fs.mkdirSync(OUT, { recursive: true });
    if (previewOnly) {
      for (const sec of [0.2, 2, 4, 6.5, 8.5, 11]) {
        const data = await p.evaluate((f) => { drawFrame(f); return document.getElementById('c').toDataURL('image/jpeg', 0.9); }, Math.round(sec * 30));
        fs.writeFileSync(path.join(OUT, `prev_${slug}_${sec}.jpg`), Buffer.from(data.split(',')[1], 'base64'));
      }
      await p.close(); continue;
    }
    const FR = path.join(OUT, 'frames_' + slug);
    fs.mkdirSync(FR, { recursive: true });
    for (let f = 0; f < 360; f++) {
      const data = await p.evaluate((f) => { drawFrame(f); return document.getElementById('c').toDataURL('image/jpeg', 0.94); }, f);
      fs.writeFileSync(path.join(FR, String(f).padStart(4, '0') + '.jpg'), Buffer.from(data.split(',')[1], 'base64'));
    }
    await p.close();
    const mp4 = path.join(OUT, `${NAMES[slug]}_video.mp4`);
    execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-framerate', '30', '-i', path.join(FR, '%04d.jpg'), '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-preset', 'medium', '-movflags', '+faststart', mp4]);
    for (const f of fs.readdirSync(FR)) fs.unlinkSync(path.join(FR, f));
    fs.rmdirSync(FR);
    console.log('done', slug, (fs.statSync(mp4).size / 1e6).toFixed(1) + ' MB');
  }
  await b.close();
})();
