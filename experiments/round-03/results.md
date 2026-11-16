# Round 3 results — MedResearch 3.0

Date: 2026-11-15 (America/Chicago). Agent: Codex. Exact model build identifier was unavailable.

Implementation commit: `cc4e2c214706fb712cd3e0a8e9358e6a75cf4d1f`. Release tag: `v3.0.0-r3`. The tag also includes this validation report and metadata. Previous source history and release tags are preserved.

## Consolidated requirements

The user reported difficulty registering because the password rejection did not explain the policy. They requested a visible simple rule, password confirmation and removal of First name/Last name. They then reported that the other functions passed and authorized a new version. These requirements now lead the [complete consolidated prompt](description.md), with all earlier prompts retained as the historical baseline. [Manual feedback](manual-feedback.json) preserves all fourteen records, including the latest three.

## Implemented behavior

- Password inputs show the 8–128-character requirement before submission. No uppercase, digit, symbol, common-password or username-similarity restriction is imposed.
- Registration and password changes include Confirm password. Both browser and API reject missing or mismatched confirmation with a specific correction message. Ordinary login uses existing credentials without confirmation.
- The Account page contains username, email, password change and sign out. Name inputs are removed. Existing database names and compatible API fields remain without any destructive migration.
- Successful registration and ordinary sign-in go straight to Search. Authentication links from research pages preserve the intended internal path, query and hash. Unsafe or unsupported destinations fall back to Search.
- If a session expires during email editing, signing back into the same account on that page restores the email draft. A different user does not inherit it.
- Existing email verification, CSRF, password hashing, per-email code limits, the production account throttle and private library checks remain. PubMed discovery and citations are unchanged.

## Local validation

| Check | Result |
| --- | --- |
| `python -m pytest -q` | 48 passed on SQLite. New cases cover simple/numeric/common passwords, length boundaries, confirmation errors, unchanged password on failed update, existing-account login and the production 20/min account throttle. |
| `python backend/manage.py check` | Passed. |
| `python backend/manage.py makemigrations --check --dry-run` | No changes detected; no new schema migration required. |
| `python backend/manage.py spectacular --validate --file openapi.yaml` | Generated and validated the Version 3 schema. |
| `npm --prefix frontend run build` | TypeScript and Vite build passed. |
| `npm --prefix frontend test` | 11 passed, including allowed return destinations and rejection of external/API/account destinations. |
| `npm --prefix frontend run e2e` | 8 passed using Edge Chromium on desktop/mobile viewports. Four discovery cases use fixtures; four account cases use real Django, isolated SQLite and a local test mailbox. |
| Account browser coverage | Simple-password verified registration, visible requirements, confirmation mismatch, direct Search redirect, absence of name inputs, password change and relogin, return to a private page with URL state, persistent verified email updates, session/draft recovery and collection isolation. |
| `python tests/deployment_smoke.py` | Production WSGI routes/assets/API, HTTPS redirect and secure cookie checks passed. |
| `python tests/live_smoke.py` | Live PMID 31452104, author suffix and citation checks, eight related records and 9,073 filtered asthma results passed. Count is a point-in-time observation. |
| Local application check | Restarted the owned backend on 8014; existing demo login redirects to Search on 5184. Registration and minimal Account screenshots inspected at desktop/mobile widths. No user profiles or libraries were overwritten. |

Parallel browser scenarios share one IP, so the disposable browser-test server has a higher global throttle. Production still uses 20 attempts/minute, covered by a dedicated regression. Verification cooldowns remain unchanged in those browser tests.

All three jobs passed in [GitHub CI run 43799414636](https://github.com/KateK77/pubmed-clone/actions/runs/43799414636) for the implementation commit. Backend tests passed on both SQLite and PostgreSQL 16 (48 each). The frontend build, 11 unit tests, 8 Chromium browser tests and production WSGI smoke check passed. The Docker image built successfully.

## Running and remaining limits

The [README](../../README.md) contains installation, exact startup commands, environment variables, demo credentials, API confirmation fields and manual acceptance checks. The Windows entry point remains `start.ps1 -Service setup`, with `-Service backend` and `-Service frontend` in separate terminals.

This release publishes source to the existing private GitHub repository. Public hosting and an external SMTP service have not been provisioned. Email verification is tested with local mailboxes, not a real recipient inbox. The existing PubMed pagination, relationship limits, process-local rate limiter and plain-text citation limitations remain documented in the README. The user's report that other features passed is recorded as user acceptance rather than independently reproduced evidence for every feature.
