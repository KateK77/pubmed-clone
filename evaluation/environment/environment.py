"""Isolation infrastructure only. No CUA calls or scripted browser test actions."""
import argparse
import hashlib
import html
import io
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import socket
import socketserver
import sqlite3
import subprocess
import sys
import tarfile
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.request import urlopen
from urllib.parse import urlparse, parse_qs

HERE = Path(__file__).resolve().parent
RUNTIME = HERE / '.runtime'
PINNED_COMMIT = '03a7dc2a349a3f26bc1712c79d77957cf9338a1a'
SOURCE = RUNTIME / 'source'

def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')

def checked_case(name):
    if not re.fullmatch(r'(?:T\d{3}|preflight)[a-zA-Z0-9_-]*', name):
        raise ValueError('Use T001..T100 or preflight, with optional safe suffix.')
    path = (RUNTIME / 'cases' / name).resolve()
    if not path.is_relative_to((RUNTIME / 'cases').resolve()):
        raise ValueError('Case path must stay inside the evaluation runtime.')
    return path

def port_free(port):
    with socket.socket() as sock:
        try:
            sock.bind(('127.0.0.1', port))
        except OSError:
            raise RuntimeError(f'Port {port} is in use. Stop only the corresponding evaluation service; do not kill unrelated services.')

def configure(case):
    path = checked_case(case)
    config = json.loads((path / 'case.json').read_text(encoding='utf-8'))
    # Clear inherited production credentials before importing Django.
    for key in list(os.environ):
        if key.startswith(('POSTGRES_', 'DJANGO_', 'EMAIL_', 'NCBI_', 'RENDER_')) or key in ('DATABASE_URL', 'DEFAULT_FROM_EMAIL'):
            del os.environ[key]
    os.environ.update({'PYTHON_DOTENV_DISABLED': '1', 'DATABASE_URL': '', 'POSTGRES_DB': '',
        'DJANGO_SETTINGS_MODULE': 'eval_settings', 'EVALUATION_CASE_DIR': str(path),
        'EVALUATION_SOURCE_DIR': str(SOURCE), 'EVALUATION_MODE': config['mode']})
    sys.path[:0] = [str(HERE), str(SOURCE / 'backend')]
    import django
    django.setup()
    from django.conf import settings
    assert settings.DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3'
    assert Path(settings.DATABASES['default']['NAME']).resolve() == path / 'evaluation.sqlite3'
    return path

