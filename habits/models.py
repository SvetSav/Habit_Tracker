from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .validators import validate_duration, validate_periodicity


class Habit(models.Model):
    """Привычка пользователя."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Пользователь",
    )
    place = models.CharField(max_length=255, verbose_name="Место")
    time = models.TimeField(verbose_name="Время выполнения")
    action = models.CharField(max_length=255, verbose_name="Действие")
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_to",
        verbose_name="Связанная привычка",
    )
    periodicity = models.PositiveSmallIntegerField(
        default=1,
        validators=[validate_periodicity],
        verbose_name="Периодичность (дни)",
    )
    reward = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Вознаграждение",
    )
    duration = models.PositiveSmallIntegerField(
        validators=[validate_duration],
        verbose_name="Время на выполнение (сек)",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
    )
    last_notification_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата последнего уведомления",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"

    def __str__(self) -> str:
        return f'Я буду {self.action} в {self.time.strftime("%H:%M")} в {self.place}'

    def clean(self):
        """Кросс-полевая валидация.

        1. У приятной привычки не может быть вознаграждения.
        2. У приятной привычки не может быть связанной привычки.
        3. У полезной привычки не может быть одновременно вознаграждения
           и связанной привычки.
        4. Связанная привычка полезной привычки должна быть приятной.
        """
        # --- Правила для приятной привычки ---
        if self.is_pleasant:
            if self.reward:
                raise ValidationError(
                    {"reward": "У приятной привычки не может быть вознаграждения."}
                )
            if self.related_habit:
                raise ValidationError(
                    {
                        "related_habit": "У приятной привычки не может быть связанной привычки."
                    }
                )
            return  # для приятной больше проверок нет

        # --- Правила для полезной привычки ---
        if self.reward and self.related_habit:
            raise ValidationError(
                "Нельзя одновременно указать вознаграждение и связанную привычку."
            )
        if self.related_habit and not self.related_habit.is_pleasant:
            raise ValidationError(
                {
                    "related_habit": "В связанные привычки могут попадать только приятные привычки."
                }
            )
