const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
(async()=>{
  const OUT=path.join(__dirname,'kisa_kisa'); fs.mkdirSync(OUT,{recursive:true});
  const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1200,height:1500}});
  await p.goto('file://'+path.join(__dirname,'news.html')); await p.waitForSelector('body[data-ready="1"]'); await p.waitForTimeout(300);
  const names={n1:'haber_1_gta6.png',n2:'haber_2_nvidia.png',n3:'haber_3_voyager.png'};
  for(const [id,n] of Object.entries(names)) await (await p.$('#'+id)).screenshot({path:path.join(OUT,n)});
  await b.close();
})();
