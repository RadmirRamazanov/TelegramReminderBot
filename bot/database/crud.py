import logging
from datetime import datetime, timezone

import aiosqlite

from bot.database.models import Reminder

logger = logging.getLogger(__name__)


async def create_reminder(conn: aiosqlite.Connection, reminder: Reminder) -> Reminder:
    remind_at_str = reminder.remind_at.strftime("%Y-%m-%d %H:%M:%S")
    cursor = await conn.execute(
        "INSERT INTO reminders (user_id, text, remind_at, is_sent) VALUES (?, ?, ?, 0)",
        (reminder.user_id, reminder.text, remind_at_str),
    )
    await conn.commit()
    reminder.id = cursor.lastrowid
    logger.debug("Создано напоминание id=%d для user_id=%d", reminder.id, reminder.user_id)
    return reminder


async def get_reminders_by_user(
    conn: aiosqlite.Connection,
    user_id: int,
    include_sent: bool = False,
) -> list[Reminder]:
    query = "SELECT id, user_id, text, remind_at, is_sent, created_at FROM reminders WHERE user_id = ?"
    params: list = [user_id]

    if not include_sent:
        query += " AND is_sent = 0"
    query += " ORDER BY remind_at ASC"

    async with conn.execute(query, params) as cursor:
        rows = await cursor.fetchall()

    return [Reminder.from_row(dict(row)) for row in rows]


async def get_reminder_by_id(
    conn: aiosqlite.Connection,
    reminder_id: int,
    user_id: int,
) -> Reminder | None:
    async with conn.execute(
        "SELECT id, user_id, text, remind_at, is_sent, created_at FROM reminders WHERE id = ? AND user_id = ?",
        (reminder_id, user_id),
    ) as cursor:
        row = await cursor.fetchone()

    return Reminder.from_row(dict(row)) if row else None


async def delete_reminder(
    conn: aiosqlite.Connection,
    reminder_id: int,
    user_id: int,
) -> bool:
    cursor = await conn.execute(
        "DELETE FROM reminders WHERE id = ? AND user_id = ?",
        (reminder_id, user_id),
    )
    await conn.commit()
    return cursor.rowcount > 0


async def get_pending_reminders(conn: aiosqlite.Connection) -> list[Reminder]:
    """Возвращает напоминания с истёкшим временем, которые ещё не отправлены."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    async with conn.execute(
        "SELECT id, user_id, text, remind_at, is_sent, created_at FROM reminders "
        "WHERE is_sent = 0 AND remind_at <= ? ORDER BY remind_at ASC",
        (now_str,),
    ) as cursor:
        rows = await cursor.fetchall()

    reminders = [Reminder.from_row(dict(row)) for row in rows]
    if reminders:
        logger.info("Найдено %d напоминаний для отправки", len(reminders))
    return reminders


async def mark_reminder_sent(conn: aiosqlite.Connection, reminder_id: int) -> None:
    await conn.execute("UPDATE reminders SET is_sent = 1 WHERE id = ?", (reminder_id,))
    await conn.commit()
