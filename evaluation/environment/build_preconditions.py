"""Map reviewed frozen tasks to setup capabilities; never changes test expectations."""
import argparse
import hashlib
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--suite', required=True)
parser.add_argument('--output', required=True)
parser.add_argument('--manifest')
parser.add_argument('--seed-dir')
parser.add_argument('--query-preflight')
args = parser.parse_args()
raw = Path(args.suite).read_bytes()
tests = json.loads(raw)
official = json.loads(Path(args.manifest).read_text(encoding='utf-8')) if args.manifest else None
query_preflight = json.loads(Path(args.query_preflight).read_text(encoding='utf-8')) if args.query_preflight else None
assert [t['id'] for t in tests] == [f'T{i:03}' for i in range(1, 101)]

# Explicit review of each case's frozen preconditions, not title-based inference.
accounts = {21,22,23,25,26,27,28,36,37,38,39,40,54,55,56,57,58,59,60,68,71,72,73,74,75,76,77,78,86,88,92,93,94,95,98,99,100}
authenticated = {22,23,25,26,27,28,36,37,40,54,55,56,57,58,59,60,68,71,72,73,74,75,77,86,92,93,94,95}
library = {22,26,38,57,58,59,60,68,72,73,74,86,92,94,95}
history = {56,72,94,95}
mail = {31,36,91,93}
mobile = {30,67,100}
manifest = {4,5,6,7,10,11,12,14,47,51,57,58,60,64,65,79,80,81,92,96}
pending = {
  35:['registration_confirmation_request_fault'],
  37:['password_confirmation_request_fault'],
  40:['controlled_session_expiry_after_email_draft'],
  70:['bounded_three_second_upstream_delay'],
  73:['known_private_collection_url_from_seed'],
  74:['object_id_request_rewrite'],
  75:['csrf_and_origin_request_rewrite'],
  76:['controlled_cookie_collision_probe','password_hash_readonly_audit'],
  77:['controlled_session_expiry_with_research_page_open'],
  78:['return_parameter_name_from_preflight_navigation'],
  79:['credible_round1_legacy_migration_fixture'],
  82:['upstream_timeout_and_explicit_release'],
  83:['upstream_429_retry_after_sequence','current_ncbi_rate_limit_reference'],
  84:['upstream_503_and_explicit_release'],
  85:['partial_xml_record_fault','observable_cache_state'],
  86:['reversible_isolated_database_transaction_fault'],
  87:['configurable_60_second_cache_ttl','outbound_request_and_cache_auditor'],
  88:['synthetic_server_key_and_secret_auditor','upstream_503_fault'],
  89:['malformed_xml_fault_and_release'],
  90:['pagination_parameter_request_rewrite'],
  93:['controlled_session_expiry_multitab'],
  94:['controlled_session_expiry_after_private_draft'],
  95:['upstream_503_with_existing_private_library'],
  96:['credible_round1_legacy_migration_fixture'],
  97:['fixed_query_filter_count_at_least_150'],
  98:['isolated_postgresql','controlled_app_restart_without_database_reset','postgres_readonly_state_auditor'],
  99:['api_contract_network_auditor'],
}

mapping = {'suite_sha256': hashlib.sha256(raw).hexdigest(), 'application_commit': '03a7dc2a349a3f26bc1712c79d77957cf9338a1a',
    'status': 'precondition_readiness_review_not_test_results',
    'scope_note': 'Actor readiness does not imply final grading readiness. No test has executed. Required fixture inputs and independent oracles must be established before their corresponding judgment.',
    'cases': {}}
