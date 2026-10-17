# Eddyforge upgrade progress

## Assumptions

- The custom browser-side admin editor remains a content preview/export tool; Django admin is the authoritative secure editor.
- Portfolio projects and services are imported from `core/static/core/content.json`; existing curated copy is preserved during imports.
- Database migrations and data imports will be run by the operator against the intended hosted database, not against the ignored local SQLite file.
- Use the project’s existing standalone page layouts while moving shared chrome into a base template.

## Phases

- [x] Phase 1 — Foundation, shared public template, SEO, deployment settings and setup documentation.
- [x] Phase 2 — Content models, Django admin, migrations, starter data and import command.
- [x] Phase 3 — Case studies, inquiry flow, server-rendered blog and RSS.
- [x] Phase 4 — Service landing pages, resume, privacy and custom error pages.
- [x] Phase 5 — Uses, now and lab pages with two self-contained demos.
- [x] Phase 6 — Authenticated client portal and retirement of the browser-side access gate.
- [x] Phase 7 — Smoke tests, full verification and handoff documentation.

## Manual steps for me

- Create a hosted PostgreSQL database and configure the documented Vercel environment variables.
- Run migrations and `import_content` against the hosted database.
- Submit test inquiries through both forms and confirm them in Django admin.
- Add real project screenshots and a resume PDF; complete project, service, resume, and Now content.
- Review the unpublished blog draft and privacy policy before publishing.
- Create client accounts and assign each client project to its account in Django admin; there is no public sign-up.
- Have the privacy policy reviewed; it is informational, not a claim of legal compliance.

## Next up

- Phase 1 is complete: shared public base, page metadata, sitemap/robots, secure settings, environment variables and local/hosted setup steps are in place.
- Phase 1 assumptions: `.vercel.app` remains allowed; custom hostname and CSRF origins come from comma-separated environment variables; `SITE_URL` overrides request-host SEO origins.
- Verification: `manage.py check` passed; `/`, `/about/`, `/services/`, `/projects/`, `/contact/`, `/robots.txt`, and `/sitemap.xml` returned HTTP 200.
- Phase 2 complete: added published project/service fields, case-study images/FAQs, project inquiries, posts, Now updates and lab experiments; added Django admin coverage, slug backfill migration, and `import_content`.
- Phase 2 assumptions: migrated legacy project/service slugs derive from titles with stable numeric suffixes for collisions; content import creates missing rows only and preserves existing/admin-edited records; seeded editorial starter copy remains unpublished except the first Now update and lab tools.
- Verification: `manage.py check` passed; `makemigrations --check --dry-run` reported no changes. No SQLite database was opened or modified.
- Phase 3 complete: added database-backed project list/detail with JSON fallback, inquiry/thanks flow, server-rendered paginated blog and RSS, homepage writing section, article metadata and Markdown sanitization.
- Phase 3 assumptions: project inquiry budget brackets are USD guidance and explicitly accept KES; the project-type form uses existing contact service choices; blog HTML is restricted to safe tags and URL schemes.
- Verification: migrations and seeding were exercised with SQLite in memory; imports are idempotent; public routes, detail pages, RSS, sitemap, inquiry redirect, and a malicious-Markdown check passed.
- Phase 4 complete: added server-rendered service listings/details, service FAQ support and JSON-LD, reusable process steps, a fact-based resume, privacy notice, sitemap entries, and branded 404/plain 500 templates.
- Phase 4 assumptions: unknown resume credentials remain empty; PDF download appears only for a configured file within `core/static/core/`; service timing stays scope-dependent when not explicitly provided; privacy text describes configuration without claiming legal compliance.
- Verification: Django checks and migration state passed; service pages, resume, privacy, service query preselection, and the custom 404 returned expected output in an in-memory database test.
- Phase 5 complete: added server-rendered Uses, Now and Lab pages plus two standalone local-only JavaScript tools; static lab demos are shown in sandboxed frames.
- Phase 5 verification: Django checks and migration-state checks passed; Uses, Now, Lab, and both demo pages returned HTTP 200; demo pages included the expected sandbox attribute.
- Phase 6 complete: added client projects, milestones, expiring shared links, admin inlines, Django-authenticated portal login/logout/dashboard/details, per-user project scoping, legacy `/login/` redirect, and staff-only `/admin-panel/`. Removed browser-side credential hashes and sessionStorage authorization checks; no public signup was added.
- Phase 6 verification: portal authentication and user isolation, expired-link filtering, staff restrictions, and POST-only logout passed regression tests.
- Phase 7 complete: added public-page, form persistence, custom 404, portal authentication/isolation, staff gate, and logout tests; documented routes, environment variables, deployment, onboarding, and operator handoff.
- Final verification: `manage.py check`, `makemigrations --check --dry-run`, and `manage.py test core.tests` all passed. Tests used Django's in-memory test database; the ignored project `db.sqlite3` was not used or modified.

