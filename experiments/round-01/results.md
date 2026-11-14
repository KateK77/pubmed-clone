# Round 1 results

Date: 2026-11-13 (America/Chicago). Model family: GPT-6 Codex. Exact model build was unavailable.

The source revision is recorded in metadata.json. The release tag v0.1.0-r1 includes this report and the original specification.

## Implemented

- Live PubMed discovery, server-side pagination and sorting, URL filters, advanced search, and query translation.
- Publication details, abstracts, metadata, PMC and DOI links, similar publications, references, and cited-by links.
- Session authentication, CSRF, profile management, private bookmarks and collections, search history, and saved queries.
- APA, MLA, Vancouver, BibTeX, and RIS citation copy or export for individual records and research sets.
- Django migrations, generated OpenAPI schema, SQLite and PostgreSQL configuration, README, and GitHub Actions configuration.

## Validation

| Command or workflow | Result |
| --- | --- |
| `python -m pytest -q` | 28 passed with mocked upstream responses on SQLite. |
| `python backend/manage.py check` | Passed. |
| `python backend/manage.py makemigrations --check --dry-run` | No changes detected. |
| `python backend/manage.py spectacular --validate --file openapi.yaml` | Generated and validated. |
| `npm --prefix frontend run build` | TypeScript and Vite build passed. |
| `npm --prefix frontend test` | 2 passed. |
| `npm --prefix frontend run e2e -- --workers=2` | 4 passed using Edge Chromium at desktop and mobile viewports with mocked API responses. |
| `python tests/live_smoke.py` | ESearch, EFetch, ELink, and ESummary returned the expected PMID 31452104 and eight related records. |
| Live Django HTTP smoke | Filtered asthma query returned 9,061 matches and ten records on page 2. Local demo sign-in passed. |

## Limits

- ESearch exposes the first 10,000 PubMed results. The result count remains the upstream total.
- Related and cited-by panels show up to eight records per relationship. PMC and DOI metadata determine direct full-text destinations. Publisher-specific LinkOut discovery is not implemented.
- Citation formats use the available metadata, with plain-text APA, MLA, and Vancouver output. No formal style-conformance certification was performed.
- The built-in NCBI request limiter applies within one server process. PostgreSQL checks are configured for CI. Local verification used SQLite.
- The release includes a local runnable application and private source repository. No hosted application environment was created.
- These are development results. The independent benchmark has not been run.
