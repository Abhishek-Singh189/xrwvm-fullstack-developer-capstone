from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthenticationTests(TestCase):
    def setUp(self):
        self.password = "CorrectHorse9!"
        self.user = User.objects.create_user(
            username="reviewer",
            password=self.password,
            email="reviewer@example.com",
            first_name="Alex",
            last_name="Reviewer",
        )

    def test_login(self):
        response = self.client.post(
            reverse("djangoapp:login"),
            {"userName": self.user.username, "password": self.password},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "Authenticated")

    def test_logout(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("djangoapp:logout"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "Logged out")
