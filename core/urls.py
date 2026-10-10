from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("admin-panel/", views.admin_page, name="admin"),
    path("login/", views.login, name="login"),
    path("projects/", views.projects, name="projects"),
    path("services/", views.services, name="services"),
]
