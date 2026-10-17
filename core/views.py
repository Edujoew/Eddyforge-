import json
import re
from copy import deepcopy
from math import ceil
from pathlib import PurePosixPath
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.utils import timezone

from .data.uses import USE_GROUPS
from .forms import ProjectInquiryForm, project_type_for_service
from .markdown_utils import render_markdown
from .models import (
    ClientProject,
    ContactMessage,
    LabExperiment,
    NowUpdate,
    Post,
    Project,
    Service,
    SharedLink,
)


def page_context(request, title, description):
    site_url = settings.SITE_URL or request.build_absolute_uri("/").rstrip("/")
    return {
        "seo_title": title,
        "seo_description": description,
        "canonical_url": f"{site_url}{request.path}",
        "site_url": site_url,
    }


def published_posts():
    return Post.objects.filter(is_published=True).filter(
        Q(published_at__isnull=True) | Q(published_at__lte=timezone.now())
    )


def home(request):
    projects = list(Project.objects.filter(is_published=True)[:2])
    latest_posts = published_posts()[:3]
    return render(
        request,
        "core/index.html",
        {
            **page_context(
                request,
                "Eddyforge | Full-Stack Development",
                "Johnny Edwards builds full-stack web products, e-commerce platforms, and custom software for ambitious teams.",
            ),
            "projects": projects,
            "latest_posts": latest_posts,
        },
    )


def about(request):
    return render(
        request,
        "core/about.html",
        page_context(
            request,
            "About Johnny Edwards | Eddyforge",
            "Meet Johnny Edwards, a Kenya-based full-stack developer building practical digital products with Django and modern frontend tools.",
        ),
    )


def contact(request):
    page_data = page_context(
        request,
        "Contact Eddyforge | Start a Conversation",
        "Tell Johnny about your web development or software project.",
    )
    if request.method == "POST":
        contact_message = ContactMessage(
            first_name=request.POST.get("first_name", "").strip(),
            last_name=request.POST.get("last_name", "").strip(),
            email=request.POST.get("email", "").strip(),
            service_needed=request.POST.get("service_needed", "").strip(),
            project_brief=request.POST.get("project_brief", "").strip(),
        )
        try:
            contact_message.full_clean()
        except ValidationError as error:
            messages.error(request, " ".join(error.messages))
            return render(
                request,
                "core/contact.html",
                {**page_data, "form_data": request.POST},
            )

        contact_message.save()
        messages.success(request, "Your message has been sent successfully.")
        return redirect("core:contact")

    return render(request, "core/contact.html", {**page_data, "form_data": {}})


@staff_member_required
def admin_page(request):
    return render(request, "core/admin.html")


def login(request):
    return redirect("core:portal_login")


@login_required
def portal_dashboard(request):
    projects = request.user.client_projects.prefetch_related("milestones")
    return render(
        request,
        "core/portal/dashboard.html",
        {
            **page_context(
                request,
                "Client Portal | Eddyforge",
                "Review your Eddyforge project status, milestones, and shared resources.",
            ),
            "projects": projects,
        },
    )


@login_required
def portal_project_detail(request, slug):
    project = get_object_or_404(
        ClientProject.objects.prefetch_related("milestones"),
        slug=slug,
        client=request.user,
    )
    shared_links = SharedLink.objects.filter(project=project, is_active=True).filter(
        Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
    )
    return render(
        request,
        "core/portal/project_detail.html",
        {
            **page_context(
                request,
                f"{project.title} | Client Portal | Eddyforge",
                project.summary or f"Status and milestones for {project.title}.",
            ),
            "project": project,
            "shared_links": shared_links,
        },
    )


def projects(request):
    published_projects = list(
        Project.objects.filter(is_published=True).prefetch_related("images")
    )
    return render(
        request,
        "core/projects.html",
        {
            **page_context(
                request,
                "Selected Projects | Eddyforge",
                "Explore software projects by Eddyforge, including resource booking and property management systems.",
            ),
            "published_projects": published_projects,
            "server_projects": bool(published_projects),
        },
    )


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug, is_published=True)
    published_projects = list(Project.objects.filter(is_published=True))
    position = next(
        (index for index, item in enumerate(published_projects) if item.pk == project.pk),
        None,
    )
    previous_project = (
        published_projects[position - 1] if position is not None and position > 0 else None
    )
    next_project = (
        published_projects[position + 1]
        if position is not None and position + 1 < len(published_projects)
        else None
    )
    summary = project.short_description or project.description
    return render(
        request,
        "core/project_detail.html",
        {
            **page_context(request, f"{project.title} | Eddyforge", summary[:320]),
            "project": project,
            "previous_project": previous_project,
            "next_project": next_project,
        },
    )


