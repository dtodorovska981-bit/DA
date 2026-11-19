const {chromium}=require('playwright');const {spawn}=require('child_process');
(async()=>{const mode=process.argv[2];const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1350}});
await p.goto('file://'+__dirname+'/index.html');await p.evaluate(()=>document.fonts.ready);
if(mode==='stills'){for(const t of process.argv.slice(3)){await p.evaluate(ms=>seek(ms),t*1000);await p.screenshot({path:`still_${t}.jpg`,type:'jpeg',quality:80});}}
else{const D=20,F=30;const ff=spawn('ffmpeg',['-y','-v','error','-f','image2pipe','-framerate',F,'-c:v','mjpeg','-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','16','-preset','slow','-movflags','+faststart',process.argv[3]],{stdio:['pipe','inherit','inherit']});
for(let i=0;i<D*F;i++){await p.evaluate(ms=>seek(ms),i*1000/F);const buf=await p.screenshot({type:'jpeg',quality:97});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
ff.stdin.end();await new Promise(r=>ff.on('close',r));}
await b.close()})();