def prepare(args):
    repo = Path(args.repo).resolve()
    if SOURCE.exists():
        raise RuntimeError('Source snapshot already exists. Reuse it; do not silently replace the evaluated version.')
    revision = subprocess.check_output(['git', '-C', str(repo), 'rev-parse', args.commit], text=True).strip()
    if revision != PINNED_COMMIT:
        raise RuntimeError('This environment is pinned to the approved application commit.')
    # Verify frontend source corresponds to the pinned revision before building.
    subprocess.run(['git', '-C', str(repo), 'diff', '--exit-code', revision, '--', 'frontend'], check=True)
    package = repo / 'frontend'
    npm = ['node', str(Path(args.npm_cli).resolve())] if args.npm_cli else ['npm.cmd' if os.name == 'nt' else 'npm']
    subprocess.run(npm + ['--prefix', str(package), 'run', 'build'], check=True)
    RUNTIME.mkdir(parents=True, exist_ok=True)
    SOURCE.mkdir()
    archived = subprocess.check_output(['git', '-C', str(repo), 'archive', revision])
    with tarfile.open(fileobj=io.BytesIO(archived)) as tar:
        tar.extractall(SOURCE, filter='data')
    shutil.copytree(package / 'dist', SOURCE / 'frontend' / 'dist')
    manifest = {str(p.relative_to(SOURCE)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (SOURCE / 'frontend' / 'dist').rglob('*') if p.is_file()}
    dump(RUNTIME / 'source-manifest.json', {'application_commit': revision,
        'frontend_build': 'npm run build, after git diff against pinned frontend succeeded',
        'frontend_sha256': manifest, 'production_env_copied': False})
    print('Prepared pinned application snapshot; no .env or production database copied.')

def reset(args):
    port_free(8124)
    port_free(8125)
    port_free(8126)
    port_free(8127)
    if not (SOURCE / 'backend' / 'manage.py').exists():
        raise RuntimeError('Run prepare first.')
    path = checked_case(args.case)
    # Destruction is restricted to this one synthetic test case, never the source or other cases.
    if path.exists():
        shutil.rmtree(path)
    for child in ['mail', 'browser-profile', 'downloads', 'logs']:
        (path / child).mkdir(parents=True, exist_ok=True)
    dump(path / 'case.json', {'case': args.case, 'mode': args.mode, 'fixture': args.fixture, 'auth_user': args.auth_user,
        'application_commit': PINNED_COMMIT, 'origin': 'http://127.0.0.1:8124'})
    (path / 'django-secret.txt').write_text(secrets.token_urlsafe(64), encoding='utf-8')
    configure(args.case)
    from django.core.management import call_command
    call_command('migrate', interactive=False, verbosity=0)
    if args.fixture == 'demo':
        call_command('create_demo', verbosity=0)
    if args.fixture == 'accounts':
        from django.contrib.auth import get_user_model
        from django.utils import timezone
        from literature.models import Collection, AccountEmail
        users = []
        for name in ['eva_a', 'eva_b']:
            username = name
            password = os.environ.get('EVALUATION_INITIAL_PASSWORD') or secrets.token_urlsafe(18)
            user = get_user_model().objects.create_user(username=username, password=password, email=f'{name}@medresearch.test')
            AccountEmail.objects.create(user=user, address=user.email, verified_at=timezone.now())
            Collection.objects.create(user=user, name=name + ' private collection')
            users.append({'username': username, 'password': password, 'email': user.email})
        dump(path / 'credentials.local.json', users)
    if args.state_file:
        seed_research_state(Path(args.state_file))
    if args.auth_user:
        if args.fixture != 'accounts':
            raise RuntimeError('Authenticated preconditions require the accounts fixture.')
        from importlib import import_module
        from django.conf import settings
        from django.contrib.auth import get_user_model
        user = get_user_model().objects.get(username=args.auth_user)
        session = import_module(settings.SESSION_ENGINE).SessionStore()
        session['_auth_user_id'] = str(user.pk)
        session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
        session['_auth_user_hash'] = user.get_session_auth_hash()
        session.save()
        dump(path / 'browser-state.local.json', {'cookies': [{
            'name': settings.SESSION_COOKIE_NAME, 'value': session.session_key,
            'domain': '127.0.0.1', 'path': '/', 'expires': int(time.time()) + settings.SESSION_COOKIE_AGE,
            'httpOnly': True, 'secure': False, 'sameSite': 'Lax'}], 'origins': []})
    print(f'Reset {args.case}: isolated SQLite, {args.mode} mode, {args.fixture} fixture. Credentials are local-only.')

def seed_research_state(filename):
    """Synthetic private relations only; publication metadata is fetched live."""
    from django.contrib.auth import get_user_model
    from django.db import transaction
    from django.utils.dateparse import parse_datetime
    from literature import ncbi
    from literature.models import Publication, Bookmark, Collection, CollectionPublication, SearchHistory, SavedSearch
    state = json.loads(filename.read_text(encoding='utf-8'))
    if state.get('reviewed_preconditions') is not True:
        raise RuntimeError('Research fixture must be explicitly reviewed against the frozen preconditions.')
    pmids = set()
    for item in state.get('bookmarks', []):
        pmids.add(str(item['pmid']))
    for item in state.get('collections', []):
        pmids.update(str(value) for value in item.get('pmids', []))
    if len(pmids) > 100 or any(not re.fullmatch(r'[1-9]\d{0,11}', pmid) for pmid in pmids):
        raise RuntimeError('Fixture PMID list invalid or too large.')
    actual = ncbi.fetch(sorted(pmids, key=int)) if pmids else []
    if {item['pmid'] for item in actual} != pmids:
        raise RuntimeError('Required fixture records were not all returned by official NCBI; do not fabricate them.')
    def owner(name):
        if name not in ['eva_a', 'eva_b']:
            raise RuntimeError('Fixture owner must be one of the synthetic accounts.')
        return get_user_model().objects.get(username=name)
    with transaction.atomic():
        for record in actual:
            Publication.objects.create(pmid=record['pmid'], title=record['title'], journal=record['journal'],
                doi=record['doi'], pmcid=record['pmcid'], publication_date=record['date'],
                abstract='\n'.join(part['text'] for part in record['abstract']), metadata=record)
        for item in state.get('bookmarks', []):
            Bookmark.objects.get_or_create(user=owner(item['owner']), publication_id=str(item['pmid']))
        for item in state.get('collections', []):
            collection, _ = Collection.objects.get_or_create(user=owner(item['owner']), name=item['name'])
            for pmid in item.get('pmids', []):
                CollectionPublication.objects.get_or_create(collection=collection, publication_id=str(pmid))
        for key, model in [('history', SearchHistory), ('saved_searches', SavedSearch)]:
            for item in state.get(key, []):
                values = {'user': owner(item['owner']), 'query': item['query'],
                    'filters': item.get('filters', {}), 'sort': item.get('sort', 'best')}
                if key == 'history':
                    values['count'] = item['count']
                created = model.objects.create(**values)
                if item.get('created_at'):
                    instant = parse_datetime(item['created_at'])
                    if instant is None or instant.tzinfo is None:
                        raise RuntimeError('Synthetic history timestamps must be explicit ISO timestamps with timezone.')
                    model.objects.filter(pk=created.pk).update(created=instant)

def serve(args):
    port_free(8124)
    configure(args.case)
    from django.core.management import call_command
    call_command('runserver', '127.0.0.1:8124', use_reloader=False)

def mail(args):
    path = checked_case(args.case) / 'mail'
    if not path.is_dir():
        raise RuntimeError('Reset a case before opening its mailbox.')
    port_free(8125)
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != '/':
                self.send_error(404)
                return
            entries = []
            for f in sorted(path.glob('*.log'), key=lambda f: f.stat().st_mtime, reverse=True):
                entries.append('<article><h2>' + html.escape(f.name) + '</h2><pre>' + html.escape(f.read_text(encoding='utf-8', errors='replace')) + '</pre></article>')
            body = ('<!doctype html><meta charset="utf-8"><title>Evaluation mailbox</title>'
                '<style>body{font:18px sans-serif;max-width:1000px;margin:30px auto}pre{white-space:pre-wrap;background:#eef;padding:16px}</style>'
                '<h1>Isolated evaluation mailbox</h1><p>Synthetic local mail only. Refresh to read new messages.</p>'
                + (''.join(entries) or '<p>No messages yet.</p>')).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, format, *values):
            pass
    print('Local synthetic mailbox: http://127.0.0.1:8125', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8125), Handler).serve_forever()

