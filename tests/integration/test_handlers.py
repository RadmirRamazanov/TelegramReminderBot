from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

import pytest

from bot.database.crud import create_reminder
from bot.database.models import Reminder
from bot.handlers.reminders import (
    AddReminderStates,
    cmd_add,
    cmd_list,
    process_reminder_text,
    process_reminder_time,
)


def make_mock_message(text: str = "", user_id: int = 12345, first_name: str = "Тест") -> MagicMock:
    message = MagicMock()
    message.text = text
    message.from_user = MagicMock()
    message.from_user.id = user_id
    message.from_user.first_name = first_name
    message.answer = AsyncMock()
    return message


def make_mock_state() -> MagicMock:
    state = MagicMock()
    state.set_state = AsyncMock()
    state.get_state = AsyncMock(return_value=None)
    state.update_data = AsyncMock()
    state.get_data = AsyncMock(return_value={})
    state.clear = AsyncMock()
    return state


class TestCmdAdd:
    async def test_cmd_add_переводит_в_состояние_ожидания_текста(self):
        message, state = make_mock_message(), make_mock_state()
        await cmd_add(message, state)
        state.set_state.assert_called_once_with(AddReminderStates.waiting_text)

    async def test_cmd_add_отправляет_ответ_пользователю(self):
        message, state = make_mock_message(), make_mock_state()
        await cmd_add(message, state)
        message.answer.assert_called_once()


class TestProcessReminderText:
    async def test_корректный_текст_сохраняется_в_fsm(self):
        message, state = make_mock_message(text="Позвонить другу"), make_mock_state()
        await process_reminder_text(message, state)
        state.update_data.assert_called_once_with(reminder_text="Позвонить другу")

    async def test_корректный_текст_переводит_в_следующее_состояние(self):
        message, state = make_mock_message(text="Сходить в магазин"), make_mock_state()
        await process_reminder_text(message, state)
        state.set_state.assert_called_once_with(AddReminderStates.waiting_time)

    async def test_пустой_текст_не_меняет_состояние(self):
        message, state = make_mock_message(text="   "), make_mock_state()
        await process_reminder_text(message, state)
        state.set_state.assert_not_called()
        message.answer.assert_called_once()

    async def test_слишком_длинный_текст_отклоняется(self):
        message, state = make_mock_message(text="A" * 501), make_mock_state()
        await process_reminder_text(message, state)
        state.set_state.assert_not_called()


class TestProcessReminderTime:
    async def test_корректная_дата_сохраняется(self):
        future = datetime.now() + timedelta(hours=2)
        message = make_mock_message(text=future.strftime("%d.%m.%Y %H:%M"))
        state = make_mock_state()
        state.get_data = AsyncMock(return_value={"reminder_text": "Тест"})
        await process_reminder_time(message, state)
        state.update_data.assert_called_once()
        assert "remind_at" in state.update_data.call_args[1]

    async def test_неверный_формат_даты_отклоняется(self):
        message, state = make_mock_message(text="31/12/2025 10:00"), make_mock_state()
        await process_reminder_time(message, state)
        state.set_state.assert_not_called()
        message.answer.assert_called_once()

    async def test_прошедшая_дата_отклоняется(self):
        past = datetime.now() - timedelta(hours=1)
        message, state = make_mock_message(text=past.strftime("%d.%m.%Y %H:%M")), make_mock_state()
        await process_reminder_time(message, state)
        state.set_state.assert_not_called()


class TestCmdList:
    async def test_пустой_список_для_нового_пользователя(self, db_conn):
        message = make_mock_message(user_id=777888999)
        await cmd_list(message, db=db_conn)
        message.answer.assert_called_once()
        text = message.answer.call_args[0][0]
        assert "нет" in text.lower() or "пока" in text.lower()

    async def test_список_с_напоминаниями(self, db_conn):
        user_id = 100200300
        future = datetime.now() + timedelta(hours=1)
        await create_reminder(
            db_conn,
            Reminder(id=None, user_id=user_id, text="Тестовое напоминание", remind_at=future),
        )
        message = make_mock_message(user_id=user_id)
        await cmd_list(message, db=db_conn)
        message.answer.assert_called_once()
        assert "Тестовое напоминание" in message.answer.call_args[0][0]