## Launch prep

### Assumptions

- No Neon/Vercel credentials were supplied or requested; no hosted database or live site was accessed.
- Launch setup uses the direct Neon connection only for local management commands and the pooled URL only for Vercel runtime configuration. Secrets are process-scoped and clipboard contents are cleared after paste.
- `-Local` uses a unique temporary SQLite file, fake account data, and no clipboard operation; the file is deleted in `finally`.
- The Vercel edge handles HTTPS. Django secure redirect stays disabled to avoid proxy redirect loops; HSTS is limited to one day and does not include subdomains or preload.
- Privacy retention period, controller name, and privacy contact remain owner decisions; the notice makes no legal-compliance claim.
- Item 3 was exercised against a local temporary server only; no deployed URL was provided.

### Checklist

- [x] Item 1 — Added idempotent `create_client`, portal password change, and read-only `content_gaps`; tested permissions and password updates.
- [x] Item 2 — Added PowerShell first-run setup with secure prompts, validation, temporary SQLite mode, migrations, starter import, superuser setup, optional client creation, content report, and clipboard cleanup.
- [x] Item 3 — Added a GET-only live smoke script with status/redirect reporting and tested all discovered public routes against a local temporary server.
- [x] Item 4 — Production check, static build, secret-pattern scan, and ignore rules reviewed; fake environment and SQLite only.
- [x] Item 5 — Updated the privacy notice and added `launch/PRIVACY_AUDIT.md` with owner questions and ODPC/legal-review reminder.
- [x] Item 6 — Added the development-only Pillow dependency and WebP image optimizer; verified dimensions, aspect ratio, transparency, and cleanup using generated test images.
- [x] Item 7 — Added the concise `LAUNCH.md` workflow and troubleshooting commands.

### Verification and remaining actions

- Launch setup `-Local` completed end-to-end: migrations, content import, superuser creation, counts, and content-gap report; its temporary SQLite database was removed.
- Smoke script passed 27 GET-only checks on the local temporary deployment, including project/service/lab details, expected 404, and login redirects.
- All 16 Django tests, `manage.py check`, `makemigrations --check --dry-run`, and `collectstatic --noinput` passed. Production `check --deploy` reports only intentional W005/W008/W021: no HSTS subdomains/preload, and no Django SSL redirect because Vercel terminates HTTPS.
- Next up: owner configures Neon/Vercel, deploys, reviews the draft and privacy notice, decides the three listed privacy details, and runs the smoke script against the deployed URL.

## Follow-up launch and portfolio requests

- Verified Step 1 tooling and documented the exact local PowerShell entry point; Neon setup still requires the owner to enter Neon URLs and account details interactively.
- Confirmed `Post` already provides the requested dynamic blog content fields and is registered for full Django admin editing/publishing; retained the existing model and RSS/detail routes rather than duplicating article data.
- Restored a main-navigation link to the permission-protected Django admin.
- Resume now uses published database projects when available, retains the existing static project fallback before content import, and supports print/save-to-PDF. The owner supplied the 2+ years experience statement; no M-Pesa integration claim was added because the source content does not verify that project.
- Follow-up verification: all 18 Django tests pass; `manage.py check` passes; `makemigrations --check --dry-run` reports no missing migrations.
