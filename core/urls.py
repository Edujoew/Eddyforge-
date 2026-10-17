from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .feeds import LatestPostsFeed
from . import views


app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("admin-panel/", views.admin_page, name="admin"),
    path("login/", views.login, name="login"),
    path(
        "portal/login/",
        LoginView.as_view(
            template_name="core/login.html",
            redirect_authenticated_user=True,
        ),
        name="portal_login",
    ),
    path("portal/logout/", LogoutView.as_view(), name="portal_logout"),
    path("portal/", views.portal_dashboard, name="portal_dashboard"),
    path(
        "portal/projects/<slug:slug>/",
        views.portal_project_detail,
        name="portal_project_detail",
    ),
    path("projects/", views.projects, name="projects"),
    path("projects/<slug:slug>/", views.project_detail, name="project_detail"),
    path("start/", views.start, name="start"),
    path("start/thanks/", views.start_thanks, name="start_thanks"),
    path("blog/", views.blog_list, name="blog"),
    path("blog/feed.xml", LatestPostsFeed(), name="blog_feed"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("services/", views.services, name="services"),
    path("services/<slug:slug>/", views.service_detail, name="service_detail"),
    path("resume/", views.resume, name="resume"),
    path("privacy/", views.privacy, name="privacy"),
    path("uses/", views.uses, name="uses"),
    path("now/", views.now, name="now"),
    path("lab/", views.lab, name="lab"),
    path("lab/<slug:slug>/", views.lab_detail, name="lab_detail"),
]