def capture(args):
    path = checked_case(args.case)
    db = path / 'evaluation.sqlite3'
    connection = sqlite3.connect(db.as_uri() + '?mode=ro', uri=True)
    connection.row_factory = sqlite3.Row
    queries = {
        'users': 'SELECT id,username,email,first_name,last_name,is_active,is_staff,is_superuser FROM auth_user ORDER BY id',
        'emails': 'SELECT user_id,address,verified_at FROM literature_accountemail ORDER BY user_id',
        'bookmarks': 'SELECT user_id,publication_id FROM literature_bookmark ORDER BY user_id,publication_id',
        'publications': 'SELECT pmid,title,journal,doi,publication_date FROM literature_publication ORDER BY pmid',
        'collections': 'SELECT id,user_id,name FROM literature_collection ORDER BY id',
        'collection_articles': 'SELECT collection_id,publication_id FROM literature_collectionpublication ORDER BY collection_id,publication_id',
        'saved_searches': 'SELECT user_id,query,filters,sort,created FROM literature_savedsearch ORDER BY id',
        'history': 'SELECT user_id,query,filters,sort,count,created FROM literature_searchhistory ORDER BY id',
        'challenge_summary': 'SELECT attempts,delivered,sent_at,expires_at FROM literature_emailchallenge ORDER BY sent_at',
        'session_summary': 'SELECT COUNT(*) AS total FROM django_session',
    }
    result = {'case': args.case, 'application_commit': PINNED_COMMIT, 'readonly_verifier': True,
              **{key: [dict(row) for row in connection.execute(sql)] for key, sql in queries.items()}}
    configure(args.case)
    from importlib import import_module
    from django.conf import settings
    decoder = import_module(settings.SESSION_ENGINE).SessionStore()
    # Decode in memory to verify identity but never output session secrets or hashes.
    result['authenticated_sessions'] = [
        {'user_id': decoder.decode(row['session_data']).get('_auth_user_id'), 'expires': row['expire_date']}
        for row in connection.execute('SELECT session_data,expire_date FROM django_session')]
    connection.close()
    target = Path(args.output).resolve() if args.output else path / 'logs' / 'state.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    dump(target, result)
    print('Saved sanitized read-only state capture (no passwords, hashes, codes, session keys or session bodies).')

