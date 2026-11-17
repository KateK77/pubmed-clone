# MedResearch 3.0 — Complete Product Description

## 0. Development Objective

Develop MedResearch 3.0 as a complete biomedical literature search and research management application inspired by PubMed.

This document defines the complete requirements for version 3.0. Implement all specified workflows, including real literature retrieval, accounts, research organization and citation exports.

Use the existing repository and preserve its users, saved research, source history and previous release tags. Inspect the current implementation before changing it. Do not replace the application with a scaffold, mockup or limited MVP.

## 1. Project Identity

Project name: MedResearch

Version: 3.0.0

Reference website: https://pubmed.ncbi.nlm.nih.gov/

GitHub repository: https://github.com/KateK77/pubmed-clone

Product type: Biomedical Literature Search and Research Management Platform

Use the existing project directory and repository. Resolve setup paths relative to the project rather than assuming the shell starts in that directory.

This is an independent educational and research prototype. It is not affiliated with PubMed, NCBI, NIH or the National Library of Medicine. Use an original visual identity; do not copy official logos or protected branding.

## 2. Evaluation Scope

Deliver a complete, working version 3.0 covering:

- Functional correctness and reliable account workflows
- Frontend usability and responsive design
- Backend architecture and persistent data
- Real PubMed retrieval and search accuracy
- Error handling and user-specific authorization
- Citation metadata fidelity
- Automated regression tests and separately runnable live API checks
- Safe upgrade of existing accounts and saved research

Record implementation results separately from this requirements document. Distinguish automated verification, manual acceptance and any later independent benchmark. Do not claim unperformed tests or fabricated success rates.

## 3. Product Objective

Develop a professional biomedical literature search platform that enables users to find, explore, filter, save, organize, and export scientific publications.

The application should reproduce the principal workflows of PubMed while using modern frontend and backend technologies.

Users should be able to:

- Search biomedical literature
- Use advanced search syntax
- Filter search results
- View complete publication metadata
- Read available abstracts
- Find related articles
- Save publications
- Create research collections
- Manage search history
- Export citations

The primary dataset must come from the official PubMed API.

The application must not fabricate scientific publications.

## 4. Technology Stack

Frontend:

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router
- TanStack Query

Backend:

- Python
- Django
- Django REST Framework

Database:

- PostgreSQL for production
- SQLite for local development

External API:

- NCBI Entrez E-utilities

Testing:

- pytest / pytest-django
- Vitest
- React Testing Library
- Playwright

Use a modular architecture with a clear boundary between the frontend, backend, and external literature services.

## 5. Visual Design

Create a clean, professional biomedical research interface.

Use PubMed as a functional and information architecture reference.

Design characteristics:

- White background
- Dark blue primary navigation
- Light gray secondary surfaces
- Clear typography
- Accessible buttons and forms
- Minimal visual distractions
- Responsive layouts
- Consistent component styling

Primary navigation:

- Home
- Search
- Advanced Search
- Saved Articles
- Collections
- Search History
- Profile

Implement responsive navigation for mobile devices.

Provide:

- Loading indicators
- Empty search states
- Error messages
- Input validation
- Pagination controls
- Filter badges
- Confirmation dialogs

## 6. Home Page

The homepage should include:

- Large biomedical literature search field
- Search button
- Advanced Search link
- Introduction to the platform
- Trending or featured publications
- Recent searches for logged-in users
- Quick links to common research topics
- Navigation to saved research collections

Example searches:

- Large language models in healthcare
- Electronic health records
- Clinical natural language processing
- Retrieval augmented generation
- Type 2 diabetes
- Cardiovascular disease
- Cancer immunotherapy

Example search suggestions may be predefined, but displayed publication results must come from actual PubMed data.

## 7. Core Literature Search

Integrate the official PubMed search API.

Users must be able to search by:

- Keywords
- Article title
- Author
- Journal
- PMID
- DOI
- Disease
- Research topic
- Medical terminology

Support common PubMed query syntax.

The search result page must show:

- Total result count
- Search query
- Active filters
- Sort controls
- Paginated publications

Each publication card should include:

- Article title
- Authors
- Journal
- Publication year
- PMID
- DOI, if available
- Abstract preview
- Publication type, if available
- Full-text availability

Clicking a publication must open its detail page.

Support configurable results per page:

- 10
- 20
- 50

Search results must use server-side pagination.

Do not retrieve a small result subset and then incorrectly display it as the complete search result set.

