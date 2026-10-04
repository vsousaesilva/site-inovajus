import { chromium } from 'playwright-core';
const times=process.argv.slice(2).map(Number);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:1});
p.on('console',m=>console.log('console',m.text())); p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+process.cwd()+'/scene.html'); await p.evaluate(()=>window.ready);
for(const t of times){await p.evaluate(t=>render(t),t); await p.screenshot({path:`stills/s_${t}.jpg`,type:'jpeg',quality:85});}
await b.close();
