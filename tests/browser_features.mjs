// Optional integration test. Start the local server from the project root first.
// In web/: npm install --no-save playwright && npx playwright install chromium
import {chromium} from '../web/node_modules/playwright/index.mjs';
import {readFile} from 'node:fs/promises';

const browser=await chromium.launch({headless:true,args:['--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream']});
try{
 const page=await browser.newPage({permissions:['camera'],acceptDownloads:true});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://localhost:8000/web/');
 await page.waitForFunction(()=>document.querySelector('#exercise').options.length===10);
 await page.locator('#exercise').selectOption('squat');
 await page.locator('#goalInput').fill('5');await page.locator('#goalInput').blur();
 if(!await page.locator('#goalStatus').textContent().then(x=>x.includes('0 / 5 次')))throw new Error('Goal not applied');
 await page.locator('#start').click();
 await page.waitForFunction(()=>document.querySelector('#latency').textContent.includes('ms'),null,{timeout:20000});
 await page.locator('#refreshCameras').click();
 await page.waitForFunction(()=>document.querySelector('#cameraSelect').options.length>1);
 const chosen=await page.locator('#cameraSelect option').nth(1).getAttribute('value');
 await page.locator('#cameraSelect').selectOption(chosen);
 await page.waitForFunction(()=>document.querySelector('#status').textContent==='训练进行中'&&document.querySelector('#video').srcObject?.active,null,{timeout:20000});
 const actual=await page.evaluate(()=>document.querySelector('#video').srcObject?.getVideoTracks()[0]?.getSettings().deviceId);
 if(actual!==chosen)throw new Error('Camera selection failed');
 await page.locator('#start').click();await page.locator('#exercise').selectOption('plank');
 if(await page.locator('#goalInput').inputValue()!=='30')throw new Error('Plank target not set');
 await page.evaluate(async()=>{
  const row=(await (await fetch('../tests/assets/motion_sequences.json')).json()).plank[0];
  const {ONNXPoseEstimator}=await import('./onnxPose.js');
  ONNXPoseEstimator.prototype.infer=async()=>({bbox:row.bbox,person_count:1,keypoints:row.keypoints.map(p=>[p.x,p.y,p.confidence])});
 });
 await page.locator('#start').click();
 await page.waitForFunction(()=>parseFloat(document.querySelector('#count').textContent)>1,null,{timeout:20000});
 await page.locator('#end').click();
 if(!await page.locator('#history').textContent().then(x=>x.includes('平板支撑')))throw new Error('Plank set not saved');
 await page.locator('#exercise').selectOption('squat');
 if(!await page.locator('#history').textContent().then(x=>x.includes('平板支撑')))throw new Error('Previous exercise lost');
 const downloadPromise=page.waitForEvent('download');await page.locator('#exportCsv').click();
 const csv=await readFile(await (await downloadPromise).path(),'utf8');
 if(!csv.includes('plank')||!csv.includes('completed')||csv.includes('keypoints'))throw new Error('CSV summary failed');
 page.once('dialog',dialog=>dialog.accept());await page.locator('#newWorkout').click();
 if(!await page.locator('#history').textContent().then(x=>x.includes('暂无训练记录')))throw new Error('New session did not clear data');
 if(errors.length)throw new Error(errors.join('\n'));
 console.log(JSON.stringify({goal:'passed',cameraSelection:'passed',plankSet:'passed',multiExerciseHistory:'passed',csvExport:'passed',newWorkout:'passed',pageErrors:errors}));
}finally{await browser.close();}
