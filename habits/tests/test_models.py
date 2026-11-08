from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from habits.models import Habit

User = get_user_model()


class HabitModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="p" * 10)

    def _create(self, **kwargs):
        defaults = dict(
            user=self.user,
            place="Дом",
            time="12:00",
            action="Зарядка",
            duration=60,
            periodicity=1,
        )
        defaults.update(kwargs)
        return Habit(**defaults)

    def test_valid_habit(self):
        habit = self._create()
        habit.full_clean()
        habit.save()
        self.assertEqual(str(habit), "Я буду Зарядка в 12:00 в Дом")

    def test_duration_too_long(self):
        habit = self._create(duration=121)
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_periodicity_invalid(self):
        habit = self._create(periodicity=8)
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_pleasant_with_reward(self):
        habit = self._create(is_pleasant=True, reward="Торт")
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_pleasant_with_related(self):
        pleasant = self._create(is_pleasant=True, action="Ванна")
        pleasant.save()
        habit = self._create(is_pleasant=True, related_habit=pleasant)
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_reward_and_related_together(self):
        pleasant = self._create(is_pleasant=True, action="Ванна")
        pleasant.save()
        habit = self._create(reward="Торт", related_habit=pleasant)
        with self.assertRaises(ValidationError):
            habit.full_clean()

    def test_related_not_pleasant(self):
        plain = self._create(action="Простое")
        plain.save()
        habit = self._create(related_habit=plain)
        with self.assertRaises(ValidationError):
            habit.full_clean()
