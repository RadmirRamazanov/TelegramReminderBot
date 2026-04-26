import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import get_settings
from bot.database.db import init_db
from bot.handlers import help, reminders, start
from bot.middlewares.db_middleware import DatabaseMiddleware
from bot.scheduler.jobs import create_scheduler


def setup_logging(log_level: int) -> None:
    logging.basicConfig(
        stream=sys.stdout,
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level_int)

    logger = logging.getLogger(__name__)
    logger.info("Запуск бота")

    await init_db(settings.database_path)

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    # MemoryStorage сбрасывает FSM-состояния при перезапуске.
    # Для продакшна замените на RedisStorage.
    dp = Dispatcher(storage=MemoryStorage())

    dp.update.middleware(DatabaseMiddleware(db_path=settings.database_path))
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(reminders.router)

    scheduler = create_scheduler(
        bot=bot,
        db_path=settings.database_path,
        interval_seconds=settings.scheduler_interval,
    )
    scheduler.start()

    logger.info("Бот запущен")
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        scheduler.shutdown()
        await bot.session.close()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    asyncio.run(main())
