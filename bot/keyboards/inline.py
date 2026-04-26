from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Сохранить", callback_data="confirm:save"))
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="confirm:cancel"))
    builder.adjust(2)
    return builder.as_markup()


def get_reminders_keyboard(reminder_ids: list[int]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for rid in reminder_ids:
        builder.add(
            InlineKeyboardButton(text=f"🗑 Удалить #{rid}", callback_data=f"delete:{rid}")
        )
    builder.adjust(1)
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel:flow"))
    return builder.as_markup()
