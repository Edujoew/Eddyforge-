from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render

from .models import ContactMessage


def home(request):
    return render(request, "core/index.html")


def about(request):
    return render(request, "core/about.html")


def contact(request):
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
                {"form_data": request.POST},
            )

        contact_message.save()
        messages.success(request, "Your message has been sent successfully.")
        return redirect("core:contact")

    return render(request, "core/contact.html", {"form_data": {}})


def admin_page(request):
    return render(request, "core/admin.html")


def login(request):
    return render(request, "core/login.html")


def projects(request):
    return render(request, "core/projects.html")


def services(request):
    return render(request, "core/services.html")
