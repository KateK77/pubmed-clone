# Changelog

## 2.0.0-r2 — 2026-11-15

- Fixed profile persistence, blank password validation, stale success messages and expired-session recovery.
- Isolated application cookies and user-specific client caches. Separated password changes from ordinary profile edits.
- Added configurable SMTP verification codes for registration and email changes, with unique email reservations, expiration, attempt limits and single-use consumption.
- Preserved NCBI author suffixes in article details and all citation formats, including refreshed legacy library records.
- Added a Windows setup/start script, Docker packaging and same-origin production frontend/API serving.
- Added real account browser regressions, production WSGI smoke checks and PostgreSQL/container CI validation.
- Preserved original requirements, manual feedback and Round 2 results. Public hosting and real SMTP service setup remain external configuration steps.

## 0.1.0-r1 — 2026-11-13

- Added live PubMed search, advanced Boolean builder, filters, article details, and relationships.
- Added accounts, bookmarks, collections, saved queries, and search history.
- Added individual and batch citations in five formats.
- Added backend, frontend, browser, and live integration checks.