def services(request):
    published_services = list(
        Service.objects.filter(is_published=True).prefetch_related("faqs", "related_projects")
    )
    return render(
        request,
        "core/services.html",
        {
            **page_context(
                request,
                "Web Development Services | Eddyforge",
                "Explore e-commerce development, corporate web solutions, custom software, and UI/UX services.",
            ),
            "published_services": published_services,
            "server_services": bool(published_services),
        },
    )


def service_detail(request, slug):
    service = get_object_or_404(
        Service.objects.prefetch_related("faqs", "related_projects"),
        slug=slug,
        is_published=True,
    )
    audience_copy = {
        "ecommerce": "For businesses that need a storefront, checkout, and order workflow shaped around their operation.",
        "corporate-web": "For organizations that need a clear web presence, company portal, or internal dashboard.",
        "custom-software": "For teams looking to support a specific workflow with purpose-built software.",
        "ui-ux": "For teams that need a responsive, consistent interface for a website or web application.",
    }
    faqs = list(service.faqs.all())
    related_projects = list(service.related_projects.filter(is_published=True))
    faq_schema = None
    if faqs:
        faq_schema = json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq.question,
                        "acceptedAnswer": {"@type": "Answer", "text": faq.answer},
                    }
                    for faq in faqs
                ],
            }
        )
        faq_schema = (
            faq_schema.replace("<", "\\u003c")
            .replace(">", "\\u003e")
            .replace("&", "\\u0026")
        )
    seo = page_context(
        request,
        service.meta_title or f"{service.title} | Eddyforge",
        service.meta_description or service.description[:320],
    )
    return render(
        request,
        "core/service_detail.html",
        {
            **seo,
            "service": service,
            "audience_copy": audience_copy.get(
                service.slug,
                "For people and teams with a clear digital product or workflow to improve.",
            ),
            "faqs": faqs,
            "related_projects": related_projects,
            "faq_schema": faq_schema,
        },
    )


def resume(request):
    from core.data.resume import RESUME_DATA

    resume_data = deepcopy(RESUME_DATA)
    published_projects = Project.objects.filter(is_published=True)
    if published_projects.exists():
        resume_data["projects"] = [
            {
                "title": project.title,
                "slug": project.slug,
                "summary": project.short_description or project.description,
                "stack": project.stack_list,
                "repository": project.repo,
            }
            for project in published_projects
        ]

    resume_root = (settings.BASE_DIR / "core" / "static" / "core").resolve()
    resume_file = (resume_root / settings.RESUME_PDF).resolve()
    has_resume_pdf = (
        resume_root in resume_file.parents
        and resume_file.is_file()
        and resume_file.suffix.lower() == ".pdf"
    )
    resume_pdf_path = "core/" + settings.RESUME_PDF.replace("\\", "/")
    return render(
        request,
        "core/resume.html",
        {
            **page_context(
                request,
                "Resume | Johnny Edwards — Eddyforge",
                resume_data["summary"],
            ),
            "resume_data": resume_data,
            "resume_pdf_path": resume_pdf_path,
            "has_resume_pdf": has_resume_pdf,
        },
    )


def privacy(request):
    return render(
        request,
        "core/privacy.html",
        {
            **page_context(
                request,
                "Privacy | Eddyforge",
                "How Eddyforge handles information shared through project inquiry and contact forms.",
            ),
            "contact_email": settings.CONTACT_EMAIL,
        },
    )


def uses(request):
    return render(
        request,
        "core/uses.html",
        {
            **page_context(
                request,
                "Uses | Eddyforge",
                "Tools, languages, frameworks, and services used to build and ship Eddyforge projects.",
            ),
            "use_groups": USE_GROUPS,
        },
    )


def now(request):
    update = NowUpdate.objects.filter(is_published=True).first()
    return render(
        request,
        "core/now.html",
        {
            **page_context(
                request,
                "Now | Eddyforge",
                "A short update on what Johnny Edwards is working on now.",
            ),
            "now_update": update,
            "rendered_update": render_markdown(update.body) if update else None,
        },
    )


def lab(request):
    experiments = LabExperiment.objects.filter(is_published=True)
    return render(
        request,
        "core/lab.html",
        {
            **page_context(
                request,
                "Lab | Eddyforge",
                "Small browser-based tools and experiments built by Eddyforge.",
            ),
            "experiments": experiments,
        },
    )


def lab_detail(request, slug):
    experiment = get_object_or_404(LabExperiment, slug=slug, is_published=True)
    demo_path = experiment.demo_path.strip()
    parsed_demo = urlsplit(demo_path)
    if parsed_demo.scheme:
        if parsed_demo.scheme not in {"http", "https"} or not parsed_demo.netloc:
            demo_url = ""
        else:
            demo_url = demo_path
    else:
        static_path = PurePosixPath(demo_path.lstrip("/"))
        if ".." in static_path.parts or not static_path.parts:
            demo_url = ""
        elif static_path.parts[0] == "static":
            demo_url = "/" + static_path.as_posix()
        else:
            demo_url = static(f"core/{static_path.as_posix()}")
    if not demo_url:
        raise ValueError(f"Invalid demo path configured for experiment {experiment.slug}.")
    return render(
        request,
        "core/lab_detail.html",
        {
            **page_context(request, f"{experiment.title} | Eddyforge", experiment.summary[:320]),
            "experiment": experiment,
            "demo_url": demo_url,
        },
    )


