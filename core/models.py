from django.db import models


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
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title


class Service(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    long_description = models.TextField(blank=True)
    icon = models.CharField(max_length=100, blank=True)
    tech = models.CharField(max_length=255, blank=True)
    tags = models.JSONField(default=list, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def __str__(self):
        return self.title