## 8. Sorting

Implement sorting options corresponding to supported PubMed search behavior.

Include:

- Best Match
- Most Recent
- Publication Date

Sorting must operate on the actual search results through appropriate API parameters or documented retrieval behavior.

The UI should clearly indicate the active sorting mode.

## 9. Advanced Filters

Implement a filter sidebar.

### Publication Date

- Last 1 Year
- Last 5 Years
- Last 10 Years
- Custom Date Range

### Article Type

- Clinical Trial
- Randomized Controlled Trial
- Review
- Systematic Review
- Meta-Analysis
- Case Report

### Text Availability

- Abstract Available
- Free Full Text
- Full Text Available

### Additional Filters

- Language
- Humans
- Other Animals
- MEDLINE subset
- Exclude preprints, where supported

Requirements:

- Multiple filters can be applied.
- Individual filters can be removed.
- All filters can be cleared.
- Active filters are visible.
- Filtering updates the search results.
- Filter state is reflected in the URL.
- Browser back/forward navigation preserves search state.

Translate filters into valid PubMed search queries.

Do not rely exclusively on filtering the currently displayed page.

## 10. Advanced Search Builder

Create a dedicated advanced search page.

Users must be able to combine multiple conditions using:

- AND
- OR
- NOT

Supported fields:

- All Fields
- Title
- Author
- Journal
- Abstract
- MeSH Terms
- Publication Date

Support nested expressions or grouped conditions where feasible.

Example:

("large language models" OR "LLM") AND "electronic health records"

Features:

- Add a search row
- Remove a search row
- Choose a field
- Choose an operator
- Enter a search term
- Preview generated query
- Execute search
- Save a search

The generated query must be compatible with the PubMed API.

Preserve parentheses and logical operator precedence.

Validate malformed expressions and provide clear feedback.

## 11. Publication Detail Page

Each publication must have a dedicated page.

Display all available metadata:

1. Title
2. Authors
3. Author affiliations
4. Journal
5. Publication date
6. Volume
7. Issue
8. Pages
9. PMID
10. PMCID, if available
11. DOI, if available
12. Abstract
13. Keywords
14. MeSH terms
15. Publication types
16. Full-text links
17. Related publications
18. References, when available
19. Cited-by information, when available

Do not invent missing fields.

The detail page should contain:

- Save Article
- Copy Citation
- Export Citation
- Open in PubMed
- Open Full Text

Clearly distinguish free full text, publisher links, and abstract-only records.

Do not bypass publisher paywalls.

Preserve author suffixes supplied by PubMed, including Jr and Sr, in the displayed author names. A valid title, identifier and abstract do not excuse omitted author metadata. Keep electronic and journal publication dates identifiable when provided.

## 12. Related Articles

Integrate ELink where appropriate.

Show related or similar publications.

Each related publication should link to its detail page.

Display:

- Title
- Authors
- Year
- Journal
- PMID

Clearly identify the relationship type.

If related article data is unavailable, show an appropriate empty state.

Do not manufacture similarity scores or citation counts.

## 13. Citation Management

Implement citation generation and export.

Supported formats:

- APA
- MLA
- Vancouver
- BibTeX
- RIS

Users should be able to:

- Copy one citation
- Export one citation
- Select multiple publications
- Export selected citations
- Export a complete collection

Use verified bibliographic metadata.

Handle:

- Missing DOI
- Missing issue
- Missing page numbers
- Long author lists
- Special characters
- Electronic publication dates

Do not fabricate bibliographic fields.

Preserve author suffixes in source metadata and format them appropriately in every supported citation style, including APA and RIS. Existing saved publications must receive corrected metadata when necessary, without losing their bookmarks or collection membership. Do not silently claim refreshed metadata if the upstream service is unavailable.

## 14. Saved Articles

Implement persistent article bookmarking.

Features:

- Save article
- Remove saved article
- View saved articles
- Search saved articles
- Sort saved articles
- Open article details
- Export saved citations

Bookmarks must persist across sessions.

Prevent duplicate saved records for the same user and PMID.

## 15. Research Collections

Allow users to organize publications into collections.

Features:

- Create collection
- Rename collection
- Delete collection
- Add publication
- Remove publication
- View publications within a collection
- Search within a collection
- Export collection citations

Example collections:

- Healthcare AI
- Clinical NLP
- Medical RAG
- AI Agents
- EHR Research
- Oncology
- Cardiology

Collections must be user-specific.

