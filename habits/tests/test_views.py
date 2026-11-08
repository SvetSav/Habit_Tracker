from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit

User = get_user_model()


class HabitViewSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p" * 10)
        self.other = User.objects.create_user(username="other", password="p" * 10)
        self.client.force_authenticate(user=self.user)

    def _data(self, **kwargs):
        base = {
            "place": "Дом",
            "time": "12:00",
            "action": "Зарядка",
            "duration": 60,
            "periodicity": 1,
        }
        base.update(kwargs)
        return base

    def test_list_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("habit-list"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_only_own_habits(self):
        Habit.objects.create(
            user=self.user, place="A", time="12:00", action="Моя", duration=60
        )
        Habit.objects.create(
            user=self.other, place="B", time="12:00", action="Чужая", duration=60
        )
        response = self.client.get(reverse("habit-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["action"], "Моя")

    def test_pagination_limit_offset(self):
        for i in range(12):
            Habit.objects.create(
                user=self.user, place=f"P{i}", time="12:00", action=f"A{i}", duration=60
            )
        response = self.client.get(reverse("habit-list"), {"limit": 5, "offset": 0})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 12)
        self.assertEqual(len(response.data["results"]), 5)
        self.assertIn("next", response.data)

    def test_create_habit(self):
        response = self.client.post(reverse("habit-list"), self._data())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), 1)
        habit = Habit.objects.first()
        self.assertEqual(habit.user, self.user)

    def test_create_invalid(self):
        response = self.client.post(reverse("habit-list"), self._data(duration=200))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_own(self):
        habit = Habit.objects.create(
            user=self.user, place="P", time="12:00", action="A", duration=60
        )
        response = self.client.get(reverse("habit-detail", args=[habit.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_retrieve_foreign_forbidden(self):
        habit = Habit.objects.create(
            user=self.other, place="P", time="12:00", action="A", duration=60
        )
        response = self.client.get(reverse("habit-detail", args=[habit.id]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_own(self):
        habit = Habit.objects.create(
            user=self.user, place="P", time="12:00", action="A", duration=60
        )
        response = self.client.patch(
            reverse("habit-detail", args=[habit.id]), {"action": "New"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit.refresh_from_db()
        self.assertEqual(habit.action, "New")

    def test_delete_own(self):
        habit = Habit.objects.create(
            user=self.user, place="P", time="12:00", action="A", duration=60
        )
        response = self.client.delete(reverse("habit-detail", args=[habit.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.count(), 0)

    def test_public_list_anonymous(self):
        Habit.objects.create(
            user=self.other,
            place="P",
            time="12:00",
            action="Публичная",
            duration=60,
            is_public=True,
        )
        Habit.objects.create(
            user=self.other,
            place="P",
            time="12:00",
            action="Скрытая",
            duration=60,
            is_public=False,
        )
        self.client.force_authenticate(user=None)
        response = self.client.get(reverse("habit-public"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["action"], "Публичная")

    def test_public_cannot_edit(self):
        habit = Habit.objects.create(
            user=self.other,
            place="P",
            time="12:00",
            action="Пуб",
            duration=60,
            is_public=True,
        )
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            reverse("habit-detail", args=[habit.id]), {"action": "Hack"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
