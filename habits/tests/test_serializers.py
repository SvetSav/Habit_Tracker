from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIRequestFactory

from habits.models import Habit
from habits.serializers import HabitSerializer

User = get_user_model()


class HabitSerializerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p" * 10)
        self.factory = APIRequestFactory()
        request = self.factory.post("/api/habits/")
        request.user = self.user
        self.context = {"request": request}

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

    def test_create_valid(self):
        serializer = HabitSerializer(data=self._data(), context=self.context)
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_create_invalid_duration(self):
        serializer = HabitSerializer(
            data=self._data(duration=130), context=self.context
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("duration", serializer.errors)

    def test_create_invalid_pleasant_with_reward(self):
        serializer = HabitSerializer(
            data=self._data(is_pleasant=True, reward="Торт"),
            context=self.context,
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("reward", serializer.errors)

    def test_create_invalid_reward_and_related(self):
        pleasant = Habit.objects.create(
            user=self.user,
            place="X",
            time="12:00",
            action="Ванна",
            is_pleasant=True,
            duration=60,
        )
        serializer = HabitSerializer(
            data=self._data(reward="Торт", related_habit=pleasant.id),
            context=self.context,
        )
        self.assertFalse(serializer.is_valid())

    def test_read_only_user(self):
        serializer = HabitSerializer(context=self.context)
        self.assertTrue(serializer.fields["user"].read_only)
