import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from core.models import LabExperiment, NowUpdate, Post, Project, Service


SERVICE_SLUGS = {
    "e-commerce development": "ecommerce",
    "corporate web solutions": "corporate-web",
    "corporate web solution": "corporate-web",
    "custom software apps": "custom-software",
    "custom software app": "custom-software",
    "ui / ux design & frontend": "ui-ux",
}

SERVICE_DELIVERABLES = {
    "e-commerce development": (
        "Mobile-first storefront\nPayment integration scoped to the chosen provider\n"
        "Inventory and order-management workflows"
    ),
    "corporate web solutions": (
        "Branded business website or company portal\n"
        "Admin dashboards or internal tools scoped to the brief"
    ),
    "corporate web solution": (
        "Branded business website or company portal\n"
        "Admin dashboards or internal tools scoped to the brief"
    ),
    "custom software apps": (
        "A web application shaped around the agreed workflow\n"
        "Custom application logic and reporting scoped to the brief"
    ),
    "custom software app": (
        "A web application shaped around the agreed workflow\n"
        "Custom application logic and reporting scoped to the brief"
    ),
    "ui / ux design & frontend": (
        "Responsive interface layouts\n"
        "A consistent frontend design system scoped to the product"
    ),
}


class Command(BaseCommand):
    help = "Import portfolio projects and services; seed starter editorial content once."

    def handle(self, *args, **options):
        content_path = (
            Path(settings.BASE_DIR) / "core" / "static" / "core" / "content.json"
        )
        try:
            content = json.loads(content_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise CommandError(f"Could not load {content_path}: {error}") from error

        project_count = self.import_projects(content.get("projects", []))
        service_count = self.import_services(content.get("services", []))
        self.seed_editorial_content()
        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {project_count} new projects and {service_count} new services."
            )
        )

    def import_projects(self, records):
        created = 0
        for record in records:
            title = record.get("title", "").strip()
            if not title:
                continue
            slug = slugify(title)[:220].strip("-") or "project"
            existing = Project.objects.filter(slug=slug).first()
            if existing is None:
                existing = Project.objects.filter(title=title).first()
            if existing:
                continue
            Project.objects.create(
                title=title,
                slug=slug,
                short_title=record.get("shortTitle", ""),
                badge=record.get("badge", ""),
                badge_icon=record.get("badgeIcon", ""),
                description=record.get("description", ""),
                short_description=record.get("shortDescription", ""),
                highlights=record.get("highlights", []),
                repo=record.get("repo", ""),
                icon=record.get("icon", ""),
                icon_label=record.get("iconLabel", ""),
                accent=record.get("accent", ""),
                image_first=bool(record.get("imageFirst", False)),
                is_published=True,
                display_order=Project.objects.count(),
            )
            created += 1
        return created

    def import_services(self, records):
        created = 0
        for record in records:
            title = record.get("title", "").strip()
            if not title:
                continue
            slug = SERVICE_SLUGS.get(title.casefold(), slugify(title)[:220].strip("-"))
            existing = Service.objects.filter(slug=slug).first()
            if existing is None:
                existing = Service.objects.filter(title=title).first()
            if existing:
                continue
            Service.objects.create(
                title=title,
                slug=slug,
                description=record.get("description", ""),
                long_description=record.get("longDescription", ""),
                icon=record.get("icon", ""),
                tech=record.get("tech", ""),
                tags=record.get("tags", []),
                intro=record.get("longDescription", ""),
                deliverables=SERVICE_DELIVERABLES.get(title.casefold(), ""),
                timeline="Agreed after discovery and scope review.",
                is_published=True,
                display_order=Service.objects.count(),
            )
            created += 1
        return created

    def seed_editorial_content(self):
        Post.objects.get_or_create(
            slug="deploying-django-on-vercel-the-gotchas-i-hit",
            defaults={
                "title": "Deploying Django on Vercel: the gotchas I hit",
                "excerpt": (
                    "A draft checklist of deployment details in this Eddyforge "
                    "project: static files, host validation, secrets, and databases."
                ),
                "body": (
                    "## Static files\n\n"
                    "This project runs `collectstatic` during the Vercel build and "
                    "uses WhiteNoise compressed static storage. Static assets are "
                    "not durable user uploads.\n\n"
                    "## Hosts, CSRF, and secrets\n\n"
                    "Production configuration must supply `DJANGO_SECRET_KEY`, "
                    "`DJANGO_ALLOWED_HOSTS`, and `DJANGO_CSRF_TRUSTED_ORIGINS`. "
                    "Set `DJANGO_DEBUG=False`; the development secret is not used "
                    "when debug is disabled.\n\n"
                    "## Database\n\n"
                    "The local SQLite configuration is useful for development, "
                    "but Vercel's filesystem is ephemeral, so it is not a durable "
                    "production database. Configure hosted PostgreSQL with "
                    "`DATABASE_URL`. The project disables server-side cursors and "
                    "uses short-lived connections for pooled/serverless database "
                    "connections. Run migrations against the intended hosted "
                    "database before serving traffic.\n\n"
                    "_Unpublished draft. Review and edit before publishing._"
                ),
                "tags": "Django\nVercel\nDeployment",
                "is_published": False,
            },
        )

        if not NowUpdate.objects.exists():
            NowUpdate.objects.create(
                body=(
                    "I am currently rebuilding the Eddyforge portfolio with "
                    "server-rendered case studies, a clearer project inquiry flow, "
                    "and practical writing and lab pages."
                ),
                is_published=True,
            )

        self.create_lab(
            title="WCAG Colour Contrast Checker",
            slug="contrast-checker",
            summary=(
                "Check foreground and background colour contrast ratios and see "
                "how they compare with WCAG text thresholds."
            ),
            demo_path="lab/contrast-checker/index.html",
            tags="Accessibility\nColour\nWCAG",
            order=1,
        )
        self.create_lab(
            title="JSON Formatter and Validator",
            slug="json-formatter",
            summary=(
                "Format JSON, report parse errors, and copy valid output without "
                "sending the data to a server."
            ),
            demo_path="lab/json-formatter/index.html",
            tags="JSON\nDeveloper tools",
            order=2,
        )

    @staticmethod
    def create_lab(*, title, slug, summary, demo_path, tags, order):
        LabExperiment.objects.get_or_create(
            slug=slug,
            defaults={
                "title": title,
                "summary": summary,
                "demo_path": demo_path,
                "tags": tags,
                "is_published": True,
                "display_order": order,
            },
        )
