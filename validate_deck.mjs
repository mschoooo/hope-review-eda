import { chromium } from 'playwright';
const browser = await chromium.launch({headless:true, executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
const page = await browser.newPage({viewport:{width:1440,height:810},deviceScaleFactor:1});
await page.goto('http://127.0.0.1:8000/index.html', {waitUntil:'networkidle'});
await page.screenshot({path:'deck_assets/desktop.png',fullPage:false});
const desktop = await page.evaluate(() => ({slides:document.querySelectorAll('.slide').length,active:document.querySelectorAll('.slide.active').length,nav:document.querySelectorAll('.nav button').length,title:document.querySelector('.title')?.textContent.trim(),overflow:document.documentElement.scrollWidth>window.innerWidth}));
await page.keyboard.press('ArrowRight'); await page.waitForTimeout(650);
const second=await page.evaluate(()=>({active:[...document.querySelectorAll('.slide')].findIndex(x=>x.classList.contains('active')),count:document.querySelector('.count')?.textContent}));
for(let i=2;i<10;i++){await page.keyboard.press('ArrowRight');await page.waitForTimeout(80)}
const assets=await page.evaluate(()=>({active:[...document.querySelectorAll('.slide')].findIndex(x=>x.classList.contains('active')),images:[...document.images].map(x=>({src:x.getAttribute('src'),ok:x.complete&&x.naturalWidth>0}))}));
const mobile=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1});
await mobile.goto('http://127.0.0.1:8000/index.html',{waitUntil:'networkidle'}); await mobile.screenshot({path:'deck_assets/mobile.png',fullPage:false});
const mob=await mobile.evaluate(()=>({width:document.documentElement.scrollWidth,height:document.documentElement.scrollHeight,viewport:innerWidth,overflow:document.documentElement.scrollWidth>innerWidth}));
console.log(JSON.stringify({desktop,second,assets,mobile:mob},null,2));
if(desktop.slides!==10||desktop.active!==1||desktop.nav!==10||desktop.overflow||second.active!==1||assets.active!==9||assets.images.some(x=>!x.ok)||mob.overflow)process.exit(1);
await browser.close();
