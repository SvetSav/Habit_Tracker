from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомный пользователь с привязкой к Telegram-чату."""

    telegram_chat_id = models.CharField(
        max_length=64,
        blank=True,
        null=True,
        verbose_name="ID чата в Telegram",
        help_text="Числовой id чата, куда бот будет присылать напоминания",
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.username