def start(request):
    page_data = page_context(
        request,
        "Start a Project | Eddyforge",
        "Share your project goals, timeline, and budget with Johnny Edwards.",
    )
    if request.method == "POST":
        form = ProjectInquiryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("core:start_thanks")
    else:
        service_type = project_type_for_service(request.GET.get("service", ""))
        form = ProjectInquiryForm(initial={"project_type": service_type} if service_type else {})
    return render(
        request,
        "core/start.html",
        {
            **page_data,
            "form": form,
        },
    )


def start_thanks(request):
    return render(
        request,
        "core/start_thanks.html",
        {
            **page_context(
                request,
                "Thanks for Reaching Out | Eddyforge",
                "Your project inquiry has been received. Here is what happens next.",
            ),
            "response_time_text": settings.RESPONSE_TIME_TEXT,
            "booking_url": settings.BOOKING_URL,
        },
    )


def blog_list(request):
    selected_tag = request.GET.get("tag", "").strip()
    posts = published_posts()
    if selected_tag:
        posts = posts.filter(tags__icontains=selected_tag)
    page_obj = Paginator(posts, 9).get_page(request.GET.get("page"))
    featured_post = page_obj.object_list.first() if page_obj.number == 1 else None
    grid_posts = list(page_obj.object_list)
    if featured_post:
        grid_posts = grid_posts[1:]
    return render(
        request,
        "core/blog_list.html",
        {
            **page_context(
                request,
                "Writing | Eddyforge",
                "Notes on building practical software, Django, deployment, and the work behind Eddyforge.",
            ),
            "page_obj": page_obj,
            "featured_post": featured_post,
            "posts": grid_posts,
            "selected_tag": selected_tag,
        },
    )


def blog_detail(request, slug):
    post = get_object_or_404(published_posts(), slug=slug)
    rendered_body = render_markdown(post.body)
    matching_posts = []
    post_tags = {tag.casefold() for tag in post.tags_list}
    for candidate in published_posts().exclude(pk=post.pk)[:30]:
        if post_tags.intersection(tag.casefold() for tag in candidate.tags_list):
            matching_posts.append(candidate)
        if len(matching_posts) == 3:
            break
    if len(matching_posts) < 3:
        matching_ids = {item.pk for item in matching_posts}
        matching_posts.extend(
            candidate
            for candidate in published_posts().exclude(pk=post.pk)[:10]
            if candidate.pk not in matching_ids
        )
        matching_posts = matching_posts[:3]

    ordered_posts = list(published_posts())
    post_index = next(index for index, item in enumerate(ordered_posts) if item.pk == post.pk)
    plain_text = re.sub(r"[#*_`>\[\]()]", " ", post.body)
    reading_minutes = max(1, ceil(len(plain_text.split()) / 220))
    structured_data = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": post.title,
            "description": post.excerpt,
            "datePublished": post.published_at.isoformat() if post.published_at else "",
            "dateModified": post.updated_at.isoformat(),
            "author": {"@type": "Person", "name": "Johnny Edwards"},
            "mainEntityOfPage": f"{settings.SITE_URL or request.build_absolute_uri('/').rstrip('/')}{request.path}",
        }
    )
    structured_data = (
        structured_data.replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )
    return render(
        request,
        "core/blog_detail.html",
        {
            **page_context(request, f"{post.title} | Eddyforge", post.excerpt[:320]),
            "post": post,
            "rendered_body": rendered_body,
            "related_posts": matching_posts,
            "previous_post": ordered_posts[post_index - 1] if post_index > 0 else None,
            "next_post": (
                ordered_posts[post_index + 1]
                if post_index + 1 < len(ordered_posts)
                else None
            ),
            "reading_minutes": reading_minutes,
            "structured_data": structured_data,
        },
    )


def robots_txt(request):
    site_url = settings.SITE_URL or request.build_absolute_uri("/").rstrip("/")
    return HttpResponse(
        f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n",
        content_type="text/plain",
    )


def custom_404(request, exception):
    best_projects = Project.objects.filter(is_published=True)[:2]
    return render(
        request,
        "core/404.html",
        {
            **page_context(
                request,
                "Page not found | Eddyforge",
                "The page you requested could not be found.",
            ),
            "best_projects": best_projects,
        },
        status=404,
    )
