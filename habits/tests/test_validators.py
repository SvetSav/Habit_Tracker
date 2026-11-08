from unittest.mock import MagicMock

from django.core.exceptions import ValidationError
from django.test import SimpleTestCase

from habits.validators import (
    validate_duration,
    validate_periodicity,
    validate_related_habit,
)


class ValidatorTests(SimpleTestCase):
    def test_related_habit_not_pleasant(self):
        habit = MagicMock(is_pleasant=False)
        with self.assertRaises(ValidationError):
            validate_related_habit(habit)

    def test_related_habit_is_pleasant(self):
        habit = MagicMock(is_pleasant=True)
        validate_related_habit(habit)  # не должно бросить
        validate_related_habit(None)

    def test_duration_ok(self):
        validate_duration(120)
        validate_duration(1)
        validate_duration(None)

    def test_duration_too_big(self):
        with self.assertRaises(ValidationError):
            validate_duration(121)

    def test_periodicity_ok(self):
        for v in (1, 5, 7):
            validate_periodicity(v)

    def test_periodicity_invalid(self):
        with self.assertRaises(ValidationError):
            validate_periodicity(0)
        with self.assertRaises(ValidationError):
            validate_periodicity(8)
