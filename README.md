# MedResearch 2.0

MedResearch searches live biomedical literature from PubMed and gives researchers a personal library for bookmarks, collections, saved searches, and citation exports. It is an independent educational prototype with no affiliation with PubMed, NCBI, NIH, or the National Library of Medicine.

Version 2.0 combines the [original specification and revised requirements](experiments/round-02/description.md) with the owner's [manual testing feedback](experiments/round-02/manual-feedback.json). It fixes profile persistence, session recovery, field errors and author suffixes, and adds configurable email verification and a production container.

**Deployment status:** this repository contains the software. A public website URL has not been provisioned. Publishing the code to GitHub does not start the Django server. See [deployment instructions](docs/deployment.md) to host the application and add its public URL to the GitHub repository's About section.

## Features

- Search by keyword, author, title, journal, PMID, DOI, or PubMed field syntax. Combine Boolean groups in the advanced builder and inspect PubMed’s translated query.
- Filter by date, article type, text availability, language, species, MEDLINE, or preprint exclusion. URL parameters preserve filters, sort, and pages.
- Read article metadata, structured abstracts, affiliations, keywords, MeSH descriptors, references, and available similar or citing records. Follow links to PubMed, PMC, and DOI destinations.
- Register, sign in, update your profile, bookmark articles, manage private collections, and rerun or save searches.
- Verify registration and email changes with single-use email codes when enabled. Keep existing accounts and their libraries through the upgrade. Profile and password changes have separate forms.
- Export selected articles, all bookmarks, or an entire collection in APA, MLA, Vancouver, BibTeX, or RIS. Copy a citation from the article page.

## Architecture

React, TypeScript, Vite, Tailwind CSS, React Router, and TanStack Query provide the browser interface. Django REST Framework exposes session and literature APIs. The NCBI service sends ESearch queries, fetches ordered batches via EFetch, and loads ELink relationships with ESummary. Django persists accounts and library records in SQLite locally or PostgreSQL in production. See [architecture](docs/architecture.md) for the data model and operating details.

## Run locally

Install Python 3.12+ and Node.js 22.12+ with npm. Open PowerShell in the folder containing this README, `backend` and `frontend`. The path is the cloned project folder, not your Windows home directory.

```powershell
.\start.ps1 -Service setup
```

Then run these commands in two separate PowerShell windows in that folder:

```powershell
.\start.ps1 -Service backend
```

```powershell
.\start.ps1 -Service frontend
```

The script also accepts an absolute path and resolves project files from its own location. If script execution is disabled, the equivalent manual setup is:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r backend/requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python backend/manage.py migrate
.\.venv\Scripts\python backend/manage.py create_demo
.\.venv\Scripts\python backend/manage.py runserver 127.0.0.1:8014
```

In another terminal:

```powershell
npm.cmd --prefix frontend ci
npm.cmd --prefix frontend run dev
```

Open [MedResearch](http://127.0.0.1:5184). On Linux or macOS, use `.venv/bin/python`, `cp`, and `npm`. Use the same browser hostname throughout the session.

The local demo account is `medresearch-demo` with password `LocalResearchDemo!26`. The seed command runs in development mode and leaves an existing demo password intact.

The example configuration disables mandatory email verification for local testing. With verification enabled, users must supply an email and a code, and registration remains unavailable until an email backend is configured. Production should use SMTP. Existing users can still log in and verify their email from Profile. No SMTP credential or test message is committed to this repository.

### Upgrade from Round 1

Back up the database, install the updated dependencies, run `python backend/manage.py migrate`, rebuild the frontend and restart both services. Do not replace an existing `.env` with the example. Add the email settings below explicitly. The migrations preserve accounts, saved articles and collections. Sign in again after upgrading because the session cookie now has an application-specific name. Legacy saved article metadata is refreshed from PubMed when opened or exported, preserving author suffixes such as `Jr`.

## Configuration

| Variable | Purpose |
| --- | --- |
| `DJANGO_DEBUG` | Set `0` in production. Default `1`. |
| `DJANGO_SECRET_KEY` | Set a strong unique secret in production. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated Django hosts. |
| `DJANGO_TRUST_PROXY` | Set `1` only behind a trusted HTTPS proxy that overwrites `X-Forwarded-Proto`. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated HTTPS origins, including the public website origin. |
| `DJANGO_HSTS_SECONDS` | HTTPS strict transport duration. Production default 3600. |
| `DJANGO_CACHE_TABLE` | Optional database-backed Django cache. Run `python backend/manage.py createcachetable` after configuring it. |
| `NCBI_EMAIL` | Operator contact sent to NCBI. Set for shared deployments. |
| `NCBI_API_KEY` | Optional server-side NCBI credential. |
| `NCBI_CACHE_SECONDS` | E-utilities cache TTL. Default 900. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | PostgreSQL connection settings. Setting the database name enables PostgreSQL. |
| `POSTGRES_SSLMODE` | PostgreSQL TLS mode. Use the value required by the database provider. |
| `EMAIL_VERIFICATION_REQUIRED` | Default `1`. The development example sets `0`. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL` | SMTP server, authentication and verified sender settings. |
| `EMAIL_USE_TLS`, `EMAIL_USE_SSL` | Enable the transport required by the email provider. Do not enable both. |
| `MEDRESEARCH_API_TARGET` | Optional Vite proxy target. Default `http://127.0.0.1:8014`. |

Build with `npm --prefix frontend run build`. The WSGI application serves the built frontend and `/api/` from one origin, including frontend route refreshes. The Dockerfile packages both. Apply migrations before starting the container. Use one application process to keep the built-in NCBI limiter within its quota. The generated OpenAPI schema is available at `/api/schema/`. `/api/health/` checks database connectivity. See [deployment](docs/deployment.md) for HTTPS, PostgreSQL, SMTP and GitHub link setup.

## Tests

```text
python -m pytest -q
python backend/manage.py check
python backend/manage.py makemigrations --check --dry-run
python backend/manage.py spectacular --validate --file openapi.yaml
npm --prefix frontend test
npm --prefix frontend run build
python tests/deployment_smoke.py
cd frontend
npx playwright install chromium
cd ..
npm --prefix frontend run e2e
python tests/live_smoke.py
```

Pytest and Vitest use deterministic fixtures. Playwright covers desktop and mobile discovery with fixture responses, plus real Django registration, verification, profile persistence, expired sessions and account isolation. Its temporary SQLite database and file-based test mailbox are separate from your local data. Set `MEDRESEARCH_TEST_PYTHON` to your virtual environment's Python path if `python` resolves elsewhere. The live smoke test contacts NCBI.

For manual validation, search `31452104`, open the record and inspect the author suffix `Jr`, citations and related articles. Search `asthma`, apply Review and a publication date filter, go to the next page, then use browser Back. Sign in, save the article, create a collection, add the article and export RIS. Change First name, save, refresh and sign in again to verify persistence. Use a second account to confirm that the first account's collection URL is inaccessible.

## Limits

- PubMed reports the complete count and exposes the first 10,000 results per query for pagination.
- Related and cited-by panels show up to eight records per relationship, subject to what ELink returns. Full-text links are derived from PMC IDs and DOI metadata. Publisher availability varies.
- Citations are plain-text renderings and bibliographic exports. Metadata availability determines which fields can be included. Dedicated selected-ID exports accept up to 200 PMIDs per request.
- Search history shows the most recent 500 entries. The bundled limiter is process-local. A shared multi-process deployment needs centralized request pacing.
- Clinical interpretation and treatment decisions are outside the prototype’s scope.