for test in tests:
    number = int(test['id'][1:])
    mode = 'smtp' if number == 31 else 'mail' if number in mail else 'unavailable' if number == 38 else 'standard'
    fixture = 'accounts' if number in accounts else 'demo' if number == 24 else 'empty'
    requirements = ['authenticated' if number in authenticated else 'anonymous']
    if fixture == 'accounts': requirements.append('synthetic_accounts')
    if fixture == 'demo': requirements.append('demo_account')
    if fixture == 'empty': requirements.append('empty_database')
    if mode == 'mail': requirements.append('email_file_mailbox')
    if mode == 'smtp': requirements.append('smtp_mailbox')
    if mode == 'unavailable': requirements.append('email_unavailable')
    if number in library: requirements.append('seeded_library')
    if number in history: requirements.append('seeded_history')
    if number in {29,49,61,73,78,99}: requirements.append('trusted_browser_navigation')
    missing = list(pending.get(number, []))
    if number in manifest: missing.append('required_official_manifest_slots')
    if number in library or number in history: missing.append('reviewed_case_specific_seed_state')
    if number in {18,20,63}: missing.append('fixed_query_count_preflight')
    profile = {'ready': not missing, 'ready_for_actor': not missing, 'ready_for_final_grading': False,
      'reviewed_against_frozen_suite': True, 'mode': mode, 'fixture': fixture,
      'requires': requirements, 'start_path': '/',
      'viewport': {'width':390,'height':844} if number in mobile else {'width':1440,'height':900},
      'instructions': 'Execute only the frozen task. Preconditions: ' + ' '.join(test['preconditions'][1:]),
      'frozen_preconditions': test['preconditions'],
      'pending_preconditions': missing,
      'grading_dependencies': [test['independent_oracle']],
      'reason': 'Pending setup: ' + ', '.join(missing) if missing else 'Core local actor setup supported; independent grading remains mandatory.'}
    if number in authenticated: profile['auth_user'] = 'eva_b' if number in {73,74} else 'eva_a'
    if number in library or number in history: profile['seed_state_file'] = f'evaluation/fixtures/setup/{test["id"]}.json'
    if number == 16: profile['start_path'] = '/search?q=cancer%20immunotherapy'
    if number in {21,23,24,32,33,34,35,36,37,38,40,76,79,93,94,96}: profile['start_path'] = '/profile'
    mapping['cases'][test['id']] = profile

if official:
    base = official['BASE']['pmid']
    three = official['LIBRARY3']['pmids']
    per_case_slots = {4:['DOI'],5:['BASE'],6:['BASE'],7:['BASE'],10:['META','REFERENCES','CITED_BY'],
      11:['ABSENT_ABSTRACT'],12:['RELATED'],14:['FREE','PUBLISHER','ABSTRACT_ONLY'],47:['PREPRINT'],
      51:['BASE'],57:['LIBRARY3','BASE'],58:['LIBRARY3'],60:['LIBRARY3'],64:['ABSENT_FIELDS'],65:['SUFFIX'],
      79:['SUFFIX'],80:['LONG','UNICODE','EDATE'],81:['NO_RELATED'],92:['LIBRARY55'],96:['SUFFIX']}
    for number, slots in per_case_slots.items():
        profile = mapping['cases'][f'T{number:03}']
        if all(official.get(slot, {}).get('status') == 'ready' for slot in slots):
            profile['pending_preconditions'].remove('required_official_manifest_slots')
            values = {}
            for slot in slots:
                record = official[slot]
                values[slot] = {key: record[key] for key in ['pmid','pmids'] if key in record}
                metadata = record.get('metadata', {})
                values[slot].update({key: metadata[key] for key in ['title','doi','journal','year','mesh'] if key in metadata})
                authors = metadata.get('authors', [])
                values[slot]['author_count'] = len(authors)
                personal = next((author for author in authors if author.get('last_name')), None)
                if personal:
                    values[slot]['first_personal_author'] = ' '.join(filter(None, [personal.get('fore_name'), personal.get('last_name'), personal.get('suffix')]))
                values[slot]['author_suffixes'] = sorted({author['suffix'] for author in authors if author.get('suffix')})
            profile['resolved_fixture_inputs'] = values
            profile['instructions'] += '\nFrozen official fixture inputs: ' + json.dumps(values, ensure_ascii=False)
    seeds = {}
    def seed(number, **state):
        seeds[f'T{number:03}'] = {'reviewed_preconditions': True, 'suite_sha256': mapping['suite_sha256'], **state}
    def bookmark(owner, pmid): return {'owner':owner,'pmid':pmid}
    def collection(owner, name, pmids): return {'owner':owner,'name':name,'pmids':pmids}
    seed(22, bookmarks=[bookmark('eva_a',base)])
    seed(26, bookmarks=[bookmark('eva_a',base),bookmark('eva_b',three[1])])
    seed(38, bookmarks=[bookmark('eva_a',base)], collections=[collection('eva_a','EVA Existing Research',[base])])
    seed(57, bookmarks=[bookmark('eva_a',p) for p in three])
    seed(58, bookmarks=[bookmark('eva_a',p) for p in three[:2]] + [bookmark('eva_b',three[2])])
    seed(59, collections=[collection('eva_a','EVA Rename',[base])])
    seed(60, collections=[collection('eva_a','EVA Working',[])])
    seed(68, collections=[collection('eva_a','EVA Keyboard',[])])
    seed(73, collections=[collection('eva_a','EVA A Private',[base])])
    seed(74, collections=[collection('eva_a','EVA A Private',[base]),collection('eva_b','EVA B Private',[three[1]])])
    seed(86, collections=[collection('eva_a','EVA DB Original',three[:2])])
    seed(92, collections=[collection('eva_a','EVA Evidence Set',official['LIBRARY55']['pmids'])])
    if query_preflight:
        counts = {item['query']: item['count'] for item in query_preflight['queries'] if item['prerequisite_ready']}
        def history_row(owner, query, day):
            return {'owner':owner,'query':query,'filters':{},'sort':'publication','count':counts[query],
                    'created_at':f'2026-11-{day:02}T12:00:00+00:00'}
        if all(term in counts for term in ['diabetes','cancer','hypertension']):
            seed(56, history=[history_row('eva_a',q,day) for q,day in [('diabetes',12),('cancer',13),('hypertension',14)]] + [history_row('eva_b','cancer',14)])
            for number in [72,94]:
                seed(number, bookmarks=[bookmark('eva_a',base),bookmark('eva_b',three[1])],
                     collections=[collection('eva_a','EVA A Private',[base]),collection('eva_b','EVA B Private',[three[1]])],
                     history=[history_row('eva_a','diabetes',13),history_row('eva_b','cancer',14)])
            seed(95, bookmarks=[bookmark('eva_a',p) for p in three[:2]],
                 collections=[collection('eva_a','EVA Offline Recovery',three[:2])],
                 history=[history_row('eva_a','diabetes',14)])
    seed_dir = Path(args.seed_dir) if args.seed_dir else Path(args.output).parent / 'setup'
    seed_dir.mkdir(parents=True, exist_ok=True)
    for ident, state in seeds.items():
        (seed_dir / (ident+'.json')).write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        profile = mapping['cases'][ident]
        profile['pending_preconditions'].remove('reviewed_case_specific_seed_state')
    p = mapping['cases']['T073']
    p['pending_preconditions'].remove('known_private_collection_url_from_seed')
    p['collection_targets'] = [{'owner':'eva_a','name':'EVA A Private','label':'eva_a.private_collection_url'}]
    mapping['official_manifest_file'] = 'evaluation/data/manifest.json'
    mapping['official_manifest_sha256'] = hashlib.sha256(Path(args.manifest).read_bytes()).hexdigest()
    mapping['cases']['T058']['instructions'] += '\nFrozen saved sets: eva_a=' + ', '.join(three[:2]) + '; eva_b-only=' + three[2]

