# Architecture

The frontend retains query, page, page size, sort, and filter values in the URL. TanStack Query keeps public requests and user-keyed library requests separate. Session cookies stay on the same origin. Every authenticated mutation uses Django’s CSRF checks, and registration and login require a CSRF token before an account exists.

```text
React SPA -> /api/ -> Django REST Framework -> NCBI E-utilities
                          |
                          +-> Django ORM -> SQLite / PostgreSQL
                          |
                          +-> Django cache -> TTL-based upstream responses
```

`literature/query.py` validates query shape and converts filter selections into PubMed clauses. Filters are ORed within a facet and ANDed across facets. Excluding preprints adds a separate NOT clause. The advanced builder folds conditions from left to right using parentheses. An All fields row accepts its own parenthesized expression.

`literature/ncbi.py` sends POST requests to ESearch, EFetch, ELink, and ESummary. ESearch supplies the original count and the current batch of PMIDs. EFetch metadata is restored to that order even if NCBI returns records in a different sequence. Related and cited-by requests use different ELink names and a batched ESummary. Best Match uses `relevance`, Most Recent uses the ESearch default entry order, and Publication Date uses `pub_date`. HTTP 429, upstream server errors, and network errors have bounded retries. Cache keys are derived from public parameters. An incomplete article page is flagged for the user.

Django’s User owns Bookmark, Collection, SearchHistory, and SavedSearch records. Publication uses PMID as its primary key and stores normalized metadata and a retrieval timestamp. CollectionPublication and Bookmark enforce uniqueness in the database. Article metadata is saved on demand when a user bookmarks or files it. User-owned queries always filter by the authenticated user, including collection citation exports.

References: [E-utilities parameters](https://www.ncbi.nlm.nih.gov/sites/books/NBK25499/) and [PubMed Help](https://pubmed.ncbi.nlm.nih.gov/help/).

## Version 2.0 accounts and metadata

The cookies are named `medresearch_sessionid` and `medresearch_csrftoken`, avoiding collisions with other local Django applications on different ports. Session responses are never cached. The client rechecks the session on focus and clears user-specific library cache entries when the account changes. Authentication failures carry a machine-readable code and restore the sign-in form. Unsaved profile edits remain in component memory while the profile page stays open and are restored only for the same user ID.

Profile changes and password changes use separate forms. Blank password fields from older clients do not invoke password validation. Errors name their fields, and success state is cleared when the user edits again. Successful profile responses update the session cache, while a reload obtains the persisted user record from Django.

`AccountEmail` reserves normalized email addresses with a unique database constraint and records verification time. `EmailChallenge` stores a purpose/user/address key, random nonce, keyed code digest, expiration, attempt count and delivery state. Delivery runs outside the database transaction. The code is only usable after the email backend reports success. Verification attempt increments persist even if account validation fails. Code consumption and account creation or email changes are atomic. Existing users are not forced through registration again.

NCBI author suffixes are preserved in normalized metadata and all five export formats. Versioned metadata identifies Round 1 saved records. Opening or exporting those records refreshes them in bounded PubMed batches before returning them, without external HTTP calls in database migrations. Unavailable refreshes return an upstream error rather than silently claiming the old metadata was corrected.

WhiteNoise serves built Vite assets through the WSGI entry point, and Django provides the SPA fallback outside `/api/` and `/assets/`. Docker builds React first, copies only the distribution into the Python image and starts Gunicorn as an unprivileged user. PostgreSQL is required for the documented public deployment.

## Version 3.0 account simplification

Password policy is a minimum of eight characters through Django's validator and a maximum of 128 through API serializers. The browser displays this policy on registration and password change. It does not enforce composition, common-password or similarity checks. Confirmation is validated before registration or password persistence; login keeps its existing authentication behavior. Password hashing, CSRF, verification-code limits and the production account throttle remain in place.

The Account UI retains only username, email, password change and sign out. Legacy name columns and compatible API fields remain to avoid deleting existing data. Successful authentication navigates to Search unless a permitted internal research URL requested authentication. A central destination parser allows known frontend paths and preserves query/hash values, while rejecting external, API and account destinations. An interrupted same-user email draft takes precedence over the ordinary redirect.

Browser tests run independent real accounts against a temporary database and mailbox. Because all parallel scenarios share one IP, only that disposable test server uses a higher global account throttle. A backend regression test checks the unchanged production limit of twenty attempts per minute. Per-address verification cooldowns remain active in browser tests.
