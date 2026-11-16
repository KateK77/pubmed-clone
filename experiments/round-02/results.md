# Round 2 results — MedResearch 2.0

Date: 2026-11-15 (America/Chicago). Agent: Codex. Exact model build identifier was unavailable.

Implementation commit: `214403c65be03ee260c5b1102ac00b27c4d0c622`. Release tag: `v2.0.0-r2`. The tag also includes this report and release metadata. Round 1 history and `v0.1.0-r1` are preserved.

## Delivery

The application retains the complete React/TypeScript/Vite and Django/DRF foundation, real NCBI E-utilities search, Boolean query builder, filters, metadata, related records, citation exports and private research library. This round implements the changes recorded during user acceptance testing. The complete original prompt, Round 2 scope and eleven feedback records are preserved alongside this report.

| Feedback | Resolution and evidence |
| --- | --- |
| Profile appears signed in but saving is unauthenticated | Application-specific cookies avoid collisions with other local Django apps. Session responses are not cached. Expired-session errors return the sign-in form, and an in-page draft can be restored after the same user signs in. Verified against real Django in desktop and mobile browsers. |
| Blank-field error and contradictory save success | Profile/password forms are separate. Empty password fields from older clients are accepted for ordinary profile updates. Errors retain field labels and editing clears prior mutation status. Saving fields disables editing until the result arrives. |
| First name disappears after refresh | Real browser checks save First name, reload, sign out, sign back in and check persistence. Server tests verify both names and ensure failed password changes do not partially save profile edits. |
| Demo username appears in Email | Inputs use purpose-specific autocomplete attributes. The original screenshot alone did not establish whether browser autofill or application data caused the value. The upgraded local profile was checked visually without writing a replacement email. |
| Independent accounts and email codes | Optional SMTP verification for registration and email changes, normalized unique email reservation, hashed single-use codes, cooldown, expiration, attempt limits and CSRF. Existing users remain usable. Tests use a temporary mailbox rather than an external email service. |
| Author suffix omitted from detail, APA and RIS | NCBI Suffix is preserved in author display and all five formats. Legacy saved metadata refreshes on read/export. Live PMID 31452104 confirms `Jr` in metadata, APA and RIS. |
| Remaining functionality reported passed | User's aggregate acceptance is recorded separately from automated verification. Existing discovery, query, library, ownership and export regression coverage remains. |
| Visitors open a GitHub link to the website | Docker, same-origin production frontend/API serving and deployment instructions are included. No hosting account, public endpoint or SMTP provider was supplied. Code is on GitHub; public hosting remains unprovisioned. |

## Validation

| Command / check | Result |
| --- | --- |
| `python -m pytest -q` | 37 passed locally on SQLite. GitHub CI also passed all 37 on SQLite and PostgreSQL 16. |
| `python backend/manage.py check` | Passed. |
| `python backend/manage.py makemigrations --check --dry-run` | No changes detected. |
| `python backend/manage.py spectacular --validate --file openapi.yaml` | Schema generated and validated. |
| `npm --prefix frontend test` | 2 passed. |
| `npm --prefix frontend run build` | TypeScript and Vite production build passed. |
| `npm --prefix frontend run e2e` | 8 passed locally using Edge Chromium at desktop/mobile viewports. GitHub CI passed with Chromium. Four discovery cases use fixtures; four account cases use real Django and an isolated database/mailbox. |
| `python tests/deployment_smoke.py` | Production WSGI served SPA routes, assets and API. HTTPS redirect, secure CSRF cookie, unknown API/asset routes and frontend refresh were verified. Also passed in CI. |
| `python tests/live_smoke.py` | Real ESearch/EFetch/ELink/ESummary returned PMID 31452104, preserved Jr, eight related records and 9,073 matches for asthma + Review + last five years. Counts are a point-in-time observation. |
| GitHub container job | Docker build passed. |
| Local upgrade | Existing SQLite database backed up before migration. Three accounts and one bookmark preserved. New migration applied. Existing demo sign-in and desktop/mobile profile layout checked on port 5184. |
| PowerShell setup script | Syntax parsed. Script resolves relative project files from its own directory. Clean-machine dependency installation was not repeated locally. |

All three jobs passed in [implementation CI run 43796453541](https://github.com/KateK77/pubmed-clone/actions/runs/43796453541).

The first parallel account browser run was intermittent. Subsequent runs passed; SQLite now starts atomic write transactions in IMMEDIATE mode so competing local writes wait for the configured timeout. A separate sandboxed browser launch could not start its test server and was rerun successfully outside that sandbox. A lowercase Review value in the new smoke script was corrected to the API's documented `Review` value before the successful live run.

## Running and upgrading

See the [README](../../README.md) for installation, exact commands, environment variables and demo credentials. The Windows entry point is `start.ps1 -Service setup`, followed by `-Service backend` and `-Service frontend` in separate terminals. The local example explicitly permits registration without email verification. The production deployment guide requires PostgreSQL, HTTPS and SMTP for verified registration.

The new cookie names require one new login after upgrading. The application does not delete or recreate existing users, bookmarks or collections. Database backups and test mailboxes are local work artifacts and are not pushed to GitHub.

## Remaining limits

- No public application URL has been provisioned. GitHub source publication is complete, but visitors cannot use a hosted website until an application host and database are configured.
- The verification workflow is implemented and tested with local test mail. Delivery to a real inbox through an external SMTP provider has not been verified.
- GitHub repository visibility remains private, as originally requested. Its visibility was not changed during this round.
- PubMed's first 10,000 matches are accessible per query. Related panels show at most eight records each. The NCBI limiter is process-local, so the documented deployment uses one worker/replica.
- Citation output uses available metadata and has no formal style-conformance certification. Legacy saved metadata refresh requires NCBI availability.
- No live cloud deployment or production-scale load test was performed. Docker construction, PostgreSQL regression tests and production WSGI smoke checks passed.
