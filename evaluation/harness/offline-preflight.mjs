// Infrastructure only: local browser, SQLite and mail capture. No model/key access.
import assert from 'node:assert/strict'
import {spawn} from 'node:child_process'
import {mkdir,readFile,writeFile,readdir} from 'node:fs/promises'
import {resolve,join} from 'node:path'
import {pathToFileURL} from 'node:url'
import {createConnection} from 'node:net'
import {sha256} from './native-cua.mjs'
const config=JSON.parse(await readFile('evaluation/run-config.json','utf8'))
const runtime=resolve('evaluation/environment/.runtime')
const out=resolve('evaluation/private/offline-preflight')
await mkdir(out,{recursive:true})
const python=resolve(config.environment_python),script=resolve('evaluation/environment/offline-environment.py')
const env={...process.env,PYTHONUNBUFFERED:'1'}
for(const key of Object.keys(env))if(key.startsWith('OPENAI_')||key.toUpperCase().endsWith('_PROXY'))delete env[key]
const checks=[],attempts=[],children=new Set()
function child(args){
  const cp=spawn(python,['-u',script,...args],{env,windowsHide:true,stdio:['ignore','pipe','pipe']})
  children.add(cp);let output=''
  cp.stdout.on('data',b=>{output+=b});cp.stderr.on('data',b=>{output+=b})
  cp.done=new Promise((ok,bad)=>{cp.once('error',bad);cp.once('close',code=>{children.delete(cp);ok(code)})})
  cp.log=()=>output;return cp
}
async function command(args){const cp=child(args);const code=await cp.done;await writeFile(join(out,args[0]+'-'+args.at(-1).replace(/[^a-zA-Z0-9_-]/g,'_')+'.log'),cp.log());assert.equal(code,0,'Offline command failed: '+args[0]);return cp}
async function stop(cp){if(cp&&cp.exitCode===null){cp.kill();await cp.done}}
async function ready(url){for(let n=0;n<60;n++){try{const r=await fetch(url,{signal:AbortSignal.timeout(1000)});if(r.ok)return await r.text()}catch{}await new Promise(r=>setTimeout(r,250))}throw new Error('Loopback readiness timeout')}
async function smtpReady(){for(let n=0;n<40;n++){const ok=await new Promise(r=>{const s=createConnection({host:'127.0.0.1',port:8127});let done=false;const end=x=>{if(!done){done=true;s.destroy();r(x)}};s.setTimeout(500);s.on('data',b=>end(b.toString().startsWith('220')));s.on('error',()=>end(false));s.on('timeout',()=>end(false))});if(ok)return;await new Promise(r=>setTimeout(r,100))}throw new Error('SMTP readiness timeout')}
const {chromium}=await import(pathToFileURL(resolve(config.playwright_module)).href)
let browser
try{
  const freeze=JSON.parse(await readFile('evaluation/freeze.json','utf8'))
  for(const [name,digest] of Object.entries(freeze.files))assert.equal(sha256(await readFile('evaluation/'+name)),digest)
  checks.push('All frozen test/requirements/Markdown hashes unchanged')
  browser=await chromium.launch({executablePath:config.browser_executable,headless:true})
  for(const mode of ['standard','mail','smtp']){
    const name='preflight-'+mode
    await command(['reset','--case',name,'--mode',mode,'--fixture','accounts'])
    checks.push(mode+': migrations and two synthetic accounts initialized in isolated SQLite')
    const server=child(['serve','--case',name])
    const health=JSON.parse(await ready(config.base_url+'/api/health/'));assert.equal(health.status,'ok')
    checks.push(mode+': local health endpoint responds')
    const stateFile=join(out,name+'-state.json')
    await command(['capture','--case',name,'--output',stateFile])
    const state=JSON.parse(await readFile(stateFile,'utf8'));assert.equal(state.users.length,2)
    assert.deepEqual(state.users.map(u=>u.username),['eva_a','eva_b'])
    checks.push(mode+': sanitized readonly database capture verifies synthetic account persistence')
    if(mode==='standard'){
      for(const viewport of [{width:1440,height:900},{width:390,height:844}]){
        const context=await browser.newContext({viewport,deviceScaleFactor:1,serviceWorkers:'block'})
        await context.route('**/*',route=>new URL(route.request().url()).origin===config.base_url?route.continue():route.abort())
        const page=await context.newPage();await page.goto(config.base_url+'/profile',{waitUntil:'networkidle'})
        assert.ok(await page.getByRole('heading',{name:/sign in/i}).count())
        assert.ok(await page.locator('input[type=password]').count()>=1)
        const bytes=await page.screenshot({path:join(out,'profile-'+viewport.width+'.png'),scale:'css'})
        assert.equal(bytes.readUInt32BE(16),viewport.width);assert.equal(bytes.readUInt32BE(20),viewport.height)
        checks.push(`Browser renders real sign-in form at frozen ${viewport.width}x${viewport.height}, 1 CSS pixel per image pixel`)
        await context.close()
      }
      await stop(server)
      const restarted=child(['serve','--case',name]);await ready(config.base_url+'/api/health/')
      const after=join(out,name+'-restart.json');await command(['capture','--case',name,'--output',after])
      assert.deepEqual(JSON.parse(await readFile(after,'utf8')).users,state.users)
      checks.push('SQLite account data survives isolated application restart (not T098 PostgreSQL evidence)')
      await stop(restarted)
    }else{
      let smtp;if(mode==='smtp'){smtp=child(['smtp','--case',name]);await smtpReady()}
      await command(['mail-probe',name]);assert.ok((await readdir(join(runtime,'cases',name,'mail'))).length>0)
      const mail=child(['mail','--case',name]);const inbox=await ready('http://127.0.0.1:8125/')
      assert.ok(inbox.includes('Offline transport probe'))
      checks.push(mode+': real Django mail backend sends to local capture and inbox shows synthetic probe')
      await stop(mail);await stop(smtp);await stop(server)
    }
  }
}catch(error){attempts.push({status:'ERROR',message:error.message});process.exitCode=1}
finally{
  if(browser)await browser.close()
  for(const cp of [...children])await stop(cp)
  const report={kind:'offline_infrastructure_preflight_only',checked_at_utc:new Date().toISOString(),
    status:attempts.length?'ERROR':'PASS',checks,errors:attempts,
    openai_api_requests:0,paid_api_calls:0,api_cost_usd:0,formal_cua_tests_executed:0,
    external_network:'Python blocks non-loopback connect and DNS; browser route allows only local application; keys removed from child environment',
    application_commit:'03a7dc2a349a3f26bc1712c79d77957cf9338a1a',
    limitations:['No live NCBI availability claim','No PostgreSQL T098 claim','No formal task verdict','25 fault/legacy/security prerequisites still require dedicated setup']}
  await writeFile('evaluation/OFFLINE_PREFLIGHT.json',JSON.stringify(report,null,2)+'\n')
  console.log(JSON.stringify(report,null,2))
}
