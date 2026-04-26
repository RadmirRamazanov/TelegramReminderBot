import logging
from pathlib import Path

import aiosqlite

logger = logging.getLogger(__name__)

CREATE_REMINDERS_TABLE = """
CREATE TABLE IF NOT EXISTS reminders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    text        TEXT    NOT NULL,
    remind_at   TEXT    NOT NULL,
    is_sent     INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
    CONSTRAINT user_id_check CHECK (user_id > 0)
);
"""

CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_reminders_user_id ON reminders(user_id);
"""

CREATE_INDEX_REMIND_AT = """
CREATE INDEX IF NOT EXISTS idx_reminders_remind_at ON reminders(remind_at, is_sent);
"""


async def init_db(db_path: Path) -> None:
    """Создаёт таблицы и индексы при первом запуске."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Инициализация базы данных: %s", db_path)

    async with aiosqlite.connect(db_path) as conn:
        await conn.execute("PRAGMA foreign_keys = ON")
        await conn.execute(CREATE_REMINDERS_TABLE)
        await conn.execute(CREATE_INDEX)
        await conn.execute(CREATE_INDEX_REMIND_AT)
        await conn.commit()

    logger.info("База данных готова")


async def get_connection(db_path: Path) -> aiosqlite.Connection:
    conn = await aiosqlite.connect(db_path)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA foreign_keys = ON")
    return conn
