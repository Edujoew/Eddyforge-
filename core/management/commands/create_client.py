import secrets

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.core.validators import validate_email
from django.db import transaction
from django.utils.text import slugify

from core.models import ClientProject


class Command(BaseCommand):
    help = "Create or reuse a client account and link a project to it."

    def add_arguments(self, parser):
        parser.add_argument("--username", required=True)
        parser.add_argument("--email", required=True)
        parser.add_argument("--project-title", required=True)
        parser.add_argument(
            "--status",
            choices=[choice for choice, _label in ClientProject.STATUS_CHOICES],
            default="planning",
        )

    def handle(self, *args, **options):
        user_model = get_user_model()
        username = options["username"].strip()
        email = options["email"].strip()
        title = options["project_title"].strip()
        if not username or not email or not title:
            raise CommandError("Username, email, and project title must not be blank.")
        try:
            validate_email(email)
        except ValidationError as error:
            raise CommandError("Enter a valid client email address.") from error

        with transaction.atomic():
            user = user_model.objects.filter(username=username).first()
            created_user = user is None
            if user is not None and (user.is_staff or user.is_superuser):
                raise CommandError(
                    f"Refusing to modify staff or superuser account {username!r}."
                )
            if created_user:
                temporary_password = secrets.token_urlsafe(24)
                user = user_model.objects.create_user(
                    username=username,
                    email=email,
                    password=temporary_password,
                )

            project = ClientProject.objects.filter(client=user, title=title).first()
            created_project = project is None
            if created_project:
                base_slug = slugify(title)[:220].strip("-") or "client-project"
                slug = base_slug
                suffix = 2
                while ClientProject.objects.filter(slug=slug).exists():
                    slug = f"{base_slug[:210]}-{suffix}"
                    suffix += 1
                project = ClientProject.objects.create(
                    client=user,
                    title=title,
                    slug=slug,
                    status=options["status"],
                )

        if created_user:
            self.stdout.write(
                self.style.WARNING(
                    f"Temporary password (shown once): {temporary_password}"
                )
            )
        else:
            self.stdout.write(f"Reusing existing client account {username!r}.")
        self.stdout.write(
            f"{'Created' if created_project else 'Reused'} project "
            f"{project.title!r} for {username!r}."
        )
