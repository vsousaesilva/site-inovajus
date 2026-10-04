import { chromium } from 'playwright-core';
import { spawn } from 'child_process';
const [f0,f1,out]=[+process.argv[2],+process.argv[3],process.argv[4]];
const FPS=30, T0=7.2;
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
const p=await b.newPage({viewport:{width:1920,height:1080},deviceScaleFactor:2});
p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+process.cwd()+'/scene.html'); await p.evaluate(()=>window.ready);
const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate',''+FPS,'-c:v','png','-i','-','-threads','2','-c:v','libx264','-preset','slow','-crf','12','-pix_fmt','yuv420p','-tune','animation',out],{stdio:['pipe','inherit','inherit']});
const st=Date.now();
for(let f=f0;f<f1;f++){
  await p.evaluate(t=>render(t),T0+f/FPS);
  const buf=await p.screenshot({type:'png'});
  if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
  if((f-f0)%100===0) console.log(out,f,((Date.now()-st)/1000/(f-f0+1)).toFixed(2)+'s/f');
}
ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close();
console.log('done',out,((Date.now()-st)/1000).toFixed(0)+'s');
