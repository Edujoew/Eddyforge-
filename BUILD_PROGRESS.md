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
- [ ] Phase 5 — Uses, now and lab pages with two self-contained demos. (in progress)
- [ ] Phase 6 — Authenticated client portal and retirement of the browser-side access gate.
- [ ] Phase 7 — Smoke tests, full verification and handoff documentation.

## Manual steps for me

- Create a hosted PostgreSQL database and configure the documented Vercel environment variables.
- Run migrations and `import_content` against the hosted database.
- Submit test inquiries through both forms and confirm them in Django admin.
- Add real project screenshots and a resume PDF; complete project, service, resume, and Now content.
- Review the unpublished blog draft and privacy policy before publishing.
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
- Next up: Phase 5 — Uses, Now and Lab pages plus standalone demos.
