# Final evaluation: isolated environment

This directory provides infrastructure only. It does not contain acceptance tests,
does not drive browser interactions, and makes no OpenAI API calls. Native CUA
execution must wait for the owner's explicit cost/budget approval. The frozen V3
test suite determines expected behavior; implementation details read during this
setup are used only to configure the environment.

## Evaluated application

- Application commit: `03a7dc2a349a3f26bc1712c79d77957cf9338a1a` (V3 plus deployment documentation).
- `prepare` archives that exact Git revision into `.runtime/source`. It does not
  edit the application's tracked files or copy a working `.env`.
- The frontend is rebuilt after verifying tracked frontend files match the pinned
  revision. The snapshot includes the built assets and their SHA-256 manifest.
- Existing development server `8014`, frontend `5184`, Render, Neon and their data
  are not used or reset. Evaluation HTTP binds only `127.0.0.1:8124`.
- The configuration-only settings overlay retains the application's middleware,
  views, validation, templates and migrations. It selects local SQLite, in-memory
  cache, local HTTP and file email. It changes no product logic. `DEBUG=True`
  and local HTTP are infrastructure choices: this environment cannot establish
  production HTTPS, secure-cookie, HSTS, production-error-page or deployment
  security compliance. Such requirements need a separately approved production-
  equivalent configuration; do not infer them from this local run.
- `DATABASE_URL`, `POSTGRES_*`, SMTP credentials and NCBI credentials are cleared
  before Django imports. `.env` loading is disabled, the source snapshot has no
  `.env`, and the final database configuration is asserted to be the case SQLite.

## Prepare once

Prerequisites: Python with `backend/requirements.txt` installed; Node with the
repository frontend dependencies already installed. Commands below assume these
files are placed in `evaluation/environment/` in the repository:

```powershell
$Python = 'C:\absolute\path\to\evaluation-venv\Scripts\python.exe'
& $Python .\evaluation\environment\environment.py prepare --repo .
```

If `npm.cmd` is not on PATH, add `--npm-cli C:\absolute\path\to\npm-cli.js`.
The snapshot cannot silently be replaced. Prepare a separate infrastructure
directory for a different application revision and record the changed baseline.
`prepare` rebuilds ignored `frontend/dist`; it does not modify application source.

## Reset before each test

Stop the prior evaluation browser, app and mailbox first. The reset command
refuses to run while any evaluation port (8124–8127) is in use. Never kill a process only
because its port matches; identify it as the evaluation process first.

```powershell
& $Python .\evaluation\environment\environment.py reset --case T001 --mode standard --fixture empty
```

Use `--fixture accounts` only when frozen preconditions need existing users. It
creates verified synthetic `eva_a` and `eva_b` at `@medresearch.test`, each with a
separate empty private collection. The native lifecycle obtains the frozen
`AUTH.initial` value from an ignored local-only `synthetic_credentials_file`
(`{"initial_password":"<frozen synthetic AUTH.initial value>"}`), passed to reset
only through the child process environment. Direct manual reset without that
environment value uses random passwords for infrastructure preflight. Credentials stay in the case's ignored
`credentials.local.json`; do not copy them into reports, action logs or Git.
No publication metadata is invented; empty/account-only fixtures contain none. Literature always comes from
the live NCBI path unless a specifically documented external fault is injected.

For cases with explicitly frozen existing research, `--state-file <reviewed.json>`
can seed private relations. The JSON must set `reviewed_preconditions:true` and
may provide `bookmarks:[{owner,pmid}]`,
`collections:[{owner,name,pmids:[]}]`,
`history:[{owner,query,filters,sort,count,created_at}]`, and
`saved_searches:[{owner,query,filters,sort,created_at}]`. Owners are restricted to
the two synthetic users. Actual publication records are fetched from NCBI by the
fixed PMIDs; a missing record blocks setup. This uses the application parser only
to populate a compatible fixture, never to define expected metadata; independent
grading still compares against the separate frozen official manifest. Synthetic
history counts/timestamps are fixture data, not claims that CUA performed those
searches. `--auth-user eva_a` / `eva_b` creates a synthetic Django session and
ignored browser storage state, solely when the frozen precondition requires an
already authenticated user. Authentication tests themselves remain anonymous.

