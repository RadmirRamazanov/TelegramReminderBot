import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

logger = logging.getLogger(__name__)
router = Router(name="help")

HELP_TEXT = """
❓ <b>Справка по Боту-напоминалке</b>

<b>Команды:</b>
/start — запустить или перезапустить бота
/add — создать новое напоминание (пошаговый диалог)
/list — показать все активные напоминания
/delete — удалить напоминание по номеру
/help — эта справка

<b>Как создать напоминание:</b>
1. Отправь <code>/add</code>
2. Введи текст напоминания (например: «Позвонить врачу»)
3. Введи дату и время в формате:
   <code>ДД.ММ.ГГГГ ЧЧ:ММ</code>
   Пример: <code>25.12.2024 09:30</code>
4. Подтверди сохранение

<b>Как удалить напоминание:</b>
• Отправь <code>/list</code> — увидишь кнопки «Удалить» под каждым напоминанием
• Или отправь <code>/delete</code> и введи номер напоминания

<b>Важно:</b>
• Напоминания приходят в этот чат в указанное время
• Проверка выполняется каждую минуту
• После отправки напоминание исчезает из списка

<b>Примеры дат:</b>
<code>01.01.2025 00:00</code> — 1 января 2025 в полночь
<code>15.06.2025 14:30</code> — 15 июня 2025 в 14:30
"""


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    logger.info("user_id=%d — /help", message.from_user.id if message.from_user else 0)
    await message.answer(HELP_TEXT, parse_mode="HTML")