def navigator(args):
    """Trusted browser infrastructure; never queries or edits application state."""
    case = checked_case(args.case)
    config = json.loads((case / 'navigation-config.local.json').read_text(encoding='utf-8'))
    local_origins = {'http://127.0.0.1:8124', 'http://127.0.0.1:8125', 'http://127.0.0.1:8126'}
    official_hosts = set(config.get('external_hosts', []))
    def allowed(value):
        try:
            parsed = urlparse(value)
            origin = f'{parsed.scheme}://{parsed.netloc}'
            return not parsed.username and not parsed.password and not any(char in value for char in '\r\n') and (
                origin in local_origins or (parsed.scheme == 'https' and parsed.hostname in official_hosts))
        except ValueError:
            return False
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == '/go':
                value = parse_qs(parsed.query).get('url', [''])[0]
                if not allowed(value):
                    self.send_error(400, 'URL is outside the reviewed evaluation allowlist')
                    return
                self.send_response(302)
                self.send_header('Location', value)
                self.send_header('Cache-Control', 'no-store')
                self.end_headers()
                return
            if parsed.path != '/':
                self.send_error(404)
                return
            try:
                current = json.loads((case / 'browser-current-url.local.json').read_text(encoding='utf-8')).get('url', '')
            except (OSError, ValueError):
                current = ''
            if not allowed(current):
                current = ''
            body = ('''<!doctype html><meta charset="utf-8"><title>Evaluation browser navigation</title>
<style>body{font:18px sans-serif;max-width:1000px;margin:24px auto;padding:0 16px}input,textarea{font:inherit;width:95%;padding:10px;margin:10px 0}button{font:inherit;padding:10px;margin:8px}label{display:block}aside{background:#eef;padding:14px}</style>
<h1>Evaluation browser navigation</h1><aside>This is trusted evaluation infrastructure, not the MedResearch product. The CUA agent must choose and type every destination. Only reviewed local and official literature origins are allowed.</aside>
<p>Switch tabs with Ctrl+Tab / Ctrl+Shift+Tab. Refresh this page to update the last observed application URL.</p>
<label>Last observed application URL<input readonly aria-label="Last observed application URL" value="''' + html.escape(current, quote=True) + '''"></label>
<form action="/go" method="get"><label>Destination URL<input name="url" type="url" required autocomplete="off" placeholder="http://127.0.0.1:8124/..."></label><button type="submit">Go in this tab</button><button type="submit" formtarget="_blank">Open in new tab</button></form>
<label>Clipboard verification pad<textarea rows="6" placeholder="Paste using native Ctrl+V. The independent verifier must also check the actual clipboard; typed text alone is not proof."></textarea></label>''').encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'")
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        def log_message(self, format, *values):
            pass
    port_free(8126)
    print('Trusted evaluation navigation: http://127.0.0.1:8126', flush=True)
    ThreadingHTTPServer(('127.0.0.1', 8126), Handler).serve_forever()

