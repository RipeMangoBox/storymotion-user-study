const {chromium}=require('playwright');
const fs=require('fs');
const BASE=process.env.TEST_URL||'http://127.0.0.1:18008';
const API=process.env.TEST_API||BASE;
const key=fs.readFileSync('runtime/test.key','utf8').trim();
(async()=>{
 const start=await fetch(API+'/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({language:'zh',consent:true,test_key:key})});
 if(!start.ok)throw Error('start '+start.status);
 const s=await start.json();
 if(s.trials.length!==40||!s.is_test||s.trials.slice(0,20).some(t=>t.mode!=='given')||s.trials.slice(20).some(t=>t.mode!=='joint'))throw Error('cohort');
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'});
 const page=await browser.newPage({viewport:{width:1360,height:1050}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(BASE,{waitUntil:'domcontentloaded'});
 await page.screenshot({path:'runtime/welcome.png',fullPage:true});
 await page.evaluate(token=>localStorage.setItem('motion-camera-study-v1-token',token),s.token);
 await page.reload({waitUntil:'domcontentloaded'});
 await page.waitForSelector('#video-0');
 for(let i=0;i<40;i++){
   await page.waitForSelector('#video-0');
   await page.evaluate(()=>document.querySelectorAll('video').forEach(v=>v.playbackRate=3));
   await page.locator('#replay').click();
   await page.waitForFunction(()=>[...document.querySelectorAll('.video-status')].every(e=>['已观看','Watched'].includes(e.textContent)),{},{timeout:90000});
   await page.evaluate(()=>document.querySelectorAll('fieldset').forEach(f=>{const r=f.querySelector('input[value="0"]');r.click();}));
   if(i===0){await page.screenshot({path:'runtime/given.png',fullPage:true});await page.locator('#language').click();await page.screenshot({path:'runtime/given-en.png',fullPage:true});}
   if(i===20){await page.screenshot({path:'runtime/joint.png',fullPage:true});}
   if(i===3){await page.reload({waitUntil:'domcontentloaded'});await page.waitForSelector('#video-0');if(await page.locator('input:checked').count()!==3)throw Error('draft restore');}
   await page.locator('#next').click();
   if(i===19){await page.waitForSelector('#continue');await page.screenshot({path:'runtime/transition.png',fullPage:true});await page.locator('#continue').click();}
   else if(i<39){await page.waitForFunction(n=>document.querySelector('.badge')?.textContent.includes((n+1)+' / 40'),i+1,{timeout:30000});}
   console.log('Completed UI trial',i+1);
 }
 await page.waitForSelector('.receipt',{timeout:30000});
 await page.screenshot({path:'runtime/completed.png',fullPage:true});
 const r=await fetch(API+'/api/session',{headers:{Authorization:'Bearer '+s.token}});const saved=await r.json();
 if(!saved.submitted||Object.keys(saved.answers).length!==40)throw Error('not persisted');
 const twice=await fetch(API+'/api/submit',{method:'POST',headers:{Authorization:'Bearer '+s.token}}).then(r=>r.json());
 if(twice.receipt!==saved.receipt)throw Error('idempotency');
 if(errors.length)throw Error(errors.join('\n'));
 await page.setViewportSize({width:390,height:844});await page.reload();await page.screenshot({path:'runtime/completed-mobile.png',fullPage:true});
 console.log(JSON.stringify({passed:true,trials:40,criteria:160,receipt:saved.receipt,consoleErrors:errors.length,base:BASE}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1);});
