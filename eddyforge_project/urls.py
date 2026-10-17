from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import (
    PublishedPostSitemap,
    PublishedProjectSitemap,
    PublishedLabSitemap,
    PublishedServiceSitemap,
    StaticPageSitemap,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "pages": StaticPageSitemap,
                "projects": PublishedProjectSitemap,
                "posts": PublishedPostSitemap,
                "services": PublishedServiceSitemap,
                "lab": PublishedLabSitemap,
            }
        },
        name="sitemap",
    ),
    path("", include("core.urls")),
]

handler404 = "core.views.custom_404"