A user must not access another user's private collections.

## 16. Search History

Implement persistent search history for authenticated users.

Each record should store:

- Query
- Timestamp
- Filters
- Sorting method
- Result count

Features:

- View search history
- Reexecute search
- Remove history item
- Clear history
- Save frequently used queries

History should be displayed chronologically.

## 17. User Accounts

Implement registration, login, logout and profile management, with persistent saved articles, collections and search history for each user.

### Authentication and session handling

- Hash passwords; never store plaintext account passwords.
- Use CSRF protection for account mutations and enforce user-specific authorization.
- Give MedResearch its own session and CSRF cookie names so other local projects cannot overwrite its cookies.
- Detect a lost or expired session. Clear stale authenticated UI and show an actionable sign-in prompt instead of a raw authentication exception.
- Do not show a successful save when the request failed. Clear stale success/error messages as the form changes or a new request begins.
- Preserve unsaved input during same-user reauthentication where practical; never transfer a draft to another account.
- Verify that account changes survive refresh, logout and later login.
- Keep existing users, passwords, bookmarks, collections and history during upgrade. A cookie-name change may require a fresh sign-in, not recreation of the account.

### Profile and password updates

- Show field-specific validation errors beside the affected input.
- Save profile changes independently of optional password changes. An untouched or empty password field must not block a profile-only save.
- Require the current password for a password change and leave the old password valid if validation fails.
- Treat username and email as distinct fields; never silently save a username as an invalid email address.
- Retain ordinary access to research functions without forcing unnecessary profile completion.

### Email verification

- Support configurable verification for new registrations and email-address changes using real delivery when an SMTP service is configured.
- Use expiring, single-use codes with resend cooldowns and bounded verification attempts. Do not reveal codes in normal production API responses or browser pages.
- Verify a replacement address before applying it when verification is enabled; failed verification must leave the existing address intact.
- Let existing accounts continue accessing their saved research; do not invalidate their credentials during migration.
- Provide an explicitly labelled local test-mail mode for development. Do not describe local test messages as real inbox delivery.
- When a deployment deliberately disables email verification, allow ordinary registration and clearly state that email verification is unavailable. Never imply that a verification message was sent without a delivery attempt.

### Account isolation and demonstration

- Scope all private resources to the authenticated user, including object-level access through guessed identifiers.
- Provide a clearly labelled local development demo account; document its username and password separately from public-site accounts.
- Keep production secrets and private account data out of GitHub.

### Registration and password usability

- Display the password rule directly below the password field before submission: 8–128 characters.
- Do not require uppercase letters, lowercase letters, numbers or symbols. Do not reject a password solely for being common, numeric-only or similar to the username.
- Add Confirm password to registration and password changes. Require matching values in both the browser and API, with a clear correction message for a missing or mismatched confirmation.
- Login uses existing credentials; it does not require password confirmation or revalidate an existing password against the new registration policy.

### Minimal account interface

- Remove First name and Last name from the account UI. Do not request name completion after registration or login.
- Limit the account page to username, email, password change and sign out. Preserve existing database name values without requiring them in the UI.
- After ordinary registration or sign-in, go directly to Search.
- When a research page requested authentication, return to that internal page with its query/filter state. Reject external or unsupported return destinations and fall back to Search.
- Preserve an unsaved email edit when the session expires and the same user signs back in on the still-open account page. Discard the draft when a different user signs in.

## 18. PubMed API Integration

Use official NCBI E-utilities.

Documentation:
https://www.ncbi.nlm.nih.gov/books/NBK25501/

Implement:

### ESearch

Retrieve matching PubMed identifiers and result counts.

### ESummary

Retrieve publication metadata.

### EFetch

Retrieve detailed publication records and available abstracts.

### ELink

Retrieve related publication relationships where supported.

Build a dedicated backend service layer.

Suggested responsibilities:

- Query construction
- Search execution
- Metadata retrieval
- XML/JSON parsing
- Result normalization
- Error handling
- Caching
- Retry logic
- Rate limiting

Use appropriate batch requests instead of unnecessary one-request-per-publication patterns.

Respect the current official NCBI API usage limits.

Keep optional API keys on the server.

### Important

The primary search interface must use live PubMed data.

Never replace failed live searches with fabricated publication data.

An explicitly labeled offline demonstration mode may use verified fixtures.

## 19. Data Models

Suggested database entities:

- User
- Publication
- Author
- PublicationAuthor
- Journal
- SavedPublication
- Collection
- CollectionPublication
- SearchHistory
- SavedSearch
- ExternalAPICache

Publication fields:

- pmid
- pmcid
- doi
- title
- abstract
- journal
- publication_date
- publication_types
- keywords
- mesh_terms
- metadata
- retrieved_at

Use PMID as the canonical PubMed identifier.

Avoid unnecessary duplicate publication records.

Store raw external metadata when useful, but normalize frequently queried fields.

Add persistent email-verification state and challenges as needed for registration and email changes. Use additive migrations and back up the local database before upgrade. Preserve existing account identifiers and library ownership. Refresh legacy publication metadata without recreating saved-research relationships.

## 20. REST API

Implement backend endpoints for:

- Authentication
- Publication search
- Publication details
- Related publications
- Advanced search
- Saved publications
- Collections
- Search history
- Citation export
- User profile
- Health check

Use consistent response structures.

Validate query parameters.

Handle invalid PMIDs and malformed search queries.

Provide generated API documentation.

Include session inspection, email-code requests and verified account updates. Enforce CSRF on registration, login, logout and profile mutations. Profile-only updates must not require a password value. Failed account operations must return actionable field errors without exposing server internals.

Registration and password-change endpoints must validate password_confirmation and the 8–128-character password rule. Login must continue accepting valid existing credentials. Retain compatible legacy name fields at the data/API layer without presenting them as required UI fields.

## 21. Caching and Performance

Implement server-side caching.

Cache appropriate API responses using normalized request parameters.

Requirements:

- Configurable cache expiration
- Cache invalidation when appropriate
- Safe handling of incomplete responses
- Batching of publication metadata requests
- Efficient pagination
- Database indexes
- Avoidance of unnecessary repeated network calls

Support large result counts without loading the entire PubMed database.

## 22. Error Handling

Handle:

- Empty search query
- No matching publications
- Invalid PMID
- Invalid DOI
- Malformed advanced query
- PubMed API timeout
- Rate limit exceeded
- External API unavailable
- Missing publication metadata
- Partial API response
- Duplicate saved article
- Unauthorized collection access
- Database errors

Display user-friendly messages.

Do not expose sensitive server details in frontend error messages.

Also handle expired sessions, profile validation failures, invalid or expired email codes, resend limits and email delivery failures. Recover the UI consistently after reauthentication and never display contradictory failure and success messages. A failed save must not be reported as persisted.

## 23. Accessibility and Responsive Design

Implement:

- Keyboard-accessible controls
- Semantic HTML
- Form labels
- Visible focus states
- Appropriate color contrast
- Responsive layouts
- Screen-reader-friendly navigation
- Accessible dialogs
- Accessible pagination

Test the application at desktop and mobile viewport sizes.

## 24. Automated Tests

Implement unit, integration, and end-to-end tests.

Required tests include:

### Search

- Basic keyword search
- Search by PMID
- Search by author
- Search by journal
- Search with no results
- Invalid query handling

### Filters

- Publication date filter
- Article type filter
- Multiple filters
- Clearing filters
- Filter persistence in URL

### Advanced Search

- AND
- OR
- NOT
- Parentheses
- Field-specific queries
- Invalid expressions

### Publication Details

- Correct PMID
- Correct metadata
- Missing abstract
- Missing DOI
- Related articles

### User Features

- Registration
- Login
- Logout
- Save publication
- Remove publication
- Create collection
- Add article to collection
- Search history persistence
- User data isolation

### External API

- Timeout
- Rate limiting
- Invalid response
- Partial metadata
- Retry behavior
- Cache behavior

### Citation Export

- APA
- MLA
- Vancouver
- BibTeX
- RIS
- Missing metadata fields

Use mocked NCBI responses for deterministic tests.

Create a separately runnable live API smoke test.

The final independent benchmark test suite will be generated after the development rounds.

Do not confuse internal development tests with final benchmark results.

### Account, upgrade and metadata regressions

- Profile save with empty password inputs
- Optional profile fields and field-specific validation
- Profile persistence after reload and re-login
- Expired-session recovery and correct authenticated UI state
- Isolation from other applications' local session cookies
- Registration and email-change verification, expired/incorrect/reused codes and resend limits
- Explicitly disabled verification and local test-mail behavior
- Existing-account and saved-library preservation during migration
- Author suffixes in article details, APA, RIS and other export formats
- Refresh of legacy saved metadata without losing ownership or collection membership