def smtp(args):
    """A loopback SMTP sink for synthetic .test recipients; never forwards mail."""
    mailbox = checked_case(args.case) / 'mail'
    if not mailbox.is_dir():
        raise RuntimeError('Reset a case before starting SMTP.')
    class Handler(socketserver.StreamRequestHandler):
        def handle(self):
            def reply(message):
                self.wfile.write(message.encode('ascii') + b'\r\n')
                self.wfile.flush()
            recipient = False
            reply('220 localhost evaluation SMTP sink')
            while True:
                raw = self.rfile.readline(8192)
                if not raw:
                    return
                command = raw.decode('ascii', errors='replace').strip()
                verb = command.split(' ', 1)[0].upper()
                if verb in ('EHLO', 'HELO'):
                    reply('250-localhost')
                    reply('250-SIZE 1048576')
                    reply('250 8BITMIME')
                elif verb == 'MAIL':
                    recipient = False
                    reply('250 Sender accepted')
                elif verb == 'RCPT':
                    match = re.search(r'<([^<>]+)>', command)
                    if not match or not match.group(1).lower().endswith('.test'):
                        reply('550 Evaluation sink accepts only synthetic .test recipients')
                    else:
                        recipient = True
                        reply('250 Synthetic recipient accepted')
                elif verb == 'DATA':
                    if not recipient:
                        reply('503 A synthetic recipient is required')
                        continue
                    reply('354 End with a single dot')
                    chunks = []
                    size = 0
                    while True:
                        line = self.rfile.readline(65536)
                        if line in (b'.\r\n', b'.\n'):
                            break
                        if not line:
                            return
                        if line.startswith(b'..'):
                            line = line[1:]
                        chunks.append(line)
                        size += len(line)
                        if size > 1048576:
                            reply('552 Message too large')
                            return
                    (mailbox / f'smtp-{time.time_ns()}.log').write_bytes(b''.join(chunks))
                    recipient = False
                    reply('250 Message captured locally; never forwarded')
                elif verb == 'QUIT':
                    reply('221 Goodbye')
                    return
                elif verb in ('RSET', 'NOOP'):
                    if verb == 'RSET':
                        recipient = False
                    reply('250 OK')
                else:
                    reply('502 Unsupported evaluation SMTP command')
    class Server(socketserver.ThreadingTCPServer):
        daemon_threads = True
    port_free(8127)
    print('Loopback synthetic SMTP sink: 127.0.0.1:8127 (no external delivery)', flush=True)
    with Server(('127.0.0.1', 8127), Handler) as server:
        server.serve_forever()

def preflight(args):
    port_free(8124)
    path = checked_case(args.case)
    logfile = path / 'logs' / 'preflight-server.log'
    with logfile.open('w', encoding='utf-8') as log:
        process = subprocess.Popen([sys.executable, '-u', str(HERE / 'environment.py'), 'serve', '--case', args.case],
            stdout=log, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        try:
            for _ in range(30):
                if process.poll() is not None:
                    raise RuntimeError('Evaluation service exited; inspect preflight-server.log.')
                try:
                    with urlopen('http://127.0.0.1:8124/api/health/', timeout=2) as response:
                        if json.load(response) == {'status': 'ok'}:
                            print('PASS infrastructure preflight: isolated service health returned ok. No application acceptance test executed.')
                            return
                except OSError:
                    time.sleep(0.5)
            raise RuntimeError('Health preflight timed out.')
        finally:
            process.terminate()  # Only the exact child process started above.
            process.wait(timeout=15)

def main():
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare')
    p.add_argument('--repo', required=True)
    p.add_argument('--commit', default=PINNED_COMMIT)
    p.add_argument('--npm-cli')
    for name in ['reset', 'serve', 'mail', 'navigator', 'smtp', 'capture', 'preflight']:
        p = commands.add_parser(name)
        p.add_argument('--case', required=True)
        if name == 'reset':
            p.add_argument('--mode', choices=['standard', 'mail', 'smtp', 'unavailable'], default='standard')
            p.add_argument('--fixture', choices=['empty', 'accounts', 'demo'], default='empty')
            p.add_argument('--auth-user', choices=['eva_a', 'eva_b'])
            p.add_argument('--state-file')
        if name == 'capture':
            p.add_argument('--output')
    args = parser.parse_args()
    globals()[args.command](args)

if __name__ == '__main__':
    main()
