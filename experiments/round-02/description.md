# Round 2 — 2.0 specification

The original complete specification follows below and remains the baseline.

The user completed manual acceptance testing and reported the remaining checklist passed. Detailed evidence and unresolved issues are preserved in manual-feedback.json.

Required revisions

- Fix profile saving with empty password inputs, clear conflicting stale success messages, show field-specific errors, and verify saved fields survive refresh and re-login.
- Handle lost sessions consistently and isolate MedResearch cookies from other local applications.
- Preserve author name suffixes in article display and all citation formats, including metadata saved in Round 1.
- Add configurable real email verification for registration. Allow existing accounts to continue using their saved research. Supply explicit local development behavior when email service is unavailable.
- Prepare the application for public deployment, with persistent PostgreSQL, server-side configuration and a GitHub entry link once an actual deployment URL exists.
- Keep React/TypeScript/Vite and Django/DRF as specified.
- Preserve the original repository and Round 1 tag. Test the completed Round 2 source and push the code, documentation and a new tag to GitHub.

Latest user scope

“你现在有了刚才我给你的反馈，你再加上最初的prompt重新写一个这个网页软件即可，最后版本再放到github上”

The user has no deployment or email service account. This round delivers the revised application source to GitHub. Public hosting and real recipient mailbox delivery require subsequent service configuration.

Original instructions
# CODEX MASTER INSTRUCTION — PUBMED-INSPIRED BIOMEDICAL LITERATURE PLATFORM

## 0. Read This First

You are an autonomous senior full-stack software engineer, biomedical informatics engineer, database architect, and QA engineer.

Your task is to build a complete biomedical literature search and research management application inspired by PubMed.

This is an independent software engineering benchmark project.

You have no previous conversation context.

Do not assume that any existing application, repository, database, or API integration has already been created.

**Build the entire specified application during Round 1.**

Do not stop after building a project scaffold, homepage mockup, or limited MVP.

You may break the implementation into internal tasks, but the required output is one complete, working application.

## 1. Project Identity

Project name: MedResearch

Reference website:
https://pubmed.ncbi.nlm.nih.gov/

GitHub owner:
KateK77

Target repository:
KateK77/pubmed-clone

Preferred local directory:
D:\AI-Workspace\Personal\pubmed-clone

Repository visibility:
PRIVATE

Product type:
Biomedical Literature Search and Research Management Platform

This is an independent educational and research prototype.

It is not affiliated with PubMed, NCBI, NIH, or the National Library of Medicine.

Do not copy official logos or protected branding.

Use an original visual identity.

## 2. Experiment Context

This project is one of three independent healthcare software generation experiments.

The experiment evaluates:

- Complete software generation
- Functional correctness
- Backend architecture
- Frontend functionality
- External API integration
- Database design
- Search accuracy
- Error handling
- Security
- Automated testing
- Improvement across iterative feedback rounds

The experiment permits up to five development rounds.

**This instruction starts Round 1 only.**

Round 1 must produce a complete application.

At the end of this round:

1. Run validation checks.
2. Save the complete requirements.
3. Commit the implemented code.
4. Create a version tag.
5. Push to GitHub.
6. Report the results.
7. Stop and wait for feedback.

Do not automatically start another round.

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

Implement:

- Registration
- Login
- Logout
- Profile management
- Saved articles
- Collections
- Search history

Security:

- Password hashing
- Session security
- CSRF protection
- Input validation
- User-specific authorization
- Object-level access control

Create a clearly labeled local demo account.

Do not expose private user data.

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

## 25. GitHub Requirements

Target repository:

KateK77/pubmed-clone

Create this repository as PRIVATE if it does not already exist.

Inspect any existing contents before modification.

Required project structure:

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

Create:

experiments/round-01/description.md
experiments/round-01/results.md
experiments/round-01/metadata.json

Save the full original instructions in description.md.

Record:

- Date
- Model identifier, if available
- Git commit SHA
- Implemented features
- Test commands
- Test results
- Known limitations

Create Git tag:

v0.1.0-r1

Push source code, documentation, and tag to GitHub.

Verify the remote commit.

Do not overwrite unrelated files or existing repository history.

If GitHub authentication is unavailable, report the blocker.

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

## 27. Final Deliverables

At the end of Round 1, provide:

1. Completed feature checklist
2. Application architecture
3. GitHub repository URL
4. Commit SHA
5. Git tag
6. Installation instructions
7. Exact startup commands
8. Environment variables
9. Demo account
10. Test results
11. Manual testing instructions
12. Known issues
13. Missing or incomplete functionality

Report results accurately.

Do not claim complete functionality without implementation and verification.

## 28. Execution Instructions

Begin implementing immediately.

Create the complete biomedical literature search platform.

Prioritize functional correctness, real PubMed data integration, and reliable search behavior.

Do not divide the delivery into multiple development phases.

Do not stop after producing a plan.

Do not automatically start Round 2.

After implementing, testing, documenting, and pushing Round 1, stop and wait for my feedback.

**BEGIN ROUND 1: BUILD THE COMPLETE MEDRESEARCH APPLICATION.**