if query_preflight:
    for number in [18,20,63,97]:
        ident = f'T{number:03}'
        data = [row for row in query_preflight['queries'] if ident in row['test_ids']]
        if data and all(row['prerequisite_ready'] for row in data):
            profile = mapping['cases'][ident]
            profile['pending_preconditions'] = [item for item in profile['pending_preconditions'] if item not in ['fixed_query_count_preflight','fixed_query_filter_count_at_least_150']]
            profile['query_count_preflight'] = [{key:row[key] for key in ['query','count','prerequisite_ready']} for row in data]
    mapping['query_preflight_sha256'] = hashlib.sha256(Path(args.query_preflight).read_bytes()).hexdigest()

for profile in mapping['cases'].values():
    missing = profile['pending_preconditions']
    profile['ready'] = profile['ready_for_actor'] = not missing
    profile['reason'] = 'Pending setup: ' + ', '.join(missing) if missing else 'Core local actor setup supported; independent grading remains mandatory.'

output = Path(args.output)
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(mapping, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
ready = sum(p['ready_for_actor'] for p in mapping['cases'].values())
lines = ['# Precondition readiness review', '', '**This is infrastructure readiness, not application test results or a pass rate.**', '',
    f'Frozen suite SHA-256: `{mapping["suite_sha256"]}`.', '',
    f'{ready}/100 cases currently have core actor setup supported; {100-ready}/100 need the explicit setup listed below. All 100 still require independent grading. Credentials configuration, model availability, paid budget approval and normal live NCBI availability are additional execution gates.', '',
    '| Case | Actor setup | Explicit pending setup |', '|---|---|---|']
for ident, p in mapping['cases'].items():
    lines.append(f'| {ident} | {"Supported" if p["ready_for_actor"] else "Pending"} | {", ".join(p["pending_preconditions"]) or "—"} |')
output.with_suffix('.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'Wrote {len(tests)} explicit profiles; core actor setup supported for {ready}; no test execution.')
