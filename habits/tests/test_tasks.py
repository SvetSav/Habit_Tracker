from datetime import date
from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from habits.models import Habit
from habits.tasks import send_reminders

User = get_user_model()


class SendRemindersTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="tg", password="p" * 10, telegram_chat_id="12345"
        )

    def _create_habit(self, **kwargs):
        defaults = dict(
            user=self.user,
            place="Дом",
            time=timezone.localtime().time().replace(second=0, microsecond=0),
            action="Зарядка",
            duration=60,
            periodicity=1,
        )
        defaults.update(kwargs)
        return Habit.objects.create(**defaults)

    @patch("habits.tasks.requests.post")
    def test_sends_message(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        self._create_habit()
        send_reminders()
        mock_post.assert_called_once()
        habit = Habit.objects.first()
        self.assertEqual(habit.last_notification_date, timezone.localtime().date())

    @patch("habits.tasks.requests.post")
    def test_skips_same_day(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        self._create_habit(last_notification_date=timezone.localtime().date())
        send_reminders()
        mock_post.assert_not_called()

    @patch("habits.tasks.requests.post")
    def test_skips_without_chat_id(self, mock_post):
        self.user.telegram_chat_id = ""
        self.user.save()
        self._create_habit()
        send_reminders()
        mock_post.assert_not_called()

    @patch("habits.tasks.requests.post")
    def test_skips_when_periodicity_not_due(self, mock_post):
        mock_post.return_value = MagicMock(status_code=200)
        # Прошло 1 день, периодичность 7 дней — не отправляем
        self._create_habit(
            periodicity=7,
            last_notification_date=date.fromordinal(
                timezone.localtime().date().toordinal() - 1
            ),
        )
        send_reminders()
        mock_post.assert_not_called()

    @patch("habits.tasks.requests.post")
    def test_handles_network_error(self, mock_post):
        import requests as rq

        mock_post.side_effect = rq.RequestException("boom")
        self._create_habit()
        # Не должно падать
        send_reminders()

    @patch("habits.tasks.settings")
    def test_no_token(self, mock_settings):
        mock_settings.TELEGRAM_BOT_TOKEN = ""
        send_reminders()  # просто не должно упасть
