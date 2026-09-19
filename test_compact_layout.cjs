// Isolated frontend fixtures; no participant session or answer is created.
const {chromium}=require('playwright');
const fs=require('fs');
const assert=require('assert');
const samples=JSON.parse(fs.readFileSync('runtime/catalog.json')).samples;
const BASE='http://127.0.0.1:18019/';
const camera=['camera_text','camera_geometry','framing'];
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'});
 const page=await browser.newPage();const errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/api/**',r=>r.fulfill({json:{}}));
 await page.route('**/media/**',r=>{
  const id=r.request().url().split('/').pop();
  return r.fulfill({contentType:'video/mp4',body:fs.readFileSync('runtime/blind_media/'+id+'.mp4')});
 });
 await page.goto(BASE);await page.waitForSelector('#consent');
 let checked=0,maxBottom=0;
 for(const viewport of [{width:1366,height:768},{width:1280,height:720},{width:1440,height:900},{width:390,height:844}]){
  await page.setViewportSize(viewport);
  for(const language of ['zh','en'])for(const sample of samples){
   const trial={...sample,questions:sample.mode==='given'?camera:['human_text','human_physics',...camera],videos:Object.values(sample.methods).slice(0,2).map(v=>'/media/'+v.media_id)};
   await page.evaluate(({trial,language})=>{
    lang=language;session={is_test:false,trials:[trial],answers:{}};index=0;page='trial';ratings={};watched=[false,false];coverage=[0,0];render();
   },{trial,language});
   await page.waitForTimeout(40);
   const result=await page.evaluate(()=>({
    bottom:document.querySelector('.nav').getBoundingClientRect().bottom,
    viewport:innerHeight,overflow:document.documentElement.scrollWidth>innerWidth,
    videoWidth:document.querySelector('.videos').getBoundingClientRect().width,
    questionWidth:document.querySelector('.questions').getBoundingClientRect().width,
    videoHeight:document.querySelector('video').getBoundingClientRect().height,
    fit:getComputedStyle(document.querySelector('video')).objectFit,
    text:document.body.innerText,
   }));
   assert(!result.overflow,'horizontal overflow');
   assert(Math.abs(result.videoWidth-result.questionWidth)<1,'width mismatch');
   assert.equal(result.fit,'contain');
   assert(!/以英文原文为准|不能单独说明|does not determine/.test(result.text));
   if(viewport.width>=760 && result.bottom>viewport.height){
    await page.screenshot({path:'runtime/compact-layout-failure.png',fullPage:true});
    console.log(await page.evaluate(()=>Object.fromEntries(['header','.prompts','.videos','.playbar','.questions','.rating-row','.nav'].map(s=>[s,document.querySelector(s).getBoundingClientRect().height]))));
    throw Error(JSON.stringify({viewport,language,id:sample.id,...result}));
   }
   if(viewport.width===1366)maxBottom=Math.max(maxBottom,result.bottom);
   checked++;
  }
 }
 await page.setViewportSize({width:1366,height:768});
 for(const mode of ['given','joint']){
  const sample=samples.find(s=>s.mode===mode);
  const trial={...sample,questions:mode==='given'?camera:['human_text','human_physics',...camera],videos:Object.values(sample.methods).slice(0,2).map(v=>'/media/'+v.media_id)};
  await page.evaluate(trial=>{lang='zh';session={is_test:false,trials:[trial],answers:{}};index=0;page='trial';ratings={};render();},trial);
  await page.waitForFunction(()=>[...document.querySelectorAll('video')].every(v=>v.readyState>=2));
  await page.locator('.choice').nth(0).click();
  assert.equal(await page.locator('input:checked').count(),1);
  await page.locator('#language').click();
  assert.equal(await page.locator('input:checked').count(),1);
  await page.locator('#language').click();
  await page.waitForTimeout(100);
  await page.screenshot({path:`runtime/compact-matrix-${mode}.png`,fullPage:true});
 }
 assert.equal(errors.length,0,errors.join('\n'));
 console.log(JSON.stringify({status:'PASS',checked,desktopZoom:'100%',maxBottomAt768:maxBottom,sharedWidths:true,radioAndLanguagePreserved:true}));
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
