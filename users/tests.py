from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserTests(APITestCase):
    def test_register(self):
        url = reverse("register")
        data = {"username": "newuser", "email": "n@n.ru", "password": "strongpass123"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertNotIn("password", response.data)

    def test_login(self):
        User.objects.create_user(username="u1", password="pass12345678")
        url = reverse("login")
        response = self.client.post(url, {"username": "u1", "password": "pass12345678"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_profile_requires_auth(self):
        url = reverse("profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_link_telegram(self):
        user = User.objects.create_user(username="u2", password="pass12345678")
        self.client.force_authenticate(user=user)
        url = reverse("link-telegram")
        response = self.client.post(url, {"chat_id": "123456789"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertEqual(user.telegram_chat_id, "123456789")
