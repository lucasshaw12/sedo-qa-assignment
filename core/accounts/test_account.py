from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CustomUserModelTests(TestCase):
    def test_custom_user_str_format(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="lshaw",
            email="lucas@example.com",
            password="pass12345!",
            first_name="Lucas",
            last_name="Shaw",
        )
        self.assertEqual(str(user), "Lucas Shaw (lshaw)")

    def test_num_tickets_assigned_defaults_to_zero(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="tuser",
            email="tuser@example.com",
            password="pass12345!",
        )
        self.assertEqual(user.num_tickets_assigned, 0)


class SignUpViewTests(TestCase):
    def test_signup_url_resolves_and_returns_200(self):
        url = reverse("signup")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_signup_uses_correct_template(self):
        url = reverse("signup")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_creates_user_and_redirects_to_login(self):
        url = reverse("signup")
        response = self.client.post(
            url,
            data={
                "username": "newuser",
                "email": "newuser@example.com",
                "password1": "StrongPass12345!",
                "password2": "StrongPass12345!",
            },
        )

        # success_url is reverse_lazy('login')
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response["Location"])

        User = get_user_model()
        self.assertTrue(User.objects.filter(username="newuser").exists())

        created = User.objects.get(username="newuser")
        self.assertEqual(created.email, "newuser@example.com")
        self.assertTrue(created.check_password("StrongPass12345!"))

    def test_signup_invalid_does_not_create_user(self):
        url = reverse("signup")
        response = self.client.post(
            url,
            data={
                "username": "baduser",
                "email": "baduser@example.com",
                "password1": "StrongPass12345!",
                "password2": "DifferentPass999!",
            },
        )

        self.assertEqual(response.status_code, 200)  # form re-rendered
        self.assertContains(response, "The two password fields didn’t match")

        User = get_user_model()
        self.assertFalse(User.objects.filter(username="baduser").exists())
