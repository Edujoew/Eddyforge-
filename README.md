# Eddyforge

Eddyforge is Johnny Edwards's full-stack development portfolio and project inquiry site. Django renders the public portfolio, stores contact and project inquiries, publishes editorial and lab content, and provides authenticated client project views. Editorial content is managed in Django admin and can be initialized from `core/static/core/content.json`.

## Local development

Use Python 3.11+ and PowerShell from the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_DEBUG = "True"
python manage.py migrate
python manage.py import_content
python manage.py createsuperuser
python manage.py runserver
```

When `DJANGO_DEBUG=True`, a random development secret is generated at process startup if `DJANGO_SECRET_KEY` is unset; production startup fails if it is unset. `DATABASE_URL` may be omitted locally to use SQLite. `python manage.py test core.tests` runs the focused smoke and access-control tests against Django's isolated test database.

## Deployment configuration

`vercel.json` builds static assets with `python manage.py collectstatic --noinput`, routes requests to `eddyforge_project/wsgi.py`, and configures the Vercel Python and static builders. The WSGI application is `eddyforge_project.wsgi:application`. WhiteNoise supplies compressed static-file storage. Configure these variables in Vercel:

| Variable | Purpose |
| --- | --- |
| `DJANGO_SECRET_KEY` | Long, random Django signing secret; required outside debug mode. |
| `DJANGO_DEBUG` | Set to `False` in production. |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated hostnames; `.vercel.app` is included automatically. |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Comma-separated fully qualified origins, including scheme, e.g. `https://example.com`. |
| `DATABASE_URL` | Neon pooled PostgreSQL URL for Vercel runtime. Leave unset for local SQLite. |
| `DIRECT_DATABASE_URL` | Neon non-pooled URL for local migration/management commands; do not set it in Vercel. |
| `SITE_URL` | Canonical public origin, e.g. `https://example.com`, without a trailing slash. |
| `BOOKING_URL` | Optional booking provider URL shown after project inquiry. |
| `CONTACT_EMAIL` | Contact address displayed in the privacy notice. |
| `RESPONSE_TIME_TEXT` | Optional response-time copy on the inquiry confirmation page. |
| `RESUME_PDF` | Optional PDF file name/path below `core/static/core/`; default is `resume.pdf`. |

HTTPS-only session and CSRF cookies are enabled when `DJANGO_DEBUG=False`. Configure a persistent managed PostgreSQL database: Vercel's filesystem and SQLite files are not durable. PostgreSQL connections use short-lived connections and disable server-side cursors for serverless compatibility. Uploads are not configured; portfolio images and the optional resume must be committed static assets or absolute URLs.

## First-time hosted database setup

For Neon, set Vercel's `DATABASE_URL` to the pooled (`-pooler`) connection string. For local schema operations, keep the direct (non-pooled) connection string in `DIRECT_DATABASE_URL` and assign it to `DATABASE_URL` only in the shell running the management command. Both connections must use TLS (`sslmode=require`).

```powershell
$env:DIRECT_DATABASE_URL = "postgresql://USER:PASSWORD@HOST/DATABASE?sslmode=require"
$env:DJANGO_SECRET_KEY = "REPLACE_WITH_A_RANDOM_SECRET"
$env:DJANGO_DEBUG = "False"
$env:DJANGO_ALLOWED_HOSTS = "example.com,www.example.com"
$env:DJANGO_CSRF_TRUSTED_ORIGINS = "https://example.com,https://www.example.com"
$env:SITE_URL = "https://example.com"
$env:CONTACT_EMAIL = "you@example.com"
$env:DATABASE_URL = $env:DIRECT_DATABASE_URL
python manage.py migrate
python manage.py createsuperuser
python manage.py import_content
```

Never commit connection strings, passwords, or production secrets. Do not put them in this OneDrive-synced workspace: `.gitignore` prevents Git tracking but does not stop OneDrive synchronization. Prefer shell environment variables, a password manager, or a secrets manager. Run database commands locally against the hosted database only when `DATABASE_URL` is explicitly set in that PowerShell session. `import_content` creates missing starter entries and does not overwrite content edited in Django admin.

## Authentication and client setup

- `/admin/` is Django's native administration site. Create a superuser with `createsuperuser`.
- `/admin-panel/` is a legacy browser-side content preview/export tool; it is restricted to staff accounts. Its local-browser edits are not a replacement for Django admin or a publishing workflow.
- `/portal/login/` is the server-authenticated client portal; `/login/` redirects there. `/portal/password/` lets clients change their password. There is no public account registration.
- Create a Django user for each client, then create `ClientProject` records in Django admin and assign them to that user. Add milestones and active shared links as project inlines. A client can only access projects assigned to their own account; expired or inactive shared links are hidden.
- Clients sign out through a POST form. Passwords and sessions are handled by Django authentication, not browser storage.
- `python manage.py create_client --username NAME --email EMAIL --project-title TITLE` creates a client and project; its generated temporary password is printed only once. Repeating the command reuses the account/project.
- `python manage.py content_gaps` reports empty and placeholder content without modifying the database.

## Launch tooling

- [`LAUNCH.md`](./LAUNCH.md) is the command-oriented deployment checklist.
- `scripts/launch_setup.ps1` runs first-time hosted setup interactively. `-Local` exercises the workflow using a disposable SQLite file and skips clipboard setup.
- `scripts/smoke_live.ps1 -BaseUrl https://example.com` runs GET-only route checks.
- For image preparation, install `requirements-dev.txt`, place files under `incoming/<project-slug>/`, then run `python scripts/optimize_images.py`. It prints static paths for Django admin; `incoming/` is ignored.

## Application structure

- `eddyforge_project/` — Django settings, URL configuration, WSGI and ASGI entry points.
- `core/` — public and portal views, models, admin, migrations, tests, management commands, templates and static files.
- `core/static/core/content.json` — source content for existing client-rendered portfolio sections and the content importer.
- `core/templates/core/base.html` — shared public-site layout, metadata and navigation.
- `staticfiles/` — generated by `collectstatic`; do not edit directly.
- `BUILD_PROGRESS.md` — implementation status and operator handoff checklist.

## Public URLs

- `/`, `/about/`, `/contact/`
- `/projects/` and `/projects/<slug>/`
- `/services/` and `/services/<slug>/`
- `/start/` and `/start/thanks/`
- `/blog/`, `/blog/<slug>/`, and `/blog/feed.xml`
- `/resume/`, `/privacy/`, `/uses/`, `/now/`
- `/lab/` and `/lab/<slug>/`
- `/robots.txt` and `/sitemap.xml`
- `/login/` is a compatibility redirect to `/portal/login/`.

## Client and staff URLs

- `/portal/login/`, `/portal/logout/`, `/portal/password/`, `/portal/`, `/portal/projects/<slug>/`
- `/admin/` (Django admin; staff accounts only)
- `/admin-panel/` (legacy browser-side tool; staff accounts only)

## Operator handoff

Before production launch, configure hosted PostgreSQL and Vercel environment variables, run migrations and `import_content` against the hosted database, and create staff/client accounts. Submit test messages through both inquiry forms and verify their records in Django admin. Add real project screenshots and, if desired, a resume PDF; complete project/service descriptions and current Now content; review the seeded unpublished blog draft and privacy notice before publishing. The privacy notice is informational and is not a claim of legal compliance.
