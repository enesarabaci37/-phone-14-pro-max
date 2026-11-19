const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{
  const D=path.join(__dirname,'ilk9'); const dirs=fs.readdirSync(D).filter(d=>fs.statSync(path.join(D,d)).isDirectory()).sort();
  const groups=process.argv[2]?process.argv[2].split(','):null;
  const b=await chromium.launch();
  const sel=dirs.filter(d=>!groups||groups.includes(d[0]));
  const html=`<html><body style="margin:0;background:#ccc;font-family:Inter">${sel.map(d=>{const f=fs.readdirSync(path.join(D,d)).sort((a,b)=>parseInt(a.match(/\d+/))-parseInt(b.match(/\d+/)));return `<div style="padding:10px"><b>${d}</b><div style="display:flex;gap:8px">${f.map(x=>`<img src="${path.join(D,d,x)}" width="300">`).join('')}</div></div>`}).join('')}</body></html>`;
  fs.writeFileSync('/tmp/claude-0/-home-user--phone-14-pro-max/0241c643-6ade-52e9-acc7-41e4a2409655/scratchpad/contact.html',html);
  const p=await b.newPage({viewport:{width:2200,height:800}});
  await p.goto('file:///tmp/claude-0/-home-user--phone-14-pro-max/0241c643-6ade-52e9-acc7-41e4a2409655/scratchpad/contact.html'); await p.waitForTimeout(800);
  await p.screenshot({path:'/tmp/claude-0/-home-user--phone-14-pro-max/0241c643-6ade-52e9-acc7-41e4a2409655/scratchpad/contact_'+(process.argv[2]||'all').replace(/,/g,'')+'.png',fullPage:true});
  await b.close();
})();
