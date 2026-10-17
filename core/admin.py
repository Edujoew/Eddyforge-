from django.contrib import admin
from django.utils import timezone

from .models import (
    ContactMessage,
    ClientProject,
    LabExperiment,
    Milestone,
    NowUpdate,
    Post,
    Project,
    ProjectImage,
    ProjectInquiry,
    Service,
    ServiceFAQ,
    SharedLink,
)


@admin.action(description="Publish selected items")
def publish_selected(modeladmin, request, queryset):
    queryset.update(is_published=True)
    if modeladmin.model is Post:
        queryset.filter(published_at__isnull=True).update(published_at=timezone.now())


@admin.action(description="Unpublish selected items")
def unpublish_selected(modeladmin, request, queryset):
    queryset.update(is_published=False)


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 0


class ServiceFAQInline(admin.TabularInline):
    model = ServiceFAQ
    extra = 0


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "service_needed", "created_at")
    search_fields = ("first_name", "last_name", "email", "project_brief")
    list_filter = ("service_needed", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "badge", "display_order", "created_at")
    search_fields = ("title", "short_title", "description", "problem", "badge")
    list_filter = ("is_published", "badge", "year", "image_first")
    ordering = ("display_order", "-created_at")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (ProjectImageInline,)
    actions = (publish_selected, unpublish_selected)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "tech", "display_order")
    search_fields = ("title", "description", "long_description", "intro", "tech")
    list_filter = ("is_published",)
    ordering = ("display_order", "-created_at")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (ServiceFAQInline,)
    actions = (publish_selected, unpublish_selected)


@admin.register(ProjectInquiry)
class ProjectInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "project_type", "budget_range", "status", "created_at")
    search_fields = ("name", "email", "company", "description")
    list_filter = ("status", "project_type", "budget_range", "created_at")
    readonly_fields = ("created_at",)
    list_editable = ("status",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("title", "is_published", "published_at", "updated_at")
    search_fields = ("title", "excerpt", "body", "tags")
    list_filter = ("is_published", "published_at")
    list_editable = ("is_published",)
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    actions = (publish_selected, unpublish_selected)


@admin.register(NowUpdate)
class NowUpdateAdmin(admin.ModelAdmin):
    list_display = ("is_published", "updated_at")
    list_filter = ("is_published", "updated_at")
    readonly_fields = ("updated_at",)
    actions = (publish_selected, unpublish_selected)


@admin.register(LabExperiment)
class LabExperimentAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "display_order")
    search_fields = ("title", "summary", "tags")
    list_filter = ("is_published",)
    ordering = ("display_order", "title")
    prepopulated_fields = {"slug": ("title",)}


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 0


class SharedLinkInline(admin.TabularInline):
    model = SharedLink
    extra = 0


@admin.register(ClientProject)
class ClientProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "client", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("title", "client__username", "client__email")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    inlines = (MilestoneInline, SharedLinkInline)


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "status", "due_date", "display_order")
    list_filter = ("status",)
    search_fields = ("title", "project__title")


@admin.register(SharedLink)
class SharedLinkAdmin(admin.ModelAdmin):
    list_display = ("title", "project", "is_active", "expires_at")
    list_filter = ("is_active",)
    search_fields = ("title", "project__title")
    actions = (publish_selected, unpublish_selected)
