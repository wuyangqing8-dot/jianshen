// Optional: in web/, npm install --no-save playwright; npx playwright install chromium
// Start python -m http.server 8000 in project root, then node tests/browser_smoke.mjs
import {chromium} from '../web/node_modules/playwright/index.mjs';
import {fileURLToPath} from 'node:url';
const browser=await chromium.launch({headless:true});
try{
 const page=await browser.newPage({viewport:{width:1400,height:1050}}),errors=[];
 page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://localhost:8000/web/');
 await page.waitForFunction(()=>document.querySelector('#exercise').options.length===10);
 const modelResult=await page.evaluate(async()=>{const {ONNXPoseEstimator}=await import('./onnxPose.js');const m=new ONNXPoseEstimator();await m.load_model();const im=new Image();im.src='../tests/assets/person.jpg';await im.decode();const p=await m.infer(im);return {provider:m.provider,people:p?.person_count,keypoints:p?.keypoints.length};});
 if(!(modelResult.people>=1&&modelResult.keypoints===17))throw new Error('Real model smoke failed');
 await page.locator('#file').setInputFiles(fileURLToPath(new URL('./assets/smoke_h264.mp4',import.meta.url)));
 await page.waitForFunction(()=>document.querySelector('#latency').textContent.includes('ms'));
 await page.locator('#pause').click();
 if(await page.locator('#status').textContent()!=='已暂停')throw new Error('Pause failed');
 await page.locator('#exercise').selectOption('plank');
 if(await page.locator('#countLabel').textContent()!=='可评估时长')throw new Error('Switch failed');
 await page.locator('#reset').click();
 await page.locator('#file').setInputFiles(fileURLToPath(new URL('./assets/smoke_h264.mp4',import.meta.url)));
 await page.waitForFunction(()=>document.querySelector('#status').textContent==='训练进行中');
 await page.locator('#start').click();
 if(await page.locator('#empty').evaluate(e=>e.style.display)!=='flex')throw new Error('Stop did not clear the video');
 if(errors.length)throw new Error(errors.join('\n'));
 console.log(JSON.stringify({modelResult,videoInput:'passed',repeatVideo:'passed',pause:'passed',switch:'passed',stop:'passed',pageErrors:errors},null,2));
}finally{await browser.close();}
