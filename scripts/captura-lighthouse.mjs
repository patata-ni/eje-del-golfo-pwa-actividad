import {chromium} from '@playwright/test';
import fs from 'node:fs/promises';
const report=JSON.parse(await fs.readFile('evidencias/lighthouse.report.json','utf8'));
const summary={version:report.lighthouseVersion,fetchTime:report.fetchTime,url:report.finalDisplayedUrl||report.finalUrl,userAgent:report.userAgent,formFactor:report.configSettings.formFactor,throttling:report.configSettings.throttling,categories:Object.fromEntries(Object.entries(report.categories).map(([key,value])=>[key,Math.round(value.score*100)])),metrics:Object.fromEntries(['first-contentful-paint','largest-contentful-paint','speed-index','total-blocking-time','cumulative-layout-shift'].map(key=>[key,{value:report.audits[key].numericValue,display:report.audits[key].displayValue}])),findings:Object.entries(report.audits).filter(([,a])=>a.score!==null&&a.score<1).map(([id,a])=>({id,title:a.title,score:a.score,display:a.displayValue,description:a.description})),warnings:report.runWarnings};
await fs.writeFile('evidencias/resumen-lighthouse.json',JSON.stringify(summary,null,2));
const browser=await chromium.launch();const page=await browser.newPage({viewport:{width:1440,height:1100}});
await page.goto('file://'+process.cwd()+'/evidencias/lighthouse.report.html');await page.waitForTimeout(1000);
await page.screenshot({path:'evidencias/05-lighthouse.png',fullPage:false});await browser.close();
