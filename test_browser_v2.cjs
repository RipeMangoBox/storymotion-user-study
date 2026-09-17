const {chromium}=require('playwright');
const fs=require('fs');
const BASE=process.env.TEST_URL||'http://127.0.0.1:18009';
const API=process.env.TEST_API||BASE;
const key=process.env.TEST_KEY||'local-browser-test';
const localMedia={};
if(process.env.LOCAL_MEDIA_ROUTE){
 const catalog=JSON.parse(fs.readFileSync('runtime/catalog.json'));
 for(const s of catalog.samples)for(const [m,v] of Object.entries(s.methods)){
  const p=process.env.LOCAL_MEDIA_ROUTE+'/'+(s.mode==='given'?'givenh':'full')+'/user_study/'+s.id+'/'+(m==='mainline'?'storymotion':'baseline/'+m)+'/preview.mp4';
  if(!fs.existsSync(p))throw Error('Missing local source '+p);localMedia[v.media_id]=p;
 }
}
async function routes(page){
 if(API===BASE)await page.route('**/config.js',route=>route.fulfill({contentType:'application/javascript',body:'window.STUDY_API="";'}));
 if(process.env.LOCAL_MEDIA_ROUTE)await page.route('**/media/*',route=>route.fulfill({contentType:'video/mp4',body:fs.readFileSync(localMedia[route.request().url().split('/').pop()])}));
}
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',...(process.env.TEST_PROXY?{proxy:{server:process.env.TEST_PROXY,bypass:'localhost,127.0.0.1'}}:{})});
 const results=[];
 for(const first of ['given','joint']){
  let s;
  for(let i=0;i<100;i++){
   const r=await fetch(API+'/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({language:'zh',consent:true,protocol_version:'paired-40-v2',test_mode:true,test_key:key})});
   if(!r.ok)throw Error(await r.text());s=await r.json();if(s.trials[0].mode===first)break;
  }
  if(s.trials[0].mode!==first)throw Error('missing task order');
  const context=await browser.newContext({viewport:{width:1366,height:768}});const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await routes(page);
  await page.goto(BASE+'/?test=1');
  await page.evaluate(token=>{localStorage.setItem('motion-camera-study-v1-test-token',token);},s.token);
  await page.reload();await page.waitForSelector('#tutorial-next');await page.locator('#tutorial-next').click();
  for(let i=0;i<40;i++){
   await page.waitForSelector('#video-0');
   await page.evaluate(()=>document.querySelectorAll('video').forEach(v=>v.playbackRate=4));
   await page.locator('#replay').click();
   await page.waitForFunction(()=>[...document.querySelectorAll('.video-status')].every(e=>['已观看','Watched'].includes(e.textContent)),{}, {timeout:60000});
   await page.evaluate(()=>document.querySelectorAll('fieldset').forEach(f=>f.querySelector('input[value="0"]').click()));
   if(i===0){
    await page.screenshot({path:'runtime/v2-'+first+'.png',fullPage:true});
    await page.locator('#language').click();await page.reload();await page.waitForSelector('#video-0');
    if(await page.locator('input:checked').count()!==s.trials[i].questions.length)throw Error('draft restore');
   }
   await page.locator('#next').click();
   if(i===19){await page.waitForSelector('#continue');const text=await page.locator('.scope').innerText();if(!text.includes(first==='given'?'joint':'camera only'))throw Error('transition '+text);await page.locator('#continue').click();}
   else if(i<39)await page.waitForFunction(n=>document.querySelector('.badge')?.textContent.includes((n+1)+' / 40'),i+1,{timeout:30000});
   if(i%10===9)console.log(first+' completed '+(i+1));
  }
  await page.waitForSelector('.receipt');const receipt=await page.locator('.receipt').innerText();
  const saved=await fetch(API+'/api/session',{headers:{Authorization:'Bearer '+s.token}}).then(r=>r.json());
  if(!saved.submitted||Object.keys(saved.answers).length!==40||!saved.is_test)throw Error('persistence');
  const twice=await fetch(API+'/api/submit',{method:'POST',headers:{Authorization:'Bearer '+s.token}}).then(r=>r.json());if(twice.receipt!==receipt)throw Error('duplicate submit');
  if(errors.length)throw Error(errors.join('\n'));
  results.push({first,receipt,trials:40,criteria:160,errors:errors.length});await context.close();
 }
 // Mobile layout and shared playback, including a one-sided readiness stall.
 const context=await browser.newContext({viewport:{width:390,height:844}});const page=await context.newPage();
 await routes(page);
 const s=await fetch(API+'/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({language:'en',consent:true,protocol_version:'paired-40-v2',test_mode:true,test_key:key})}).then(r=>r.json());
 await page.goto(BASE+'/?test=1');await page.evaluate(t=>{localStorage.setItem('motion-camera-study-v1-test-token',t);localStorage.setItem('motion-camera-study-v1-test-tutorial',t);},s.token);await page.reload();await page.waitForSelector('#video-0');
 if(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth))throw Error('horizontal overflow');
 await page.screenshot({path:'runtime/v2-mobile.png',fullPage:true});
 await page.waitForFunction(()=>[...document.querySelectorAll('video')].every(v=>v.readyState>=3));
 await page.evaluate(()=>{Object.defineProperty(document.querySelector('#video-1'),'readyState',{value:2,configurable:true});});await page.locator('#play').click();await page.waitForTimeout(500);
 if(await page.evaluate(()=>[...document.querySelectorAll('video')].some(v=>!v.paused)))throw Error('buffer barrier');
 await page.evaluate(()=>delete document.querySelector('#video-1').readyState);await page.waitForTimeout(1000);
 if(await page.evaluate(()=>[...document.querySelectorAll('video')].some(v=>v.paused)))throw Error('buffer recovery');
 await page.locator('#play').click();await page.waitForTimeout(300);
 if(await page.evaluate(()=>[...document.querySelectorAll('video')].some(v=>!v.paused)))throw Error('synchronized pause');
 console.log(JSON.stringify({passed:true,results,mobile:true,bufferBarrier:true}));await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
