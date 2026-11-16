# Public deployment

The repository provides a React frontend and a Django application. A public deployment needs an application host, persistent PostgreSQL database and, if email verification is enabled, an SMTP provider. No hosting account, public URL or SMTP credential has been provisioned for this release.

GitHub stores the source, runs the automated checks and can link visitors to the deployed website. GitHub Pages is static hosting and cannot run this Django backend. The Docker image serves the frontend, accounts and API on one origin so visitors only need one website URL.

## Prepare the service

### Prepared Render + Neon showcase

The owner requested that the existing GitHub repository and its full history become public. The repository is now public. Hosting is prepared but has not been provisioned. Render access and the target workspace have been confirmed; Neon database authorization is still required.

Validation of commit `9918a1be27e0b94a1fc81eec9ab66cb2a404ab01` passed in [GitHub CI](https://github.com/KateK77/pubmed-clone/actions/runs/43801157728): 53 backend cases on both SQLite and PostgreSQL, 11 frontend unit cases, 8 browser cases, the production WSGI smoke check and the Docker startup smoke check. The latter created a temporary PostgreSQL database, registered an account through CSRF-protected HTTP, restarted the app and verified that its session persisted. The blueprint also passed the Render JSON schema check.

`render.yaml` creates one **Free** Docker web service and obtains its own hostname from `RENDER_EXTERNAL_HOSTNAME`. It generates a Django secret, checks `/api/health/`, and deploys linked-repository changes after CI passes. No paid service or temporary Render database is declared.

Create a Neon project on its Free plan, then provide the PostgreSQL connection string as Render's secret `DATABASE_URL`. Also set an operator contact in `NCBI_EMAIL`. The startup command runs migrations against that database before starting one Gunicorn worker on the assigned `PORT`. It refuses SQLite so a host restart cannot silently erase accounts or collections. There is no demo-account seed in the public startup path. Local accounts and private research data are not uploaded.

The showcase configuration explicitly uses `EMAIL_VERIFICATION_REQUIRED=0`, matching the current locally accepted experience. Visitors can register and have private accounts, but their email addresses are not marked verified. Render's Free web services block common SMTP ports (25, 465 and 587), so ordinary SMTP verification cannot be promised on that plan. Enabling real mail requires a supported delivery path and provider configuration first.

Render's Free web service may sleep when idle and has usage limits. Neon Free also has storage/compute quotas. Render's separate Free Postgres expires after 30 days, so this blueprint uses external Neon storage instead. These limits mean a free showcase has availability constraints; they do not create an unlimited production service. See [Render Free](https://render.com/docs/free) and [Neon plans](https://neon.com/docs/introduction/plans).

Once the host returns a successful public deployment URL, test anonymous search, registration and account isolation. Then replace the README's pending status with an **Open MedResearch** link and set GitHub's About → Website to that exact URL. Do not invent a hostname before the host assigns it.

### Other hosts

1. Choose a host supporting Docker, HTTPS and a persistent PostgreSQL connection. Create a database and retain its connection credentials in the host's secret settings. Pricing and free-tier limits depend on the provider.
2. Connect the repository or build `docker build -t medresearch:3.0 .` from its root. The image listens on port `8000` and runs one Gunicorn worker with four threads. Configure the host's internal service port accordingly.
3. Set the environment variables below. Use your actual hostname and credentials. These placeholders are not working account credentials.
4. Before the first start and each schema upgrade, run `python backend/manage.py migrate --noinput` as a release command using the same image and database. Back up an existing database before upgrading.
5. Start the image and enable the host's HTTPS endpoint. Check `/api/health/`, `/profile` and a direct article URL. Verify that refreshing an article or profile URL returns the application.

```dotenv
DJANGO_DEBUG=0
DJANGO_SECRET_KEY=<a-long-random-secret>
DJANGO_ALLOWED_HOSTS=<your-public-hostname>
DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-public-hostname>
DJANGO_TRUST_PROXY=1
DJANGO_HSTS_SECONDS=3600
POSTGRES_DB=<database-name>
POSTGRES_USER=<database-user>
POSTGRES_PASSWORD=<database-password>
POSTGRES_HOST=<database-host>
POSTGRES_PORT=5432
POSTGRES_SSLMODE=require
NCBI_EMAIL=<operator-contact-email>
EMAIL_VERIFICATION_REQUIRED=1
EMAIL_HOST=<smtp-host>
EMAIL_PORT=587
EMAIL_HOST_USER=<smtp-user>
EMAIL_HOST_PASSWORD=<smtp-password>
EMAIL_USE_TLS=1
EMAIL_USE_SSL=0
DEFAULT_FROM_EMAIL=<provider-approved-sender>
```

Only set `DJANGO_TRUST_PROXY=1` when the host's trusted proxy overwrites `X-Forwarded-Proto`. Use the database provider's required TLS mode and certificate settings. Do not expose the container directly over HTTP in production. Do not copy `.env` into the image. The Docker build context excludes local databases, credentials and browser test output.

The single-process NCBI limiter is not coordinated across replicas. Keep one replica and one worker until a shared limiter has been implemented. Database-backed cache is optional: set `DJANGO_CACHE_TABLE=medresearch_cache` and run `python backend/manage.py createcachetable`. Configure backups for PostgreSQL and periodically run `python backend/manage.py clearsessions`.

## Email verification

Configure an SMTP account and sender approved by your provider. With port 587, providers commonly require `EMAIL_USE_TLS=1`. For implicit TLS on port 465, use `EMAIL_USE_TLS=0` and `EMAIL_USE_SSL=1`. Follow your provider's actual configuration.

The site requests a six-digit code, limits resends to one minute, expires codes after ten minutes, permits five verification attempts and consumes a successful code once. It stores a keyed digest rather than the plain code. Codes are bound to registration or to a specific signed-in user's email change. Existing accounts remain usable and can verify their addresses in Profile.

With `EMAIL_VERIFICATION_REQUIRED=1`, a missing SMTP configuration blocks new registrations and explains that email is unavailable. A failed delivery never creates a verified account. With the variable set to `0`, users can register without verification, and those addresses are not marked verified. This mode is convenient for local testing and should be an explicit deployment decision.

Automated tests use a temporary local mailbox. They verify the code workflow but do not prove delivery through an external provider. Before announcing the public website, test a real mailbox, code expiration, duplicate email rejection, profile changes, sign out and sign in. Configure provider monitoring and delivery limits appropriate to the audience.

## Link from GitHub

After the deployment has a working HTTPS URL, set the repository's **About → Website** field to that URL and add an **Open MedResearch** link near the top of the README. Visitors can then open the website and create their own accounts without installing Python or Node.js. This repository is now public; the deployed website's access is a separate hosting setting.

Do not advertise a localhost address, a GitHub source URL or an unconfigured Pages URL as the public application. This release intentionally contains no invented live URL.

## Release acceptance

- Open the public URL in a private browser window and search PubMed without signing in.
- Register with a real email, a password meeting the visible 8–128-character rule and matching confirmation. Enter the email code and verify that Search opens.
- Change the account email with a new code, save, reload and verify persistence. Sign out and sign back in to check the email and saved library.
- Use a different account and confirm it cannot access the first account's collection URL.
- Search PMID `31452104`, verify the `Jr` suffix and download RIS.
- Confirm HTTPS, database persistence across service restarts and an email provider delivery record.

References: [GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages), [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) and [Django email](https://docs.djangoproject.com/en/5.2/topics/email/).