### Deployment and setup checks

- Windows setup invoked from outside the repository directory
- PostgreSQL configuration and additive migrations
- Production frontend routes, static assets and API served from the intended origin
- HTTPS/security-cookie configuration and private resource authorization
- Clear separation of mocked regression checks from live PubMed retrieval and real email delivery checks

### Version 3 account acceptance

- Password requirements visible before a registration attempt
- Short/long password boundaries and acceptance of otherwise valid common or numeric-only passwords
- Missing/mismatched confirmation in browser and API
- Failed password change leaves the existing password usable
- Ordinary login without confirmation, including previously registered accounts
- No First name/Last name controls or forced profile-completion step
- Successful registration/sign-in goes directly to Search
- Safe return to an internal research page with preserved URL state
- Rejection of external or unsupported return destinations
- Same-user email-draft restoration and different-user draft isolation

## 25. GitHub and Deployment Requirements

Use the existing repository:

https://github.com/KateK77/pubmed-clone

Inspect existing contents before modification. Preserve unrelated files, users' work, repository history and earlier version tags.

Maintain this project structure:

- frontend/
- backend/
- tests/
- docs/
- experiments/
- .github/workflows/
- README.md
- AGENTS.md
- CHANGELOG.md
- .env.example
- .gitignore

Save this complete version-specific description at experiments/round-03/description.md. Store verification results and release metadata separately in that directory.

Record the version, date, implementation commit, available model identifier, test commands, actual results and known limitations. Create and push the v3.0.0-r3 release tag without moving previous tags.

Provide a public-hosting configuration that serves the React frontend and Django API, uses persistent PostgreSQL, keeps credentials server-side and supports HTTPS session/CSRF protection. Keep SQLite available for local development.

Visitors must be able to follow the repository's website link to register their own accounts and use saved research when the site is deployed. Publish only a verified working application URL; do not present a local address or a deployment-template button as an already hosted website.

Make email verification configurable and document the required server-side mail settings. Distinguish an implemented workflow from verified delivery to an external mailbox. Do not claim a deployment or delivery capability that has not actually been verified.

Push the completed source and documentation to GitHub and verify the remote commit. Report a concrete blocker if GitHub authentication or a required deployment service is unavailable.

### Public showcase

- Publish the MedResearch website entry at https://medresearch-cljd.onrender.com and identify it clearly as the PubMed project.
- Document intentionally public, ordinary demo accounts in a Username/Password table after verifying fresh login and session persistence on that site.
- Keep public-site credentials distinct from the local development account and from accounts for other projects.
- Explain that users sharing a demo login share its research data; provide personal registration for separate libraries.
- Do not claim that shared-profile or password changes are blocked unless the application actually enforces that behavior.
- For the showcase configuration without SMTP, explicitly state that registration works without email verification. Keep the configurable verification workflow available for deployments that enable it.

## 26. README Requirements

The README must include:

- Project overview
- Feature list
- Technology stack
- Architecture
- Installation instructions
- Environment variables
- Database configuration
- Database migrations
- Startup commands
- API configuration
- Demo account
- Test commands
- Known limitations
- Independent prototype disclaimer

A new developer should be able to clone and run the application using the documented instructions.

Include upgrade/backup instructions, project-relative Windows startup commands, the distinction between local and public demo accounts, email-verification configuration, the verified live website link when deployed, and known hosting/API limits. Keep operational status and verification reports separate from the product requirements.

## 27. Final Deliverables

Deliver the complete MedResearch 3.0 application with:

1. Feature checklist and architecture
2. GitHub repository URL and verified commit SHA
3. Release tag v3.0.0-r3
4. This complete version-specific description
5. Installation, upgrade and exact startup commands
6. Environment-variable and database configuration
7. Clearly labelled demo-account instructions
8. Actual automated and live-check results, reported separately
9. Manual acceptance instructions
10. Deployment configuration and verified public entry link when available
11. Known issues, missing capabilities and unverified integrations

Report results accurately. Do not claim complete functionality without implementation and verification.

## 28. Completion Criteria

Complete and verify version 3.0 across the full literature, account, collection, history and citation workflows in this document.

Prioritize real PubMed data, correct metadata, dependable account persistence, clear registration/profile behavior and user-specific data access.

Preserve existing research data and prior releases. Run the relevant automated checks, keep live service checks separate, update the documentation, push the version to GitHub and report the actual outcome.

Do not automatically start another development version or a paid independent benchmark.
