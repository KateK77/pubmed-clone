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
