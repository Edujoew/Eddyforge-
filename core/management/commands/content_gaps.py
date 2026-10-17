from django.core.management.base import BaseCommand

from core.data.resume import RESUME_DATA
from core.data.uses import USE_GROUPS
from core.models import LabExperiment, NowUpdate, Post, Project, Service


class Command(BaseCommand):
    help = "Report empty or placeholder content without changing records."

    PLACEHOLDERS = ("todo", "tbd", "placeholder", "lorem ipsum", "your text here")
    EXCLUDED_FIELDS = {
        "id",
        "slug",
        "is_published",
        "display_order",
        "created_at",
        "updated_at",
        "published_at",
    }

    def handle(self, *args, **options):
        rows = []
        for model in (Project, Service, Post, NowUpdate, LabExperiment):
            for instance in model.objects.all().order_by("pk"):
                gaps = []
                for field in model._meta.concrete_fields:
                    if field.name in self.EXCLUDED_FIELDS or field.is_relation:
                        continue
                    value = getattr(instance, field.name)
                    if value is None or value == "" or value == [] or value == {}:
                        gaps.append(field.name)
                    elif self.contains_placeholder(value):
                        gaps.append(f"{field.name} (placeholder)")
                label = getattr(instance, "title", None) or str(instance)
                state = "published" if getattr(instance, "is_published", False) else "unpublished"
                rows.append(
                    (
                        model.__name__,
                        label,
                        state,
                        ", ".join(gaps) if gaps else "none found",
                    )
                )

        for key, value in RESUME_DATA.items():
            if value == [] or value == "":
                rows.append(("Resume", key, "static", "empty section"))
        for group in USE_GROUPS:
            if not group.get("items"):
                rows.append(("Uses", group.get("title", "(untitled)"), "static", "empty section"))

        headers = ("Content type", "Entry", "Status", "Empty / placeholder fields")
        if not rows:
            self.stdout.write(" | ".join(headers))
            self.stdout.write("-+-".join("-" * len(label) for label in headers))
            self.stdout.write("No empty or placeholder content found.")
            return
        widths = tuple(
            max(len(header), *(len(str(row[index])) for row in rows))
            for index, header in enumerate(headers)
        )
        self.stdout.write(" | ".join(label.ljust(width) for label, width in zip(headers, widths)))
        self.stdout.write("-+-".join("-" * width for width in widths))
        for row in rows:
            self.stdout.write(
                " | ".join(str(value).ljust(width) for value, width in zip(row, widths))
            )

    @classmethod
    def contains_placeholder(cls, value):
        if isinstance(value, str):
            return any(marker in value.casefold() for marker in cls.PLACEHOLDERS)
        if isinstance(value, (list, tuple)):
            return any(cls.contains_placeholder(item) for item in value)
        if isinstance(value, dict):
            return any(cls.contains_placeholder(item) for item in value.values())
        return False
