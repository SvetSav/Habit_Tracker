from django.core.exceptions import ValidationError


def validate_related_habit(value):
    """Связанная привычка должна быть приятной."""
    if value is not None and not value.is_pleasant:
        raise ValidationError(
            "В связанные привычки могут попадать только приятные привычки."
        )


def validate_duration(value):
    """Время выполнения — не более 120 секунд."""
    if value is not None and value > 120:
        raise ValidationError(
            "Время выполнения привычки не должно превышать 120 секунд."
        )


def validate_periodicity(value):
    """Периодичность от 1 до 7 дней."""
    if value is not None and (value < 1 or value > 7):
        raise ValidationError("Периодичность должна быть от 1 до 7 дней.")
