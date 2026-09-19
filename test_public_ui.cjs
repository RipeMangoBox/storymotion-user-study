// Real public-media playback using explicitly excluded test sessions.
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = 'https://ripemangobox.github.io/storymotion-user-study/';
const API = fs.readFileSync('web/config.js', 'utf8').match(/https:\/\/[^']+/)[0];
(async () => {
  const browser = await chromium.launch({headless:true, executablePath:'/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge'});
  const checked=[];
  for(const mode of ['given','joint']) {
    let s;
    for(let i=0;i<48;i++) {
      const r=await fetch(API+'/api/start',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({language:'zh',consent:true,test_mode:true,test_key:fs.readFileSync('runtime/test.key','utf8').trim(),protocol_version:'paired-40-v2'})});
      if(!r.ok)throw Error('Test session start failed '+r.status);
      s=await r.json();if(s.trials[0].mode===mode)break;
    }
    if(!s.is_test||s.trials[0].mode!==mode)throw Error('Missing test task');
    const context=await browser.newContext();const page=await context.newPage();const errors=[];
    page.on('pageerror',e=>errors.push(e.message));
    await page.goto(BASE+'?test=1');
    await page.evaluate(token=>localStorage.setItem('motion-camera-study-blender-v3-test-token',token),s.token);
    await page.reload();await page.locator('#tutorial-next').click();
    await page.waitForSelector('#video-0');
    await page.evaluate(()=>document.querySelectorAll('video').forEach(v=>v.playbackRate=4));
    await page.locator('#replay').click();
    await page.waitForFunction(()=>[...document.querySelectorAll('.video-status')].every(e=>['已观看','Watched'].includes(e.textContent)),{}, {timeout:90000});
    await page.evaluate(()=>document.querySelectorAll('fieldset').forEach(f=>f.querySelector('input[value="0"]').click()));
    await page.locator('#language').click();await page.reload();await page.waitForSelector('#video-0');
    if(await page.locator('input:checked').count()!==s.trials[0].questions.length)throw Error('Draft restore failed');
    const status=await page.locator('.video-status').allTextContents();
    if(status.length!==2||!status.every(t=>['已观看','Watched'].includes(t)))throw Error('Playback status not restored');
    await page.screenshot({path:'runtime/public-recheck-'+mode+'.png',fullPage:true});
    if(errors.length)throw Error(errors.join(';'));
    checked.push({mode,real_public_playback:true,bilingual_toggle:true,draft_resume:true,questions:s.trials[0].questions.length});
    await context.close();
  }
  await browser.close();console.log(JSON.stringify({status:'PASS',checked}));
})().catch(e=>{console.error(e);process.exit(1)});
