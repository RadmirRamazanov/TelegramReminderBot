import logging
from pathlib import Path

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.database.crud import get_pending_reminders, mark_reminder_sent
from bot.database.db import get_connection

logger = logging.getLogger(__name__)

REMINDER_MESSAGE = "🔔 <b>Напоминание!</b>\n\n{text}"


async def check_and_send_reminders(bot: Bot, db_path: Path) -> None:
    """Выбирает просроченные напоминания из БД и отправляет их пользователям."""
    try:
        async with await get_connection(db_path) as conn:
            reminders = await get_pending_reminders(conn)
            for reminder in reminders:
                try:
                    await bot.send_message(
                        chat_id=reminder.user_id,
                        text=REMINDER_MESSAGE.format(text=reminder.text),
                        parse_mode="HTML",
                    )
                    await mark_reminder_sent(conn, reminder.id)
                    logger.info("Напоминание id=%d отправлено user_id=%d", reminder.id, reminder.user_id)
                except Exception as e:
                    logger.error("Ошибка отправки напоминания id=%d: %s", reminder.id, e)
    except Exception as e:
        logger.error("Ошибка планировщика: %s", e)


def create_scheduler(bot: Bot, db_path: Path, interval_seconds: int) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        func=check_and_send_reminders,
        trigger="interval",
        seconds=interval_seconds,
        kwargs={"bot": bot, "db_path": db_path},
        id="check_reminders",
        max_instances=1,
        misfire_grace_time=30,
    )
    logger.info("Планировщик: проверка каждые %d сек.", interval_seconds)
    return scheduler
