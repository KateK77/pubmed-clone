"""Offline planning arithmetic, not measured CUA usage or acceptance results."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
suite = json.loads((ROOT/'final_test_cases_100.json').read_text(encoding='utf-8'))
prices = {'input': 2.5, 'cached_input': 0.25, 'output': 15}
levels = ['Easy','Medium','Hard','Expert']
# Each tuple is requests/task, mean TOTAL input/request incl. screenshot/tool/schema/
# frozen task/notes/action ledger, mean output/request. Hypotheses, not measurements.
assumptions = {
    'optimistic': [(4,2600,70),(7,3200,90),(9,3800,120),(14,4600,160)],
    'central': [(5,3000,80),(9,3800,110),(12,4600,140),(20,5800,200)],
    'higher_usage': [(8,3500,120),(14,4500,180),(20,5500,240),(32,7000,320)],
}
def price(i,o): return (i*prices['input']+o*prices['output'])/1e6
scenarios = {}
for label,values in assumptions.items():
    groups=[]
    for level,(requests,inp,out) in zip(levels,values):
        count=sum(t['difficulty']==level for t in suite)
        groups.append(dict(difficulty=level,tests=count,requests_per_test=requests,
            total_requests=count*requests,input_per_request=inp,output_per_request=out,
            input_tokens=count*requests*inp,output_tokens=count*requests*out,
            estimated_usd=round(count*requests*price(inp,out),6)))
    coverage={}
    for budget in (4,5,15):
        spent=0;finished=0
        # Fixed T001..T100 order, no cherry-picking. Keep one request's max-output
        # reserve beyond actual estimated output so a new request cannot overshoot.
        for test in suite:
            n,i,o=values[levels.index(test['difficulty'])]
            projected=n*price(i,o)
            if spent+projected+price(0,1024-o)>budget: break
            spent+=projected;finished+=1
        coverage[str(budget)]=dict(estimated_completed_attempts=finished,
            estimated_spend_usd=round(spent,6),assumes_all_prerequisites_ready=True,
            not_a_pass_count=True)
    scenarios[label]=dict(groups=groups,total_requests=sum(g['total_requests'] for g in groups),
        input_tokens=sum(g['input_tokens'] for g in groups),output_tokens=sum(g['output_tokens'] for g in groups),
        estimated_total_usd=round(sum(g['estimated_usd'] for g in groups),6),budget_coverage=coverage)

careflow=list(csv.DictReader((ROOT/'data/careflow-reference.csv').read_text(encoding='utf-8').splitlines()))
cf_input=sum(int(r['input_tokens']) for r in careflow)
cf_output=sum(int(r['output_tokens']) for r in careflow)
cf_requests=sum(int(r['requests']) for r in careflow)
reference=dict(source='https://github.com/KateK77/careflow-ehr/blob/docs/public-showcase-cua100/docs/testing/cua100-v1/results.csv',
    model='gpt-5.4',tasks=len(careflow),requests=cf_requests,
    input_tokens=cf_input,output_tokens=cf_output,calculated_uncached_usd=price(cf_input,cf_output),
    average_requests_per_task=cf_requests/len(careflow),average_input_per_request=cf_input/cf_requests,
    average_output_per_request=cf_output/cf_requests,
    completed_actions=sum(int(r['completed_actions']) for r in careflow),
    csv_sha256=hashlib.sha256((ROOT/'data/careflow-reference.csv').read_bytes()).hexdigest())
report=dict(kind='unbenchmarked_offline_budget_forecast',paid_calls=0,approval=False,
    suite_sha256=hashlib.sha256((ROOT/'final_test_cases_100.json').read_bytes()).hexdigest(),
    model='gpt-5.4',service_tier='default',reasoning_effort='none',prices_per_million=prices,
    target_usd=4,maximum_acceptable_usd=5,active_stop_usd=4,
    model_metadata_accessible=True,native_api_compatibility_verified=False,
    screenshot_tokens=dict(desktop_1440x900=1566,mobile_390x844=422,careflow_1280x800=1200),
    extra_tool_fees_assumed_usd=0,
    extra_fee_note='Local browser only; no hosted container/web-search/file-search. Official tools table does not list a separate native computer surcharge; confirm account billing before paid execution. Not an invoice or tax-inclusive guarantee.',
    reference=reference,scenarios=scenarios,
    limitations=['No paid calibration; request and token quantities are explicit hypotheses',
      'A completed paid attempt is not a PASS; failures and infrastructure errors remain separate',
      'All 100 expectations unchanged; currently 25 case-specific prerequisites still pending',
      'Neither $15 nor $5 is authorization to spend; explicit approval remains required'])
(ROOT/'BUDGET_ESTIMATE.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'central':scenarios['central'],'reference':reference},indent=2))
