from django.contrib.sitemaps import Sitemap
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from .models import LabExperiment, Post, Project, Service


class StaticPageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return (
            "home",
            "about",
            "services",
            "projects",
            "contact",
            "start",
            "blog",
            "resume",
            "privacy",
            "uses",
            "now",
            "lab",
        )

    def location(self, item):
        return reverse(f"core:{item}")


class PublishedProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Project.objects.filter(is_published=True)

    def lastmod(self, item):
        return item.updated_at


class PublishedPostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Post.objects.filter(is_published=True).filter(
            Q(published_at__isnull=True) | Q(published_at__lte=timezone.now())
        )

    def lastmod(self, item):
        return item.updated_at


class PublishedServiceSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Service.objects.filter(is_published=True)

    def lastmod(self, item):
        return item.updated_at


class PublishedLabSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return LabExperiment.objects.filter(is_published=True)
