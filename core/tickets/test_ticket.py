from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Ticket


class TestTicketModel(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="pass12345!",
        )
        self.ticket = Ticket.objects.create(
            title="Printer not working",
            body="The office printer is showing an error code.",
            author=self.user,
        )

    def test_ticket_str_returns_title(self):
        self.assertEqual(str(self.ticket), "Printer not working")


class TestTicketViews(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="pass12345!",
        )
        self.other_user = get_user_model().objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="pass12345!",
        )
        self.superuser = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="pass12345!",
        )

        self.ticket = Ticket.objects.create(
            title="Cannot log in",
            body="User cannot log into the portal.",
            author=self.user,
            is_completed=False,
        )
        self.other_ticket = Ticket.objects.create(
            title="VPN drops frequently",
            body="VPN disconnects multiple times per day.",
            author=self.other_user,
            is_completed=False,
        )

    def test_ticket_list_view_redirects_anonymous_user_to_login(self):
        url = reverse("ticket_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={url}")

    def test_ticket_list_view_status_code_200_for_logged_in_user(self):
        self.client.login(username="testuser", password="pass12345!")
        response = self.client.get(reverse("ticket_list"))
        self.assertEqual(response.status_code, 200)

    def test_ticket_list_view_uses_correct_template_for_logged_in_user(self):
        self.client.login(username="testuser", password="pass12345!")
        response = self.client.get(reverse("ticket_list"))
        self.assertTemplateUsed(response, "tickets/ticket_list.html")

    def test_ticket_list_view_shows_tickets_for_logged_in_user(self):
        self.client.login(username="testuser", password="pass12345!")
        response = self.client.get(reverse("ticket_list"))
        self.assertContains(response, self.ticket.title)

    def test_ticket_list_view_ordering_completed_then_date_desc(self):
        self.client.login(username="testuser", password="pass12345!")

        t1 = Ticket.objects.create(
            title="Old incomplete",
            body="Older, incomplete.",
            author=self.user,
            is_completed=False,
        )
        t2 = Ticket.objects.create(
            title="New incomplete",
            body="Newer, incomplete.",
            author=self.user,
            is_completed=False,
        )
        t3 = Ticket.objects.create(
            title="Newest complete",
            body="Complete ticket.",
            author=self.user,
            is_completed=True,
        )

        now = timezone.now()
        Ticket.objects.filter(pk=t1.pk).update(date=now - timedelta(days=3))
        Ticket.objects.filter(pk=t2.pk).update(date=now - timedelta(days=1))
        Ticket.objects.filter(pk=t3.pk).update(date=now)

        response = self.client.get(reverse("ticket_list"))
        titles = [t.title for t in response.context["object_list"]]

        self.assertLess(titles.index("New incomplete"), titles.index("Old incomplete"))
        self.assertLess(titles.index("Old incomplete"), titles.index("Newest complete"))

    def test_ticket_create_view_redirects_anonymous_user_to_login(self):
        url = reverse("ticket_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={url}")

    def test_ticket_create_view_creates_ticket_and_sets_author(self):
        self.client.login(username="testuser", password="pass12345!")
        response = self.client.post(
            reverse("ticket_add"),
            data={
                "title": "Email not sending",
                "body": "Outgoing mail is stuck in the outbox.",
                "is_completed": False,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("ticket_list"))

        created = Ticket.objects.get(title="Email not sending")
        self.assertEqual(created.author, self.user)
        self.assertEqual(created.body, "Outgoing mail is stuck in the outbox.")
        self.assertFalse(created.is_completed)

    def test_ticket_update_view_redirects_anonymous_user_to_login(self):
        url = reverse("ticket_edit", args=[self.ticket.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={url}")

    def test_ticket_update_view_owner_can_update(self):
        self.client.login(username="testuser", password="pass12345!")
        response = self.client.post(
            reverse("ticket_edit", args=[self.ticket.pk]),
            data={
                "title": "Cannot log in (updated)",
                "body": "Password reset attempted, still failing.",
                "is_completed": True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("ticket_list"))

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.title, "Cannot log in (updated)")
        self.assertEqual(self.ticket.body, "Password reset attempted, still failing.")
        self.assertTrue(self.ticket.is_completed)

    def test_ticket_update_view_non_owner_gets_404(self):
        self.client.login(username="otheruser", password="pass12345!")
        response = self.client.get(reverse("ticket_edit", args=[self.ticket.pk]))
        self.assertEqual(response.status_code, 404)

    def test_ticket_update_view_superuser_can_update_any_ticket(self):
        self.client.login(username="admin", password="pass12345!")
        response = self.client.post(
            reverse("ticket_edit", args=[self.ticket.pk]),
            data={
                "title": "Admin updated",
                "body": "Reviewed by admin.",
                "is_completed": True,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("ticket_list"))

        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.title, "Admin updated")
        self.assertTrue(self.ticket.is_completed)

    def test_ticket_delete_view_redirects_anonymous_user_to_login(self):
        url = reverse("ticket_delete", args=[self.ticket.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={url}")

    def test_ticket_delete_view_owner_can_delete(self):
        self.client.login(username="testuser", password="pass12345!")
        response = self.client.post(reverse("ticket_delete", args=[self.ticket.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("ticket_list"))

        self.assertFalse(Ticket.objects.filter(pk=self.ticket.pk).exists())

    def test_ticket_delete_view_non_owner_gets_404(self):
        self.client.login(username="otheruser", password="pass12345!")
        response = self.client.post(reverse("ticket_delete", args=[self.ticket.pk]))
        self.assertEqual(response.status_code, 404)

        self.assertTrue(Ticket.objects.filter(pk=self.ticket.pk).exists())

    def test_ticket_delete_view_superuser_can_delete_any_ticket(self):
        self.client.login(username="admin", password="pass12345!")
        response = self.client.post(reverse("ticket_delete", args=[self.other_ticket.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("ticket_list"))

        self.assertFalse(Ticket.objects.filter(pk=self.other_ticket.pk).exists())

    def test_ticket_complete_redirects_anonymous_user_to_login(self):
        url = reverse("ticket_complete", args=[self.ticket.pk])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        login_url = reverse("login")
        self.assertRedirects(response, f"{login_url}?next={url}")

    def test_ticket_complete_marks_ticket_complete_and_redirects(self):
        self.client.login(username="testuser", password="pass12345!")
        response = self.client.post(reverse("ticket_complete", args=[self.ticket.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("ticket_list"))

        self.ticket.refresh_from_db()
        self.assertTrue(self.ticket.is_completed)
