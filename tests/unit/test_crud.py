from datetime import datetime, timedelta

import pytest

from bot.database.crud import (
    create_reminder,
    delete_reminder,
    get_pending_reminders,
    get_reminder_by_id,
    get_reminders_by_user,
    mark_reminder_sent,
)
from bot.database.models import Reminder


class TestCreateReminder:
    async def test_создание_напоминания_присваивает_id(self, db_conn, sample_reminder):
        saved = await create_reminder(db_conn, sample_reminder)
        assert saved.id is not None and saved.id > 0

    async def test_создание_напоминания_сохраняет_данные(self, db_conn, sample_reminder):
        saved = await create_reminder(db_conn, sample_reminder)
        assert saved.user_id == sample_reminder.user_id
        assert saved.text == sample_reminder.text
        assert saved.remind_at.replace(microsecond=0) == sample_reminder.remind_at.replace(microsecond=0)

    async def test_создание_двух_напоминаний_разные_id(self, db_conn, future_datetime):
        r1 = Reminder(id=None, user_id=100, text="Первое", remind_at=future_datetime)
        r2 = Reminder(id=None, user_id=100, text="Второе", remind_at=future_datetime)
        s1 = await create_reminder(db_conn, r1)
        s2 = await create_reminder(db_conn, r2)
        assert s1.id != s2.id


class TestGetRemindersByUser:
    async def test_пустой_список_для_нового_пользователя(self, db_conn):
        assert await get_reminders_by_user(db_conn, user_id=999999) == []

    async def test_возвращает_напоминания_только_своего_пользователя(self, db_conn, future_datetime):
        await create_reminder(db_conn, Reminder(id=None, user_id=111, text="111", remind_at=future_datetime))
        await create_reminder(db_conn, Reminder(id=None, user_id=222, text="222", remind_at=future_datetime))

        result = await get_reminders_by_user(db_conn, user_id=111)
        assert len(result) == 1 and result[0].user_id == 111

    async def test_не_возвращает_отправленные_по_умолчанию(self, db_conn, future_datetime):
        saved = await create_reminder(db_conn, Reminder(id=None, user_id=100, text="sent", remind_at=future_datetime))
        await mark_reminder_sent(db_conn, saved.id)
        assert await get_reminders_by_user(db_conn, user_id=100) == []

    async def test_возвращает_отправленные_с_флагом(self, db_conn, future_datetime):
        saved = await create_reminder(db_conn, Reminder(id=None, user_id=100, text="sent", remind_at=future_datetime))
        await mark_reminder_sent(db_conn, saved.id)
        assert len(await get_reminders_by_user(db_conn, user_id=100, include_sent=True)) == 1

    async def test_сортировка_по_времени(self, db_conn):
        base = datetime.now() + timedelta(hours=1)
        await create_reminder(db_conn, Reminder(id=None, user_id=100, text="Позже", remind_at=base + timedelta(hours=2)))
        await create_reminder(db_conn, Reminder(id=None, user_id=100, text="Раньше", remind_at=base))
        result = await get_reminders_by_user(db_conn, user_id=100)
        assert result[0].text == "Раньше"


class TestGetReminderById:
    async def test_возвращает_своё_напоминание(self, db_conn, sample_reminder):
        saved = await create_reminder(db_conn, sample_reminder)
        found = await get_reminder_by_id(db_conn, saved.id, sample_reminder.user_id)
        assert found is not None and found.id == saved.id

    async def test_возвращает_none_для_чужого_user_id(self, db_conn, sample_reminder):
        saved = await create_reminder(db_conn, sample_reminder)
        assert await get_reminder_by_id(db_conn, saved.id, user_id=99999) is None

    async def test_возвращает_none_для_несуществующего_id(self, db_conn, sample_reminder):
        assert await get_reminder_by_id(db_conn, reminder_id=99999, user_id=sample_reminder.user_id) is None


class TestDeleteReminder:
    async def test_удаление_своего_напоминания(self, db_conn, sample_reminder):
        saved = await create_reminder(db_conn, sample_reminder)
        assert await delete_reminder(db_conn, saved.id, sample_reminder.user_id) is True
        assert await get_reminder_by_id(db_conn, saved.id, sample_reminder.user_id) is None

    async def test_нельзя_удалить_чужое_напоминание(self, db_conn, sample_reminder):
        saved = await create_reminder(db_conn, sample_reminder)
        assert await delete_reminder(db_conn, saved.id, user_id=99999) is False

    async def test_удаление_несуществующего_возвращает_false(self, db_conn, sample_reminder):
        assert await delete_reminder(db_conn, reminder_id=99999, user_id=sample_reminder.user_id) is False


class TestGetPendingReminders:
    async def test_возвращает_просроченные(self, db_conn, past_reminder):
        await create_reminder(db_conn, past_reminder)
        pending = await get_pending_reminders(db_conn)
        assert len(pending) >= 1

    async def test_не_возвращает_будущие(self, db_conn, sample_reminder):
        await create_reminder(db_conn, sample_reminder)
        pending = await get_pending_reminders(db_conn)
        assert all(r.text != "Тестовое напоминание" for r in pending)


class TestMarkReminderSent:
    async def test_помечает_как_отправленное(self, db_conn, sample_reminder):
        saved = await create_reminder(db_conn, sample_reminder)
        await mark_reminder_sent(db_conn, saved.id)
        all_reminders = await get_reminders_by_user(db_conn, user_id=sample_reminder.user_id, include_sent=True)
        sent = next((r for r in all_reminders if r.id == saved.id), None)
        assert sent is not None and sent.is_sent is True
