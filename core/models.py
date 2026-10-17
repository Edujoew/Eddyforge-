from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


def split_lines(value):
    return [line.strip() for line in value.splitlines() if line.strip()]


class ContactMessage(models.Model):
    SERVICE_CHOICES = [
        ("e_commerce", "E-commerce Development"),
        ("corporate_web", "Corporate Web Solution"),
        ("custom_software", "Custom Software App"),
        ("ui_ux", "UI / UX Design & Frontend"),
        ("other", "Other"),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    service_needed = models.CharField(max_length=32, choices=SERVICE_CHOICES)
    project_brief = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "contact message"
        verbose_name_plural = "contact messages"

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.service_needed}"


class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    short_title = models.CharField(max_length=200, blank=True)
    badge = models.CharField(max_length=100, blank=True)
    badge_icon = models.CharField(max_length=100, blank=True)
    description = models.TextField()
    short_description = models.TextField(blank=True)
    highlights = models.JSONField(default=list, blank=True)
    repo = models.URLField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    icon_label = models.CharField(max_length=150, blank=True)
    accent = models.CharField(max_length=32, blank=True)
    image_first = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)
    role = models.CharField(max_length=160, blank=True)
    year = models.PositiveSmallIntegerField(null=True, blank=True)
    duration = models.CharField(max_length=100, blank=True)
    live_url = models.URLField(blank=True)
    problem = models.TextField(blank=True)
    approach = models.TextField(blank=True)
    results = models.TextField(blank=True)
    stack = models.TextField(blank=True)
    cover = models.CharField(max_length=500, blank=True, help_text="Static path or absolute image URL.")
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    @property
    def stack_list(self):
        return split_lines(self.stack)

    @property
    def results_list(self):
        return split_lines(self.results)

    def get_absolute_url(self):
        return reverse("core:project_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    path_or_url = models.CharField(max_length=500)
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "pk"]

    def __str__(self):
        return self.caption or f"Image for {self.project}"


class Service(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    long_description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    tech = models.CharField(max_length=255, blank=True)
    tags = models.JSONField(default=list, blank=True)
    is_published = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.CharField(max_length=320, blank=True)
    intro = models.TextField(blank=True)
    deliverables = models.TextField(blank=True)
    timeline = models.CharField(max_length=160, blank=True)
    related_projects = models.ManyToManyField(Project, blank=True, related_name="related_services")
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    @property
    def deliverables_list(self):
        return split_lines(self.deliverables)

    def get_absolute_url(self):
        return reverse("core:service_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class ServiceFAQ(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="faqs")
    question = models.CharField(max_length=300)
    answer = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "pk"]
        verbose_name = "service FAQ"
        verbose_name_plural = "service FAQs"

    def __str__(self):
        return self.question


class ProjectInquiry(models.Model):
    BUDGET_CHOICES = [
        ("under_500", "Under $500"),
        ("500_1500", "$500-$1,500"),
        ("1500_5000", "$1,500-$5,000"),
        ("over_5000", "Over $5,000"),
        ("not_sure", "Not sure yet"),
    ]
    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("won", "Won"),
        ("lost", "Lost"),
    ]

    name = models.CharField(max_length=160)
    email = models.EmailField()
    company = models.CharField(max_length=200, blank=True)
    project_type = models.CharField(max_length=32, choices=ContactMessage.SERVICE_CHOICES)
    budget_range = models.CharField(max_length=32, choices=BUDGET_CHOICES)
    timeline = models.CharField(max_length=160)
    description = models.TextField()
    reference_links = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def reference_links_list(self):
        return split_lines(self.reference_links)

    def __str__(self):
        return f"{self.name} — {self.get_project_type_display()}"


class Post(models.Model):
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True)
    excerpt = models.TextField()
    body = models.TextField(help_text="Markdown source.")
    tags = models.TextField(blank=True, help_text="One tag per line.")
    cover = models.CharField(max_length=500, blank=True, help_text="Static path or absolute image URL.")
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    @property
    def tags_list(self):
        return split_lines(self.tags)

    def save(self, *args, **kwargs):
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()
            update_fields = kwargs.get("update_fields")
            if update_fields is not None:
                kwargs["update_fields"] = {*update_fields, "published_at"}
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:blog_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class NowUpdate(models.Model):
    body = models.TextField(help_text="Markdown source.")
    is_published = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Now update"
        verbose_name_plural = "Now updates"

    def __str__(self):
        return f"Now update — {self.updated_at:%Y-%m-%d}"


class LabExperiment(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.TextField()
    demo_path = models.CharField(max_length=500, help_text="Static path below core/static/core/ or an absolute URL.")
    repo_url = models.URLField(blank=True)
    tags = models.TextField(blank=True, help_text="One tag per line.")
    is_published = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "title"]

    @property
    def tags_list(self):
        return split_lines(self.tags)

    def get_absolute_url(self):
        return reverse("core:lab_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class ClientProject(models.Model):
    STATUS_CHOICES = [
        ("planning", "Planning"),
        ("in_progress", "In progress"),
        ("on_hold", "On hold"),
        ("complete", "Complete"),
    ]

    client = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="client_projects",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.TextField(blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="planning")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "title"]

    def get_absolute_url(self):
        return reverse("core:portal_project_detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class Milestone(models.Model):
    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("in_progress", "In progress"),
        ("complete", "Complete"),
    ]

    project = models.ForeignKey(
        ClientProject,
        on_delete=models.CASCADE,
        related_name="milestones",
    )
    title = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default="upcoming")
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "due_date", "pk"]

    def __str__(self):
        return f"{self.project}: {self.title}"


class SharedLink(models.Model):
    project = models.ForeignKey(
        ClientProject,
        on_delete=models.CASCADE,
        related_name="shared_links",
    )
    title = models.CharField(max_length=200)
    url = models.URLField()
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.project}: {self.title}"
