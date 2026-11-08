# Habit Tracker — бэкенд SPA-приложения «Атомные привычки»

## Возможности
- JWT-аутентификация (регистрация, авторизация)
- CRUD привычек с проверкой прав (только свои)
- Просмотр публичных привычек (только чтение)
- Пагинация `limit/offset/count/results` (по 5 записей)
- Валидаторы согласно ТЗ
- Celery-задача: отправка напоминаний в Telegram по расписанию
- Документация OpenAPI/Swagger по `/api/docs/`
- CORS

## Запуск через Docker
```
cp .env.template .env
``` 
### отредактируйте .env, задайте SECRET_KEY и TELEGRAM_BOT_TOKEN
```
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```
## Запуск локально (SQLite)
```
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.template .env
```
### в .env замените DB_* на sqlite параметры или настройте PostgreSQL
```
python manage.py migrate
python manage.py runserver
```
## Celery
```
celery -A config worker -l info
celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
## Telegram-бот
Создайте бота через @BotFather, получите токен.
Впишите токен в TELEGRAM_BOT_TOKEN.
Запустите бота: python manage.py run_telegram_bot.
В Telegram отправьте боту /start — он покажет chat_id.
Отправьте POST /api/users/link-telegram/ с {"chat_id": "..."} (требуется авторизация).

### Документация
Swagger UI: http://localhost:8000/api/docs/

Redoc: http://localhost:8000/api/redoc/

### Тесты и покрытие
```
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📄 Пакет `config/`

### `config/__init__.py`
```
from .celery import app as celery_app

__all__ = ('celery_app',)
```

## Cloudflare Worker для обхода блокировки Telegram

Код Worker'а лежит в `deploy/cloudflare-worker/worker.js`.
Разверните его на Cloudflare (Compute → Workers → Create → Edit code → вставить → Deploy).
Затем запустите `tgwsapiproxy --worker-host <ваш-домен>.workers.dev`.