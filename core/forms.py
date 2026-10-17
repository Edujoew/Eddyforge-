from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import ContactMessage, ProjectInquiry


class ProjectInquiryForm(forms.ModelForm):
    TIMELINE_CHOICES = [
        ("under_2_weeks", "As soon as possible (under 2 weeks)"),
        ("2_4_weeks", "2-4 weeks"),
        ("1_2_months", "1-2 months"),
        ("flexible", "Flexible / still deciding"),
    ]

    timeline = forms.ChoiceField(choices=TIMELINE_CHOICES)
    website = forms.CharField(
        required=False,
        label="Leave this field blank",
        widget=forms.TextInput(
            attrs={"autocomplete": "off", "tabindex": "-1", "class": "honeypot"}
        ),
    )

    class Meta:
        model = ProjectInquiry
        fields = (
            "name",
            "email",
            "company",
            "project_type",
            "budget_range",
            "timeline",
            "description",
            "reference_links",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "reference_links": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "project_type": "What do you need built?",
            "budget_range": "Budget range",
            "description": "What are you looking to build?",
            "reference_links": "Reference links",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["reference_links"].help_text = (
            "Optional; add one https:// or http:// link per line."
        )
        for name, field in self.fields.items():
            if field.widget.is_hidden or name == "website":
                continue
            field.widget.attrs.setdefault("class", "form-input")

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("website"):
            raise ValidationError("Unable to submit this form.")
        return cleaned_data

    def clean_reference_links(self):
        value = self.cleaned_data.get("reference_links", "")
        urls = [line.strip() for line in value.splitlines() if line.strip()]
        validate_url = URLValidator(schemes=("http", "https"))
        if len(urls) > 10:
            raise ValidationError("Please provide no more than 10 reference links.")
        for url in urls:
            try:
                validate_url(url)
            except ValidationError as error:
                raise ValidationError(
                    "Enter a valid http:// or https:// URL on each line."
                ) from error
        return "\n".join(urls)


def project_type_for_service(slug):
    service_types = {
        "ecommerce": "e_commerce",
        "corporate-web": "corporate_web",
        "custom-software": "custom_software",
        "ui-ux": "ui_ux",
    }
    project_type = service_types.get(slug)
    valid_choices = {choice for choice, label in ContactMessage.SERVICE_CHOICES}
    return project_type if project_type in valid_choices else ""
