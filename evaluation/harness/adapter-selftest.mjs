// Local adapter unit checks only: no model, website, network, or paid API execution.
import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { allowURL,checkBudget,costUpper,countPayload,executeAction,limitsFor,localOrigin,redactedAction,requestPolicy,safeBrowserURL,validateApproval } from './native-cua.mjs'
const c=JSON.parse(await readFile(new URL('./config.example.json',import.meta.url),'utf8'))
const zero=()=>({model_requests:0,actions:0,input_tokens:0,output_tokens:0,charged_upper_usd:0})
let checks=0
function check(f){f();checks++}
check(()=>assert.equal(allowURL('http://127.0.0.1:8124/search',c),true))
check(()=>assert.equal(allowURL('http://127.0.0.1:9999/',c),false))
check(()=>assert.equal(allowURL('https://pubmed.ncbi.nlm.nih.gov/31452104/',c),true))
check(()=>assert.equal(allowURL('https://pubmed.ncbi.nlm.nih.gov.evil.example/',c),false))
check(()=>assert.equal(allowURL('https://user:secret@pubmed.ncbi.nlm.nih.gov/',c),false))
check(()=>assert.equal(allowURL('file:///C:/Users/',c),false))
check(()=>assert.equal(requestPolicy('https://analytics.example/event',false,c),'block-resource'))
check(()=>assert.equal(requestPolicy('https://analytics.example/',true,c),'block-navigation'))
check(()=>assert.equal(requestPolicy('https://static.ncbi.nlm.nih.gov/pubmed/file.css',false,c),'allow'))
check(()=>assert.equal(requestPolicy('https://static.ncbi.nlm.nih.gov/',true,c),'block-navigation'))
check(()=>assert.equal(requestPolicy('https://pubmed.ncbi.nlm.nih.gov/31452104/',true,c),'allow'))
check(()=>assert.throws(()=>validateApproval({},c,'suite','config'),/approval/))
check(()=>assert.throws(()=>validateApproval({approved:true,user_statement:'yes',approved_at:'2026-11-16',model:c.model,max_usd:c.total_usd,suite_sha256:'wrong',config_sha256:'config'},c,'suite','config'),/match/))
check(()=>validateApproval({approved:true,user_statement:'Explicit user approval supplied externally',approved_at:'2026-11-16',model:c.model,max_usd:c.total_usd,suite_sha256:'suite',config_sha256:'config'},c,'suite','config'))
check(()=>assert.throws(()=>validateApproval({approved:true,user_statement:'Only 30 approved',approved_at:'2026-11-16',model:c.model,max_usd:30,suite_sha256:'suite',config_sha256:'config'},c,'suite','config'),/Budget/))
check(()=>assert.equal(costUpper(10000,1000,c),0.07))
check(()=>assert.throws(()=>checkBudget(zero(),{...zero(),charged_upper_usd:c.total_usd-0.01},c,10000,2048),/budget/))
check(()=>assert.throws(()=>checkBudget({...zero(),model_requests:20},zero(),c,100,100),/request/))
check(()=>assert.throws(()=>checkBudget({...zero(),input_tokens:149999},zero(),c,2,100),/Input/))
check(()=>assert.equal(redactedAction({type:'type',text:'secret-password'}).text,'[REDACTED_TYPED_TEXT]'))
const events=[]
const page={keyboard:{press:async(...a)=>events.push(['press',...a]),insertText:async(...a)=>events.push(['type',...a]),down:async(...a)=>events.push(['key-down',...a]),up:async(...a)=>events.push(['key-up',...a])},mouse:{click:async(...a)=>events.push(['click',...a]),move:async(...a)=>events.push(['move',...a]),wheel:async(...a)=>events.push(['wheel',...a]),down:async()=>events.push(['down']),up:async()=>events.push(['up'])},waitForTimeout:async n=>events.push(['wait',n])}
const nativeFixture={type:'computer_call',call_id:'fixture-not-api',status:'completed',actions:[{type:'click',x:100,y:90,button:'left'},{type:'type',text:'synthetic text'},{type:'keypress',keys:['CTRL','A']},{type:'scroll',x:100,y:100,scroll_x:0,scroll_y:500},{type:'screenshot'}]}
for(const a of nativeFixture.actions)await executeAction(page,a,c)
check(()=>assert.equal(events[0][0],'click'))
check(()=>assert.equal(events[1][0],'type'))
check(()=>assert.deepEqual(events[2],['press','Control+A']))
check(()=>assert.deepEqual(events[4],['wheel',0,500]))
await assert.rejects(()=>executeAction(page,{type:'click',x:9999,y:1},c),/coordinates/);checks++
await assert.rejects(()=>executeAction(page,{type:'keypress',keys:['CTRL','SHIFT','I']},c),/Privileged/);checks++
await assert.rejects(()=>executeAction(page,{type:'javascript',code:'alert(1)'},c),/Unsupported/);checks++
await assert.rejects(()=>executeAction(page,{type:'drag',path:[]},c),/drag/);checks++
check(()=>assert.equal(allowURL('http://127.0.0.1:8125/inbox',c),true))
check(()=>assert.equal(allowURL('http://127.0.0.1:8126/',c),true))
check(()=>assert.equal(allowURL('http://127.0.0.1:8127/',c),false))
check(()=>assert.equal(safeBrowserURL('http://127.0.0.1:8124/search?q=asthma&code=123456#sensitive'),'http://127.0.0.1:8124/search?q=asthma&code=REDACTED'))
check(()=>assert.throws(()=>localOrigin('https://external.example'),/loopback/))
check(()=>assert.throws(()=>localOrigin('http://127.0.0.1:8125/mail'),/origins/))
check(()=>assert.equal(limitsFor({difficulty:'expert'},c).model_requests,60))
check(()=>assert.equal(limitsFor({difficulty:'Hard'},c).actions,160))
check(()=>assert.equal(limitsFor({difficulty:'Medium'},c).runtime_seconds,900))
check(()=>assert.throws(()=>limitsFor({difficulty:'Unknown'},c),/difficulty/))
check(()=>assert.ok(checkBudget({...zero(),model_requests:20},zero(),c,100,100,limitsFor({difficulty:'Expert'},c))>0))
check(()=>assert.deepEqual(countPayload({model:'gpt-6.1-sol',reasoning:{effort:'low'},tools:[{type:'computer'}],max_output_tokens:2048,store:true,service_tier:'default'}),{model:'gpt-6.1-sol',reasoning:{effort:'low'},tools:[{type:'computer'}]}))
const browserEvents=[]
page.goBack=async()=>browserEvents.push('back');page.goForward=async()=>browserEvents.push('forward');page.reload=async()=>browserEvents.push('reload');page.isClosed=()=>false;page.url=()=>c.base_url;page.bringToFront=async()=>browserEvents.push('main-tab')
const mailbox={isClosed:()=>false,url:()=>c.allowed_local_origins[0],bringToFront:async()=>browserEvents.push('mailbox-tab')}
let selected=page
const driver={pages:()=>[page,mailbox],selectPage:p=>{selected=p}}
await executeAction(page,{type:'keypress',keys:['ALT','LEFT']},c,driver)
await executeAction(page,{type:'keypress',keys:['ALT','RIGHT']},c,driver)
await executeAction(page,{type:'keypress',keys:['CTRL','R']},c,driver)
await executeAction(page,{type:'keypress',keys:['F5']},c,driver)
await executeAction(page,{type:'keypress',keys:['CTRL','TAB']},c,driver)
check(()=>assert.equal(selected,mailbox))
await executeAction(mailbox,{type:'keypress',keys:['CTRL','SHIFT','TAB']},c,driver)
check(()=>assert.equal(selected,page))
check(()=>assert.deepEqual(browserEvents,['back','forward','reload','reload','mailbox-tab','main-tab']))
await assert.rejects(()=>executeAction(page,{type:'keypress',keys:['CTRL','L']},c,driver),/Privileged/);checks++
console.log(JSON.stringify({kind:'adapter_unit_selftest_only',checks,passed:checks,model_requests:0,website_tests_executed:0,api_cost_usd:0},null,2))
