const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{ const slug=process.argv[2]; const D=path.join(__dirname,'video_out');
 const imgs=[0.2,2,4,6.5,8.5,11].map(s=>`<img src="${path.join(D,`prev_${slug}_${s}.jpg`)}" width="420">`).join('');
 const f=path.join(D,'_s.html'); fs.writeFileSync(f,`<html><body style="margin:0;background:#333;display:grid;grid-template-columns:repeat(3,420px);gap:6px;padding:6px">${imgs}</body></html>`);
 const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1290,height:870}}); await p.goto('file://'+f); await p.waitForTimeout(500);
 await p.screenshot({path:path.join(D,`sheet_${slug}.png`),fullPage:true}); await b.close(); fs.unlinkSync(f); })();
