from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

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
        self.ticket = Ticket.objects.create(
            title="Cannot log in",
            body="User cannot log into the system.",
            author=self.user,
        )

    def test_ticket_list_view_status_code_200(self):
        url = reverse("ticket_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ticket_list_view_uses_correct_template(self):
        url = reverse("ticket_list")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")

    def test_ticket_list_view_shows_ticket_fields(self):
        url = reverse("ticket_list")
        response = self.client.get(url)
        self.assertContains(response, "Cannot log in")
        self.assertContains(response, "User cannot log into the system.")
        self.assertContains(response, str(self.user))

    def test_ticket_add_requires_login(self):
        url = reverse("ticket_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_ticket_edit_requires_login(self):
        url = reverse("ticket_edit", args=[self.ticket.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_ticket_delete_requires_login(self):
        url = reverse("ticket_delete", args=[self.ticket.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

    def test_logged_in_user_can_create_ticket(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_add")

        response = self.client.post(
            url,
            data={
                "title": "New ticket",
                "body": "Something is broken.",
                "author": self.user.pk,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")
        self.assertTrue(Ticket.objects.filter(title="New ticket").exists())

    def test_logged_in_user_can_edit_ticket(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_edit", args=[self.ticket.pk])

        response = self.client.post(
            url,
            data={
                "title": "Cannot log in - updated",
                "body": "Updated details",
                "author": self.user.pk,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.title, "Cannot log in - updated")
        self.assertEqual(self.ticket.body, "Updated details")

    def test_logged_in_user_can_delete_ticket(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_delete", args=[self.ticket.pk])

        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Ticket.objects.filter(pk=self.ticket.pk).exists())

    def test_ticket_add_uses_correct_template(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_form.html")

    def test_ticket_edit_uses_correct_template(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_edit", args=[self.ticket.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_form.html")

    def test_ticket_delete_uses_correct_template(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_delete", args=[self.ticket.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_delete.html")
        self.assertContains(response, "Are you sure you want to delete")

