import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

logger = logging.getLogger(__name__)
router = Router(name="start")

WELCOME_MESSAGE = """
👋 Привет, {name}!

Я <b>Бот-напоминалка</b> — помогу тебе не забыть о важных делах.

<b>Что я умею:</b>
📝 /add — добавить новое напоминание
📋 /list — список всех активных напоминаний
🗑 /delete — удалить напоминание
❓ /help — подробная справка

Начнём? Отправь /add чтобы создать первое напоминание!
"""


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_name = message.from_user.first_name if message.from_user else "друг"
    logger.info("user_id=%d — /start", message.from_user.id if message.from_user else 0)
    await message.answer(WELCOME_MESSAGE.format(name=user_name), parse_mode="HTML")
