import assert from 'node:assert/strict'
import {readFile} from 'node:fs/promises'
import {taskEnvelope, initialInput, nextInput, ledgerTurn, tokenEstimate} from './efficient-context.mjs'
import {validateApproval, checkBudget} from './native-cua.mjs'
const config=JSON.parse(await readFile(new URL('../run-config.json',import.meta.url),'utf8'))
const suite=JSON.parse(await readFile(new URL('../final_test_cases_100.json',import.meta.url),'utf8'))
let checks=0
for(const test of suite){assert.deepEqual(JSON.parse(taskEnvelope(test,'notes',config.viewport,config.base_url)).frozen_test,test);checks++}
const task=taskEnvelope(suite[0],'notes',config.viewport,config.base_url)
const history=[], screenshot=n=>({type:'computer_call_output',call_id:'call'+n,output:{type:'computer_screenshot',image_url:'data:image/png;base64,image'+n,detail:'original'}})
let prior, input=initialInput(task,'first')
for(let turn=0;turn<80;turn++){
  if(prior)history.push(...ledgerTurn(prior))
  const output=[{type:'message',role:'assistant',content:[{type:'output_text',text:'Observed '+turn}]},
    {type:'computer_call',call_id:'call'+turn,actions:[{type:'click',x:turn,y:50}]}]
  input=nextInput(task,history,output,[screenshot(turn)])
  const serialized=JSON.stringify(input)
  assert.equal((serialized.match(/data:image/g)||[]).length,1)
  assert.ok(serialized.includes('Observed 0'))
  assert.deepEqual(JSON.parse(input[0].content).frozen_test,suite[0]);checks+=3
  prior=output
}
assert.throws(()=>nextInput(task,[],[{type:'computer_call',call_id:'missing'}],[screenshot(1)]),/pairing/);checks++
assert.throws(()=>nextInput(task,[],[{type:'reasoning'}],[]),/reasoning/);checks++
const usage=tokenEstimate({input_tokens:1000,output_tokens:100,input_tokens_details:{cached_tokens:600}},config.prices)
assert.equal(usage.uncached_upper_usd,0.004);checks++
assert.equal(usage.cache_adjusted_estimate_usd,0.00265);checks++
assert.throws(()=>tokenEstimate({input_tokens:10,output_tokens:1,input_tokens_details:{cached_tokens:11}},config.prices),/usage/);checks++
const approval={approved:true,user_statement:'TEST FIXTURE ONLY',approved_at:'fixture',model:config.model,max_usd:5,suite_sha256:'suite',config_sha256:'config'}
validateApproval(approval,config,'suite','config');checks++
assert.throws(()=>validateApproval(approval,{...config,total_usd:5.01},'suite','config'),/Budget/);checks++
assert.throws(()=>validateApproval({},config,'suite','config'),/approval/);checks++
const zero={model_requests:0,input_tokens:0,output_tokens:0,charged_upper_usd:0}
assert.throws(()=>checkBudget(zero,{...zero,charged_upper_usd:3.99},config,1000,1024),/budget/);checks++
console.log(JSON.stringify({kind:'offline_optimization_unit_checks',checks,passed:checks,formal_tests_executed:0,api_calls:0,cost_usd:0},null,2))
