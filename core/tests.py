from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import (
    ClientProject,
    ContactMessage,
    LabExperiment,
    Milestone,
    NowUpdate,
    Post,
    Project,
    ProjectInquiry,
    Service,
    SharedLink,
)


class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.project = Project.objects.create(
            title="Example project",
            slug="example-project",
            description="An example case study.",
            is_published=True,
        )
        cls.service = Service.objects.create(
            title="Example service",
            slug="example-service",
            description="An example service.",
            is_published=True,
        )
        cls.post = Post.objects.create(
            title="Example post",
            slug="example-post",
            excerpt="An example article.",
            body="Article body.",
            is_published=True,
            published_at=timezone.now(),
        )
        LabExperiment.objects.create(
            title="Contrast checker",
            slug="contrast-checker",
            summary="Check text contrast.",
            demo_path="lab/contrast-checker/index.html",
            is_published=True,
        )
        NowUpdate.objects.create(body="Working on the portfolio.", is_published=True)

    def test_public_pages_render(self):
        paths = (
            "/",
            "/about/",
            "/contact/",
            "/projects/",
            self.project.get_absolute_url(),
            "/start/",
            "/start/thanks/",
            "/blog/",
            self.post.get_absolute_url(),
            "/blog/feed.xml",
            "/services/",
            self.service.get_absolute_url(),
            "/resume/",
            "/privacy/",
            "/uses/",
            "/now/",
            "/lab/",
            "/lab/contrast-checker/",
            "/robots.txt",
            "/sitemap.xml",
        )
        for path in paths:
            with self.subTest(path=path):
                self.assertEqual(self.client.get(path).status_code, 200)

    def test_contact_form_persists_valid_message(self):
        response = self.client.post(
            "/contact/",
            {
                "first_name": "Ada",
                "last_name": "Lovelace",
                "email": "ada@example.com",
                "service_needed": "custom_software",
                "project_brief": "Build a useful application.",
            },
        )
        self.assertRedirects(response, "/contact/")
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_project_inquiry_persists_valid_submission(self):
        response = self.client.post(
            "/start/",
            {
                "name": "Ada Lovelace",
                "email": "ada@example.com",
                "company": "Analytical Engines",
                "project_type": "custom_software",
                "budget_range": "500_1500",
                "timeline": "2_4_weeks",
                "description": "Build a useful application.",
                "reference_links": "https://example.com",
                "website": "",
            },
        )
        self.assertRedirects(response, "/start/thanks/")
        self.assertEqual(ProjectInquiry.objects.count(), 1)

    @override_settings(DEBUG=False)
    def test_unknown_page_uses_branded_not_found_response(self):
        response = self.client.get("/does-not-exist/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Page not found", status_code=404)


class ClientPortalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        user_model = get_user_model()
        cls.client_user = user_model.objects.create_user(
            username="client",
            password="safe-test-password",
        )
        cls.other_user = user_model.objects.create_user(
            username="another-client",
            password="safe-test-password",
        )
        cls.staff_user = user_model.objects.create_user(
            username="staff",
            password="safe-test-password",
            is_staff=True,
        )
        cls.project = ClientProject.objects.create(
            client=cls.client_user,
            title="Private project",
            slug="private-project",
            summary="A client-only project.",
            status="in_progress",
        )
        cls.other_project = ClientProject.objects.create(
            client=cls.other_user,
            title="Another private project",
            slug="another-private-project",
        )
        cls.milestone = Milestone.objects.create(
            project=cls.project,
            title="First milestone",
            details="Project work is underway.",
            status="in_progress",
        )
        SharedLink.objects.create(
            project=cls.project,
            title="Active resource",
            url="https://example.com/resource",
        )
        SharedLink.objects.create(
            project=cls.project,
            title="Expired resource",
            url="https://example.com/expired",
            expires_at=timezone.now() - timedelta(days=1),
        )

    def test_anonymous_portal_requests_redirect_to_login(self):
        for path in ("/portal/", self.project.get_absolute_url()):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertRedirects(
                    response,
                    f"/portal/login/?next={path}",
                    fetch_redirect_response=False,
                )

    def test_portal_login_authenticates_and_redirects_to_dashboard(self):
        response = self.client.post(
            "/portal/login/",
            {"username": "client", "password": "safe-test-password"},
        )
        self.assertRedirects(response, "/portal/")
        self.assertContains(self.client.get("/portal/"), "Private project")
        self.assertNotContains(self.client.get("/portal/"), "Another private project")

    def test_client_cannot_view_another_clients_project(self):
        self.client.force_login(self.client_user)
        response = self.client.get(self.other_project.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_project_detail_shows_milestones_and_only_current_links(self):
        self.client.force_login(self.client_user)
        response = self.client.get(self.project.get_absolute_url())
        self.assertContains(response, self.milestone.title)
        self.assertContains(response, "Active resource")
        self.assertNotContains(response, "Expired resource")

    def test_legacy_admin_panel_is_staff_only(self):
        anonymous_response = self.client.get("/admin-panel/")
        self.assertEqual(anonymous_response.status_code, 302)
        self.client.force_login(self.client_user)
        self.assertNotEqual(self.client.get("/admin-panel/").status_code, 200)
        self.client.force_login(self.staff_user)
        self.assertEqual(self.client.get("/admin-panel/").status_code, 200)

    def test_logout_uses_post_and_clears_authentication(self):
        self.client.force_login(self.client_user)
        self.assertEqual(self.client.get("/portal/logout/").status_code, 405)
        response = self.client.post("/portal/logout/")
        self.assertRedirects(response, "/portal/login/")
        self.assertNotIn("_auth_user_id", self.client.session)
