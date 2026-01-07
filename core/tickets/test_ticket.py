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
            first_name="Test",
            last_name="User",
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
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="pass12345!",
        )
        self.other_user = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="pass12345!",
        )
        self.superuser = User.objects.create_superuser(
            username="adminuser",
            email="admin@example.com",
            password="pass12345!",
        )

        self.ticket = Ticket.objects.create(
            title="Cannot log in",
            body="User cannot log into the system.",
            author=self.user,
        )
        self.other_ticket = Ticket.objects.create(
            title="Other ticket",
            body="Other ticket body",
            author=self.other_user,
        )

    def test_ticket_list_view_status_code_200(self):
        url = reverse("ticket_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_ticket_list_view_uses_correct_template(self):
        url = reverse("ticket_list")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")

    def test_ticket_list_view_shows_all_tickets_to_anonymous_user(self):
        url = reverse("ticket_list")
        response = self.client.get(url)
        self.assertContains(response, self.ticket.title)
        self.assertContains(response, self.other_ticket.title)

    def test_ticket_list_view_shows_all_tickets_to_logged_in_user(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_list")
        response = self.client.get(url)
        self.assertContains(response, self.ticket.title)
        self.assertContains(response, self.other_ticket.title)

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

    def test_logged_in_user_can_create_ticket_and_author_is_set_automatically(
            self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_add")

        response = self.client.post(
            url,
            data={
                "title": "New ticket",
                "body": "Something is broken.",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_list.html")
        created = Ticket.objects.get(title="New ticket")
        self.assertEqual(created.author, self.user)

    def test_logged_in_user_cannot_create_ticket_for_someone_else_even_if_author_is_posted(
            self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_add")

        response = self.client.post(
            url,
            data={
                "title": "Spoof ticket",
                "body": "Trying to spoof author.",
                "author": self.other_user.pk,
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        created = Ticket.objects.get(title="Spoof ticket")
        self.assertEqual(created.author, self.user)

    def test_owner_can_edit_own_ticket(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_edit", args=[self.ticket.pk])

        response = self.client.post(
            url,
            data={
                "title": "Cannot log in - updated",
                "body": "Updated details",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.title, "Cannot log in - updated")
        self.assertEqual(self.ticket.body, "Updated details")
        self.assertEqual(self.ticket.author, self.user)

    def test_non_owner_cannot_edit_someone_elses_ticket(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_edit", args=[self.other_ticket.pk])

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_superuser_can_edit_any_ticket(self):
        self.client.login(username="adminuser", password="pass12345!")
        url = reverse("ticket_edit", args=[self.other_ticket.pk])

        response = self.client.post(
            url,
            data={
                "title": "Admin updated",
                "body": "Admin updated body",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.other_ticket.refresh_from_db()
        self.assertEqual(self.other_ticket.title, "Admin updated")
        self.assertEqual(self.other_ticket.body, "Admin updated body")
        self.assertEqual(self.other_ticket.author, self.other_user)

    def test_owner_can_delete_own_ticket(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_delete", args=[self.ticket.pk])

        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Ticket.objects.filter(pk=self.ticket.pk).exists())

    def test_non_owner_cannot_delete_someone_elses_ticket(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_delete", args=[self.other_ticket.pk])

        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(
            Ticket.objects.filter(
                pk=self.other_ticket.pk).exists())

    def test_superuser_can_delete_any_ticket(self):
        self.client.login(username="adminuser", password="pass12345!")
        url = reverse("ticket_delete", args=[self.other_ticket.pk])

        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            Ticket.objects.filter(
                pk=self.other_ticket.pk).exists())

    def test_ticket_add_uses_correct_template(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_add")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_form.html")

    def test_ticket_edit_uses_correct_template_for_owner(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_edit", args=[self.ticket.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_form.html")

    def test_ticket_delete_uses_correct_template_for_owner(self):
        self.client.login(username="testuser", password="pass12345!")
        url = reverse("ticket_delete", args=[self.ticket.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "tickets/ticket_delete.html")
        self.assertContains(response, "Are you sure you want to delete")