Each reset affects only `.runtime/cases/<case>/`: SQLite, generated Django secret,
mail, downloads, browser profile and private credentials. All paths are validated
to stay under this dedicated runtime. Previous evidence must be copied into the
evaluation evidence directory before resetting the same ID again. A repeated run
must be explicitly recorded as a retry, not silently replace its earlier result.

## Start the actual application

```powershell
& $Python .\evaluation\environment\environment.py serve --case T001
```

Open `http://127.0.0.1:8124` in a **new isolated CUA browser context/profile**.
Use `.runtime/cases/T001/browser-profile/` and the case downloads directory if the
native harness needs persistent folders. Do not reuse the user's ordinary browser
or the context used for localhost `8014`. Cookies are not port-isolated; the
frontend expects the ordinary CSRF cookie name, so a dedicated profile is
essential. Both session and CSRF cookie names are preserved from the application.
The harness must
close contexts and stop both services before reset. `Ctrl+C` stops a foreground
service. If started as a background child, stop only the child process handle
created by the harness, with hidden windows on Windows.

## Email-code scenarios

For frozen cases requiring verification, select `--mode mail`; this enables the
unchanged product email-code flow and Django's local file mailbox. Start its
viewer in a separate terminal:

```powershell
& $Python .\evaluation\environment\environment.py reset --case T031 --mode mail --fixture empty
& $Python .\evaluation\environment\environment.py serve --case T031
# Separate terminal:
& $Python .\evaluation\environment\environment.py mail --case T031
```

CUA can open `http://127.0.0.1:8125` in another tab, refresh, read the synthetic
message from a screenshot, and type its code into the real application. The
viewer is evaluation infrastructure; it serves only that case's local mail,
escapes message text, has no arbitrary-file route, and binds loopback only.
Standard mode also uses file email but does not require verification at signup.

File mode proves local email-code behavior, **not SMTP transport or real inbox delivery**.
A V3 test demanding real external delivery needs its own approved service and
prerequisites; otherwise it remains BLOCKED. Mailbox code screenshots should be
retained only as synthetic evidence after the challenge expires; never commit
live secrets, private browser storage or passwords.

### Isolated real SMTP transport for T031

`--mode smtp` configures the unchanged Django SMTP email backend to connect to
`127.0.0.1:8127`. The `smtp --case T031` command starts a loopback capture receiver
that accepts only `.test` recipients, writes raw received messages into that
case's mailbox and never forwards mail. Start `serve`, `smtp`, and `mail` for the
same reset case in separate processes; the lifecycle hook manages these exact
children automatically. The mailbox remains visible on 8125. This is real local
SMTP transport, independently preflighted with Django `send_mail`, and is
distinct from file mode. It does not prove any external provider or real-person
inbox delivery. The preflight message itself was synthetic infrastructure data,
not a registration or acceptance test.

## Independent verification

```powershell
& $Python .\evaluation\environment\environment.py capture --case T001 --output .\evaluation\logs\T001-state.json
```

This reads SQLite through `mode=ro` and exports an allowlist: synthetic users and
emails, article IDs, collection ownership, saved queries, history, challenge
attempt/delivery/timestamps, and session count. It excludes passwords, password
hashes, challenge digests/nonces/codes, session keys/bodies, and Django secrets.
It does not decide pass/fail. A verifier must compare the final state against the
frozen expected outcome and compare before/after captures when relevant.
No verifier may create successful state on behalf of the CUA agent.

## Infrastructure preflight (not an acceptance test)

```powershell
& $Python .\evaluation\environment\environment.py reset --case preflight --mode standard --fixture accounts
& $Python .\evaluation\environment\environment.py preflight --case preflight
& $Python .\evaluation\environment\environment.py capture --case preflight
```

Preflight starts its own exact child process, reads only `/api/health/`, then
terminates that child. It neither registers through the UI nor executes a test
task. A successful health check must never be counted toward the 100 CUA results.

## External fault injection: design only

No faults are active. When a frozen recovery test requires one, the harness may
use an isolated browser/network context to abort one selected request, or a
separately documented local proxy to fail a bounded upstream request. The CUA
still chooses all clicks/typing. Record target URL pattern, start/end time,
injection mechanism and restoration evidence. Do not change application source,
replace NCBI search results with fabricated literature, modify another service,
or use a broad system firewall rule. Distinguish the intended outage from test
infrastructure errors. Timeout/expiry fixtures must be documented before running
the relevant frozen case; do not alter expected outcomes after observation.

