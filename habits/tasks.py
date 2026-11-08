import logging
import os

import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone

from .models import Habit

logger = logging.getLogger(__name__)


@shared_task(name="habits.tasks.send_reminders")
def send_reminders():
    """Отправить напоминания по привычкам, время которых наступило.

    Запускается раз в минуту через Celery Beat. Для каждой привычки:
    - проверяем, что у пользователя указан telegram_chat_id;
    - что время привычки (hour:minute) совпадает с текущим;
    - что с момента последнего уведомления прошло не меньше `periodicity` дней.
    """
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN не задан — уведомления не отправляются.")
        return

    # Прокси, через который пойдёт запрос (тот же, что у бота).
    # tgwsapiproxy должен быть запущен на 127.0.0.1:8080.
    proxy_url = os.getenv("TELEGRAM_PROXY_URL", "").strip()
    proxies = {"https": proxy_url, "http": proxy_url} if proxy_url else None
    if proxies:
        logger.info("send_reminders: использую прокси %s", proxy_url)
    else:
        logger.warning(
            "send_reminders: TELEGRAM_PROXY_URL не задан, "
            "запросы пойдут напрямую в Telegram"
        )

    now = timezone.localtime()
    today = now.date()
    current_hour = now.hour
    current_minute = now.minute

    habits = (
        Habit.objects.filter(
            time__hour=current_hour,
            time__minute=current_minute,
            user__telegram_chat_id__isnull=False,
        )
        .exclude(user__telegram_chat_id="")
        .select_related("user")
    )

    for habit in habits:
        if habit.last_notification_date is not None:
            days_since = (today - habit.last_notification_date).days
            if days_since < habit.periodicity:
                continue

        text = (
            f"🔔 Напоминание: {habit.action} "
            f'в {habit.time.strftime("%H:%M")} в {habit.place}'
        )
        url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
        try:
            response = requests.post(
                url,
                json={"chat_id": habit.user.telegram_chat_id, "text": text},
                proxies=proxies,  # ← КЛЮЧЕВАЯ СТРОКА
                timeout=15,
            )
            if response.status_code == 200:
                habit.last_notification_date = today
                habit.save(update_fields=["last_notification_date"])
            else:
                logger.error(
                    "Telegram API вернул %s для привычки %s: %s",
                    response.status_code,
                    habit.id,
                    response.text,
                )
        except requests.RequestException as exc:
            logger.exception(
                "Ошибка при отправке уведомления habit=%s: %s", habit.id, exc
            )
