# MedResearch

MedResearch searches live biomedical literature from PubMed and gives researchers a personal library for bookmarks, collections, saved searches, and citation exports. It is an independent educational prototype with no affiliation with PubMed, NCBI, NIH, or the National Library of Medicine.

## Features

- Search by keyword, author, title, journal, PMID, DOI, or PubMed field syntax. Combine Boolean groups in the advanced builder and inspect PubMed’s translated query.
- Filter by date, article type, text availability, language, species, MEDLINE, or preprint exclusion. URL parameters preserve filters, sort, and pages.
- Read article metadata, structured abstracts, affiliations, keywords, MeSH descriptors, references, and available similar or citing records. Follow links to PubMed, PMC, and DOI destinations.
- Register, sign in, update your profile, bookmark articles, manage private collections, and rerun or save searches.
- Export selected articles, all bookmarks, or an entire collection in APA, MLA, Vancouver, BibTeX, or RIS. Copy a citation from the article page.

## Architecture

React, TypeScript, Vite, Tailwind CSS, React Router, and TanStack Query provide the browser interface. Django REST Framework exposes session and literature APIs. The NCBI service sends ESearch queries, fetches ordered batches via EFetch, and loads ELink relationships with ESummary. Django persists accounts and library records in SQLite locally or PostgreSQL in production. See [architecture](docs/architecture.md) for the data model and operating details.

## Run locally

Install Python 3.12+ and Node.js 22.12+ with npm. From the repository root in PowerShell:

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

## Configuration

| Variable | Purpose |
| --- | --- |
| `DJANGO_DEBUG` | Set `0` in production. Default `1`. |
| `DJANGO_SECRET_KEY` | Set a strong unique secret in production. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated Django hosts. |
| `DJANGO_TRUST_PROXY` | Set `1` only behind a trusted HTTPS proxy that overwrites `X-Forwarded-Proto`. |
| `DJANGO_CACHE_TABLE` | Optional database-backed Django cache. Run `python backend/manage.py createcachetable` after configuring it. |
| `NCBI_EMAIL` | Operator contact sent to NCBI. Set for shared deployments. |
| `NCBI_API_KEY` | Optional server-side NCBI credential. |
| `NCBI_CACHE_SECONDS` | E-utilities cache TTL. Default 900. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT` | PostgreSQL connection settings. Setting the database name enables PostgreSQL. |
| `MEDRESEARCH_API_TARGET` | Optional Vite proxy target. Default `http://127.0.0.1:8014`. |

Build with `npm --prefix frontend run build`. In production, serve `frontend/dist` with a SPA fallback and proxy `/api/` to Django on the same HTTPS origin. Apply migrations before starting a WSGI server with `medresearch.wsgi:application` from `backend/`. Use one upstream request process to keep the built-in NCBI limiter within the configured quota. The generated OpenAPI schema is available at `/api/schema/`. `/api/health/` checks database connectivity.

## Tests

```text
python -m pytest -q
python backend/manage.py check
python backend/manage.py makemigrations --check --dry-run
python backend/manage.py spectacular --validate --file openapi.yaml
npm --prefix frontend test
npm --prefix frontend run build
cd frontend
npx playwright install chromium
cd ..
npm --prefix frontend run e2e
python tests/live_smoke.py
```

The first three test suites use deterministic fixtures. The smoke test uses the live network. For manual validation, search `31452104`, open the record, and inspect its related articles. Search `asthma`, apply Review and a publication date filter, go to the next page, then use browser Back. Sign in, save the article, create a collection, add the article, and export the collection as RIS. Verify that search history replays the same filter state. Use a second account to confirm that the first account’s collection URL is inaccessible.

## Limits

- PubMed reports the complete count and exposes the first 10,000 results per query for pagination.
- Related and cited-by panels show up to eight records per relationship, subject to what ELink returns. Full-text links are derived from PMC IDs and DOI metadata. Publisher availability varies.
- Citations are plain-text renderings and bibliographic exports. Metadata availability determines which fields can be included. Dedicated selected-ID exports accept up to 200 PMIDs per request.
- Search history shows the most recent 500 entries. The bundled limiter is process-local. A shared multi-process deployment needs centralized request pacing.
- Clinical interpretation and treatment decisions are outside the prototype’s scope.
