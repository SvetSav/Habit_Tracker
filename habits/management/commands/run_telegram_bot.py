"""Запуск Telegram-бота: показывает chat_id по команде /start.

Работает через локальный HTTP-прокси (tgwsapiproxy на порту 8080),
который перенаправляет трафик к api.telegram.org через Cloudflare Worker.
Адрес прокси берётся из переменной окружения TELEGRAM_PROXY_URL.
"""

import os

from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отвечает на /start и присылает пользователю его chat_id."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"Ваш chat_id: {chat_id}\n\n"
        f"Скопируйте его и сохраните в приложении "
        f"(POST /api/auth/link-telegram/)."
    )


class Command(BaseCommand):
    help = "Запуск Telegram-бота (polling) через локальный прокси"

    def handle(self, *args, **options):
        # 1. Токен бота
        if not settings.TELEGRAM_BOT_TOKEN:
            self.stderr.write(self.style.ERROR("TELEGRAM_BOT_TOKEN не задан в .env"))
            return

        # 2. Прокси (единый HTTP-адрес для всех запросов)
        proxy_url = os.getenv("TELEGRAM_PROXY_URL", "").strip()
        if not proxy_url:
            self.stderr.write(
                self.style.ERROR(
                    "TELEGRAM_PROXY_URL не задан в .env. "
                    "Укажите, например, http://127.0.0.1:8080"
                )
            )
            return

        self.stdout.write(self.style.WARNING(f"Использую HTTP-прокси: {proxy_url}"))

        # 3. Один HTTPXRequest для бота и для получения обновлений.
        #    Увеличенные таймауты важны для нестабильных соединений через прокси.
        request = HTTPXRequest(
            proxy=proxy_url,
            connect_timeout=15.0,
            read_timeout=15.0,
            write_timeout=15.0,
            pool_timeout=15.0,
        )

        # 4. Собираем приложение — один и тот же request и для bot, и для updater
        application = (
            ApplicationBuilder()
            .token(settings.TELEGRAM_BOT_TOKEN)
            .request(request)  # для исходящих запросов бота (sendMessage, getMe и т.д.)
            .get_updates_request(request)  # для получения обновлений (getUpdates)
            .build()
        )

        # 5. Обработчики
        application.add_handler(CommandHandler("start", start_command))

        # 6. Запуск
        self.stdout.write(self.style.SUCCESS("Бот запущен. Ctrl+C — остановка."))
        application.run_polling(
            drop_pending_updates=True,
            allowed_updates=Update.ALL_TYPES,
        )
