import asyncio
from datetime import datetime, timedelta
from pathlib import Path

import aiosqlite
import pytest
import pytest_asyncio

from bot.database.db import init_db
from bot.database.models import Reminder


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db_path(tmp_path: Path) -> Path:
    path = tmp_path / "test_reminders.db"
    await init_db(path)
    return path


@pytest_asyncio.fixture
async def db_conn(db_path: Path) -> aiosqlite.Connection:
    async with aiosqlite.connect(db_path) as conn:
        conn.row_factory = aiosqlite.Row
        yield conn


@pytest.fixture
def future_datetime() -> datetime:
    return datetime.now() + timedelta(hours=1)


@pytest.fixture
def past_datetime() -> datetime:
    return datetime.now() - timedelta(hours=1)


@pytest.fixture
def sample_reminder(future_datetime: datetime) -> Reminder:
    return Reminder(id=None, user_id=123456789, text="Тестовое напоминание", remind_at=future_datetime)


@pytest.fixture
def past_reminder(past_datetime: datetime) -> Reminder:
    return Reminder(id=None, user_id=123456789, text="Просроченное напоминание", remind_at=past_datetime)
