from django.contrib import admin

from .models import ContactMessage, Project, Service


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "service_needed", "created_at")
    search_fields = ("first_name", "last_name", "email", "project_brief")
    list_filter = ("service_needed", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "badge", "display_order", "created_at", "updated_at")
    search_fields = ("title", "short_title", "description", "badge")
    list_filter = ("badge", "image_first", "created_at")
    ordering = ("display_order", "-created_at")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "tech", "display_order", "created_at", "updated_at")
    search_fields = ("title", "description", "long_description", "tech")
    list_filter = ("created_at",)
    ordering = ("display_order", "-created_at")
    readonly_fields = ("created_at", "updated_at")
