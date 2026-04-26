import logging
from datetime import datetime

import aiosqlite
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from bot.database.crud import create_reminder, delete_reminder, get_reminders_by_user
from bot.database.models import Reminder
from bot.keyboards.inline import get_cancel_keyboard, get_confirm_keyboard, get_reminders_keyboard

logger = logging.getLogger(__name__)
router = Router(name="reminders")

DATE_FORMAT = "%d.%m.%Y %H:%M"


class AddReminderStates(StatesGroup):
    waiting_text = State()
    waiting_time = State()
    confirming = State()


class DeleteReminderStates(StatesGroup):
    waiting_id = State()


# --- /add ---

@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext) -> None:
    await state.set_state(AddReminderStates.waiting_text)
    logger.info("user_id=%d — /add", message.from_user.id)
    await message.answer(
        "📝 <b>Шаг 1 из 2</b>\n\nВведи текст напоминания.\n"
        "Например: <i>Позвонить врачу</i> или <i>Купить молоко</i>",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddReminderStates.waiting_text)
async def process_reminder_text(message: Message, state: FSMContext) -> None:
    text = message.text.strip() if message.text else ""

    if not text:
        await message.answer("⚠️ Текст не может быть пустым. Попробуй ещё раз.")
        return

    if len(text) > 500:
        await message.answer(f"⚠️ Текст слишком длинный ({len(text)} символов). Максимум — 500.")
        return

    await state.update_data(reminder_text=text)
    await state.set_state(AddReminderStates.waiting_time)
    await message.answer(
        "🕐 <b>Шаг 2 из 2</b>\n\nВведи дату и время в формате:\n"
        "<code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n\nНапример: <code>25.12.2024 09:30</code>",
        parse_mode="HTML",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(AddReminderStates.waiting_time)
async def process_reminder_time(message: Message, state: FSMContext) -> None:
    raw = message.text.strip() if message.text else ""

    try:
        remind_at = datetime.strptime(raw, DATE_FORMAT)
    except ValueError:
        await message.answer(
            "⚠️ Неверный формат даты.\n\n"
            "Используй формат: <code>ДД.ММ.ГГГГ ЧЧ:ММ</code>\n"
            "Например: <code>25.12.2024 09:30</code>",
            parse_mode="HTML",
        )
        return

    if remind_at <= datetime.now():
        await message.answer("⚠️ Дата уже прошла. Укажи дату в будущем.")
        return

    await state.update_data(remind_at=remind_at.isoformat())
    data = await state.get_data()
    await state.set_state(AddReminderStates.confirming)

    await message.answer(
        "✅ <b>Проверь данные напоминания:</b>\n\n"
        f"📝 Текст: <b>{data['reminder_text']}</b>\n"
        f"🕐 Время: <b>{remind_at.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
        "Всё верно?",
        parse_mode="HTML",
        reply_markup=get_confirm_keyboard(),
    )


@router.callback_query(F.data == "confirm:save", AddReminderStates.confirming)
async def confirm_save(callback: CallbackQuery, state: FSMContext, db: aiosqlite.Connection) -> None:
    data = await state.get_data()
    remind_at = datetime.fromisoformat(data["remind_at"])

    reminder = Reminder(
        id=None,
        user_id=callback.from_user.id,
        text=data["reminder_text"],
        remind_at=remind_at,
    )
    saved = await create_reminder(db, reminder)
    await state.clear()

    logger.info("Напоминание id=%d создано для user_id=%d", saved.id, callback.from_user.id)

    await callback.message.edit_text(
        f"✅ Напоминание сохранено!\n\n"
        f"📝 <b>{saved.text}</b>\n"
        f"🕐 Напомню <b>{saved.remind_at_str}</b>",
        parse_mode="HTML",
    )
    await callback.answer("Напоминание сохранено!")


@router.callback_query(F.data == "confirm:cancel")
async def confirm_cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text("❌ Создание напоминания отменено.")
    await callback.answer("Отменено")


@router.callback_query(F.data == "cancel:flow")
async def cancel_flow(callback: CallbackQuery, state: FSMContext) -> None:
    if await state.get_state() is not None:
        await state.clear()
        await callback.message.edit_text("❌ Добавление напоминания отменено.")
        await callback.answer("Отменено")
    else:
        await callback.answer("Нечего отменять.")


# --- /list ---

@router.message(Command("list"))
async def cmd_list(message: Message, db: aiosqlite.Connection) -> None:
    reminders = await get_reminders_by_user(db, message.from_user.id)

    if not reminders:
        await message.answer(
            "📋 У тебя пока нет активных напоминаний.\n\nДобавь первое с помощью /add"
        )
        return

    lines = [f"📋 <b>Твои напоминания ({len(reminders)}):</b>\n"]
    for i, r in enumerate(reminders, start=1):
        lines.append(f"{i}. [#{r.id}] {r.remind_at_str} — {r.text}")

    await message.answer(
        "\n".join(lines),
        parse_mode="HTML",
        reply_markup=get_reminders_keyboard([r.id for r in reminders]),
    )


# --- /delete ---

@router.message(Command("delete"))
async def cmd_delete(message: Message, state: FSMContext) -> None:
    await state.set_state(DeleteReminderStates.waiting_id)
    await message.answer(
        "🗑 Введи номер напоминания для удаления.\n\nПосмотреть номера — /list",
        reply_markup=get_cancel_keyboard(),
    )


@router.message(DeleteReminderStates.waiting_id)
async def process_delete_id(message: Message, state: FSMContext, db: aiosqlite.Connection) -> None:
    raw = message.text.strip() if message.text else ""

    if not raw.isdigit():
        await message.answer("⚠️ Введи числовой номер напоминания.")
        return

    reminder_id = int(raw)
    deleted = await delete_reminder(db, reminder_id, message.from_user.id)
    await state.clear()

    if deleted:
        await message.answer(f"✅ Напоминание #{reminder_id} удалено.")
    else:
        await message.answer(f"⚠️ Напоминание #{reminder_id} не найдено.\nПроверь номер командой /list")


@router.callback_query(F.data.startswith("delete:"))
async def callback_delete(callback: CallbackQuery, db: aiosqlite.Connection) -> None:
    reminder_id = int(callback.data.split(":")[1])
    deleted = await delete_reminder(db, reminder_id, callback.from_user.id)

    if deleted:
        await callback.answer(f"Напоминание #{reminder_id} удалено ✅")
        await callback.message.edit_text(
            callback.message.text + f"\n\n✅ Напоминание #{reminder_id} удалено.",
            parse_mode="HTML",
            reply_markup=None,
        )
    else:
        await callback.answer("Напоминание не найдено ⚠️", show_alert=True)
