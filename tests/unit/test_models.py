from datetime import datetime

import pytest

from bot.database.models import Reminder


class TestReminderCreation:
    def test_создание_корректного_напоминания(self):
        remind_at = datetime(2025, 12, 25, 9, 30)
        reminder = Reminder(id=None, user_id=123456, text="Позвонить маме", remind_at=remind_at)

        assert reminder.id is None
        assert reminder.user_id == 123456
        assert reminder.text == "Позвонить маме"
        assert reminder.remind_at == remind_at
        assert reminder.is_sent is False

    def test_напоминание_с_id(self):
        reminder = Reminder(id=42, user_id=100, text="Тест", remind_at=datetime(2025, 1, 1, 10, 0))
        assert reminder.id == 42

    def test_напоминание_помечено_отправленным(self):
        reminder = Reminder(id=1, user_id=100, text="Тест", remind_at=datetime(2025, 1, 1), is_sent=True)
        assert reminder.is_sent is True


class TestReminderValidation:
    def test_пустой_текст_вызывает_ошибку(self):
        with pytest.raises(ValueError, match="Текст напоминания не может быть пустым"):
            Reminder(id=None, user_id=100, text="", remind_at=datetime(2025, 1, 1))

    def test_текст_из_пробелов_вызывает_ошибку(self):
        with pytest.raises(ValueError):
            Reminder(id=None, user_id=100, text="   ", remind_at=datetime(2025, 1, 1))

    def test_отрицательный_user_id_вызывает_ошибку(self):
        with pytest.raises(ValueError, match="user_id должен быть положительным"):
            Reminder(id=None, user_id=-1, text="Тест", remind_at=datetime(2025, 1, 1))

    def test_нулевой_user_id_вызывает_ошибку(self):
        with pytest.raises(ValueError):
            Reminder(id=None, user_id=0, text="Тест", remind_at=datetime(2025, 1, 1))


class TestReminderProperties:
    def test_remind_at_str_формат(self):
        reminder = Reminder(id=1, user_id=100, text="Тест", remind_at=datetime(2025, 6, 15, 14, 30))
        assert reminder.remind_at_str == "15.06.2025 14:30"

    def test_from_row_создаёт_объект(self):
        row = {
            "id": 7,
            "user_id": 999,
            "text": "Купить хлеб",
            "remind_at": "2025-12-31 23:59:00",
            "is_sent": 0,
            "created_at": "2025-01-01 00:00:00",
        }
        reminder = Reminder.from_row(row)

        assert reminder.id == 7
        assert reminder.user_id == 999
        assert reminder.text == "Купить хлеб"
        assert reminder.remind_at == datetime(2025, 12, 31, 23, 59)
        assert reminder.is_sent is False

    def test_from_row_is_sent_true(self):
        row = {
            "id": 1,
            "user_id": 100,
            "text": "Тест",
            "remind_at": "2025-01-01 10:00:00",
            "is_sent": 1,
            "created_at": "2025-01-01 00:00:00",
        }
        reminder = Reminder.from_row(row)
        assert reminder.is_sent is True