## Sensitive and durable artifacts

Commit only the infrastructure code, this document, frozen tests, sanitized
results, action logs and reviewed screenshots. `.runtime/` must remain ignored.
Never commit its source snapshot, SQLite, private credentials, generated secrets,
mail files, browser profiles or raw session state. No paid API request is made by
any command here. No application acceptance test has been executed by this setup.

## Native harness lifecycle hooks

`lifecycle.mjs` exports `prepare`, `verify` and `cleanup` for the native harness.
It performs no CUA calls or scripted browser tasks. Set these additional harness
configuration keys before execution:

```json
{
  "environment_python": "C:/absolute/path/to/venv/Scripts/python.exe",
  "preconditions_file": "evaluation/case_preconditions.json",
  "synthetic_credentials_file": "<ignored local-only JSON file>"
}
```

The preconditions file must be reviewed against the **frozen** suite and contain
its exact SHA-256, with an explicit entry for every supported case. No entry is
inferred from application code, a case title or a category. A missing entry, a
`ready:false` entry, unsupported requirements, or an unprepared source snapshot
returns BLOCKED before any model request. Example structure (not a mapping of
actual frozen test IDs):

```json
{
  "suite_sha256": "<frozen-suite-hash>",
  "cases": {
    "T001": {
      "ready": true,
      "reviewed_against_frozen_suite": true,
      "mode": "standard",
      "fixture": "empty",
      "requires": ["anonymous", "empty_database", "live_ncbi"],
      "start_path": "/",
      "instructions": "<reviewed precondition notes; not task execution>"
    }
  }
}
```

Supported capabilities are `anonymous`, `authenticated`, `empty_database`,
`synthetic_accounts`, `empty_private_collections`, `live_ncbi`,
`email_file_mailbox`, `email_unavailable`, `demo_account`, `seeded_library`,
`seeded_history`, `seeded_saved_searches`, `smtp_mailbox`, and `trusted_browser_navigation`.
Authentication requires an explicit profile `auth_user`; seeded research requires
`seed_state_file`. `mode: unavailable` uses unconfigured SMTP with required
verification, so the product can demonstrate its actual unavailable-email path.
`fixture: demo` invokes the delivered local demo setup command. Specially expired
codes, external fault injection, external real-recipient SMTP, and production-security assertions
are deliberately unsupported until
their exact frozen preconditions receive an explicit implementation/review.

`prepare` resets only that test's synthetic case, starts exact hidden child
processes, waits for local health, and returns credentials only in private CUA
instructions plus `secrets` for log redaction. `verify` captures a read-only state
snapshot and appends evidence but **never assigns PASS/FAIL automatically**.
`cleanup` takes a final snapshot and stops only the children it spawned. The
native harness must close its isolated browser context before invoking cleanup.
Precondition setup logs and sanitized state captures may be evidence; do not log
the returned `instructions`, `secrets`, or raw prepared object.

Both file and SMTP mailbox profiles remain BLOCKED unless the harness explicitly supports native
CUA navigation to the viewer and configuration includes
`allowed_local_origins: ["http://127.0.0.1:8125"]` and
`mailbox_navigation_supported: true`. These flags are assertions of implemented,
reviewed infrastructure support, not a way to bypass missing functionality.

## Trusted navigation and clipboard fixture

The reviewed `trusted_browser_navigation` capability starts a separate loopback
service on `8126`, which must be in `allowed_local_origins`. It provides a real
HTML URL form and real Go/new-tab links. CUA decides which URL to type and which
button to click; the fixture validates the exact local/official origin allowlist
then redirects the actual browser. It never invokes a task workflow, reads
product DOM, injects scripts into the product, or accesses arbitrary files.
It substitutes isolated browser navigation chrome because headless page captures
do not include a native address bar. Reports must identify it as evaluation
infrastructure, not product functionality.

The harness may write only the last observed application URL to
`prepared.navigation_state_file` as an independent read-only observation. Refresh
the navigation tab to display that value; it is filtered by the same allowlist.
The clipboard pad accepts native Ctrl+V. Pasted pad content alone is insufficient
evidence of a correct copy operation; the independent verifier must compare the
actual clipboard with the frozen citation oracle. No clipboard contents, URLs
with secrets, browser profiles, or session values are automatically committed.
