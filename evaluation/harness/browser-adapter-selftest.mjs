// Synthetic local driver self-test. No MedResearch task and no OpenAI calls.
import assert from 'node:assert/strict'
import { createServer } from 'node:http'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'
import { executeAction, sha256 } from './native-cua.mjs'
const { chromium }=await import(pathToFileURL(resolve(process.argv[2]||'outputs/medresearch/frontend/node_modules/playwright/index.mjs')).href)
const server=createServer((request,response)=>{response.setHeader('Content-Type','text/html');response.end(`<title>${request.url}</title><h1>${request.url}</h1>`)})
await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve))
const origin='http://127.0.0.1:'+server.address().port
const config={base_url:origin,allowed_local_origins:[],external_hosts:[],viewport:{width:1280,height:800}}
let browser,checks=0
try{
  browser=await chromium.launch({executablePath:'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe'})
  const context=await browser.newContext({viewport:config.viewport});const first=await context.newPage()
  await first.goto(origin+'/one');await first.goto(origin+'/two');const second=await context.newPage();await second.goto(origin+'/mailbox')
  let selected=first;const driver={pages:()=>context.pages(),selectPage:page=>{selected=page}}
  await executeAction(first,{type:'keypress',keys:['ALT','LEFT']},config,driver);assert.equal(await first.title(),'/one');checks++
  await executeAction(first,{type:'keypress',keys:['ALT','RIGHT']},config,driver);assert.equal(await first.title(),'/two');checks++
  await executeAction(first,{type:'keypress',keys:['CTRL','R']},config,driver);assert.equal(await first.title(),'/two');checks++
  const before=sha256(await selected.screenshot())
  await executeAction(selected,{type:'keypress',keys:['CTRL','TAB']},config,driver);assert.equal(selected,second);checks++
  assert.notEqual(sha256(await selected.screenshot()),before);checks++
  await executeAction(selected,{type:'keypress',keys:['CTRL','SHIFT','TAB']},config,driver);assert.equal(selected,first);checks++
  assert.equal(sha256(await selected.screenshot()),before);checks++
  console.log(JSON.stringify({kind:'synthetic_local_browser_adapter_selftest_only',checks,passed:checks,model_requests:0,medresearch_tests_executed:0,api_cost_usd:0},null,2))
}finally{if(browser)await browser.close();await new Promise(resolve=>server.close(resolve))}
