"""Render the frozen evaluation inventory; never infer a verdict from model prose."""
import argparse
from collections import Counter
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
STATUSES = ('PASS', 'FAIL', 'BLOCKED', 'ERROR', 'NOT_RUN')
LEVELS = {'Easy': 30, 'Medium': 40, 'Hard': 20, 'Expert': 10}

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def escape(value):
    return str(value).replace('|', '\\|').replace('\n', '<br>')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--reviewed-results', type=Path)
    args = parser.parse_args()
    suite_path = ROOT / 'final_test_cases_100.json'
    suite_hash = hashlib.sha256(suite_path.read_bytes()).hexdigest()
    suite = read(suite_path)
    tests = suite if isinstance(suite, list) else suite['tests']
    assert [t['id'] for t in tests] == [f'T{i:03}' for i in range(1, 101)]
    assert Counter(t['difficulty'] for t in tests) == Counter(LEVELS)
    destination = ROOT / 'final_results_100.json'
    if args.reviewed_results:
        supplied = read(args.reviewed_results)
        assert supplied['suite_sha256'] == suite_hash, 'Results must match frozen suite'
        results = supplied['results']
        assert {r['id'] for r in results} == {t['id'] for t in tests}
        assert len(results) == 100
        for result in results:
            assert result['status'] in STATUSES
            if result['status'] in ('PASS', 'FAIL'):
                assert result.get('model_requests', 0) > 0, 'No verdict without native execution'
                assert result.get('independent_review'), 'Model prose is not independent review'
                assert result.get('evidence'), 'PASS/FAIL require recorded evidence'
        metadata = supplied['metadata']
    else:
        if destination.exists() and any(r['status'] != 'NOT_RUN' for r in read(destination)['results']):
            raise SystemExit('Refusing to overwrite actual execution records with an empty inventory')
        results = [dict(id=t['id'], status='NOT_RUN', actual_outcome='尚未执行原生 CUA 任务。',
                        reason='等待 API 配置核查、前置就绪审查及用户明确的付费执行批准。',
                        duration_seconds=None, model_requests=0, actions=0,
                        input_tokens=0, output_tokens=0, evidence=[], attempts=[])
                   for t in tests]
        metadata = dict(description='Round 3 / V3 consolidated Description',
                        description_sha256='19f1b6ae980962d19c472a390a141757675ba611b3f8a6168e1ac9faf825f391',
                        application_commit='03a7dc2a349a3f26bc1712c79d77957cf9338a1a',
                        planned_cua_model='gpt-6.1-sol', cua_model_used=None,
                        model_requests=0, total_cua_actions=0, api_input_tokens=0,
                        api_output_tokens=0, native_execution_seconds=0,
                        actual_api_cost_usd=0, paid_inference_calls=0,
                        cost_note='尚无付费推理调用；准备工作和本地适配器检查不计入 CUA 用量。')
    counts = Counter(r['status'] for r in results)
    valid = counts['PASS'] + counts['FAIL']
    executed = any(r.get('model_requests', 0) > 0 for r in results)
    primary = counts['PASS'] if executed else None
    valid_rate = round(counts['PASS'] / valid * 100, 2) if valid else None
    output = dict(stage='COMPLETE' if valid == 100 else 'INCOMPLETE' if executed else 'PRE_EXECUTION_NOT_FINAL',
                  evaluation_complete=valid == 100, suite_sha256=suite_hash,
                  generated_at=datetime.now(ZoneInfo('America/Chicago')).isoformat(),
                  total=100, counts={s: counts[s] for s in STATUSES},
                  primary_overall_pass_rate_percent=primary,
                  validly_evaluated_pass_rate_percent=valid_rate,
                  rate_note='正式主通过率为 PASS/100；未执行时不展示软件成绩。受阻/错误/未运行不算通过。',
                  metadata=metadata, results=results)
    destination.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lookup = {r['id']: r for r in results}
    with (ROOT/'summary.csv').open('w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['ID','Difficulty','Category','Task','Expected','Actual','Status','Reason',
                         'Seconds','CUA actions','Model requests','Input tokens','Output tokens','Evidence'])
        for test in tests:
            result = lookup[test['id']]
            writer.writerow([test['id'],test['difficulty'],test['category'],test['task'],test['expected_result'],
                result.get('actual_outcome',''),result['status'],result.get('reason',''),result.get('duration_seconds'),
                result.get('actions',0),result.get('model_requests',0),result.get('input_tokens',0),
                result.get('output_tokens',0),'; '.join(result.get('evidence',[]))])
    lines = ['# MedResearch V3 最终评估报告', '',
             '**阶段：尚未执行 / 非最终成绩。**' if not executed else
             ('**阶段：完整评估。**' if valid == 100 else '**阶段：不完整评估。**'), '',
             '本报告只统计这套冻结的 100 项原生 CUA 任务；已有 CI、适配器检查和旧 Playwright 结果全部排除。', '',
             '## A. Overall Results', '', 'Total: **100**', '']
    lines += [f'- {status}: **{counts[status]}**' for status in STATUSES]
    lines += ['', f'Overall Pass Rate: **{primary if primary is not None else "未计算（未执行）"}{"%" if primary is not None else ""}**',
              f'Validly evaluated pass rate: **{valid_rate if valid_rate is not None else "N/A（无有效评估）"}{"%" if valid_rate is not None else ""}**', '',
              '主分母固定 100；有效评估分母为 PASS+FAIL。零执行不应被解读为软件 0% 通过或 100% 失败。', '',
              '## B. Difficulty-Based Results', '',
              '| Difficulty | Total | Passed | Failed | Blocked | Error | Not run | Pass Rate |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for level, total in LEVELS.items():
        subset = [lookup[t['id']] for t in tests if t['difficulty'] == level]
        c = Counter(r['status'] for r in subset)
        rate = f'{c["PASS"]/total*100:.2f}%' if executed else '—'
        lines.append(f'| {level} | {total} | {c["PASS"]} | {c["FAIL"]} | {c["BLOCKED"]} | {c["ERROR"]} | {c["NOT_RUN"]} | {rate} |')
    lines += ['', '### 按功能领域', '', '| 领域 | 总数 | PASS | FAIL | BLOCKED | ERROR | NOT_RUN | 通过率 |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
    for category in dict.fromkeys(t['category'] for t in tests):
        subset = [lookup[t['id']] for t in tests if t['category'] == category]
        c = Counter(r['status'] for r in subset)
        rate = f'{c["PASS"]/len(subset)*100:.2f}%' if executed else '—'
        lines.append('| '+escape(category)+' | '+str(len(subset))+' | '+' | '.join(str(c[s]) for s in STATUSES)+' | '+rate+' |')
    lines += ['', '## C. Detailed Test Results', '']
    for test in tests:
        result = lookup[test['id']]
        lines += [f'### {test["id"]} · {test["difficulty"]} · {test["task"]}', '',
                  f'- 领域：{test["category"]}', f'- 预期：{test["expected_result"]}',
                  f'- 实际：{result.get("actual_outcome", "待独立核查")}', f'- 状态：**{result["status"]}**',
                  f'- 原因：{result.get("reason", "无")}',
                  '- 证据：'+('; '.join(result.get('evidence',[])) or '无；尚无原生 CUA 执行证据。'), '']
    lines += ['## D. Failure Analysis', '',
              '未执行时，缺失功能、功能错误、UI/UX、权限与校验、CUA 导航错误均**未评估**，不能从准备阶段推断产品失败。',
              '基础设施就绪情况与受阻前置见准备记录；任何适配器故障重试不计作正式应用测试。', '',
              '## E. Evaluation Metadata', '', '```json', json.dumps(metadata,ensure_ascii=False,indent=2), '```', '',
              f'冻结测试集 SHA-256：`{suite_hash}`。', '',
              '[全部任务](FINAL_TEST_CASES.md) · [JSON 结果](final_results_100.json) · [CSV](summary.csv) · [执行预算](EXECUTION_PLAN.md)', '']
    (ROOT/'FINAL_EVALUATION_REPORT.md').write_text('\n'.join(lines),encoding='utf-8')
    print(json.dumps({'total':100,'stage':output['stage'],'counts':output['counts'],'suite_sha256':suite_hash}))

if __name__ == '__main__':
    main()
