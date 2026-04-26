from aiogram.types import InlineKeyboardMarkup

from bot.keyboards.inline import get_cancel_keyboard, get_confirm_keyboard, get_reminders_keyboard


def _buttons(keyboard: InlineKeyboardMarkup) -> list:
    return [btn for row in keyboard.inline_keyboard for btn in row]


class TestConfirmKeyboard:
    def test_возвращает_inline_клавиатуру(self):
        assert isinstance(get_confirm_keyboard(), InlineKeyboardMarkup)

    def test_содержит_две_кнопки(self):
        assert len(_buttons(get_confirm_keyboard())) == 2

    def test_callback_data_кнопки_сохранить(self):
        btns = _buttons(get_confirm_keyboard())
        assert any(b.callback_data == "confirm:save" for b in btns)

    def test_callback_data_кнопки_отмена(self):
        btns = _buttons(get_confirm_keyboard())
        assert any(b.callback_data == "confirm:cancel" for b in btns)


class TestRemindersKeyboard:
    def test_пустой_список_даёт_пустую_клавиатуру(self):
        assert len(_buttons(get_reminders_keyboard([]))) == 0

    def test_количество_кнопок_равно_количеству_id(self):
        assert len(_buttons(get_reminders_keyboard([1, 2, 3, 4, 5]))) == 5

    def test_callback_data_содержит_id(self):
        callbacks = [b.callback_data for b in _buttons(get_reminders_keyboard([10, 20, 30]))]
        for rid in [10, 20, 30]:
            assert f"delete:{rid}" in callbacks

    def test_одна_кнопка_в_строке(self):
        keyboard = get_reminders_keyboard([1, 2, 3])
        assert len(keyboard.inline_keyboard) == 3


class TestCancelKeyboard:
    def test_возвращает_inline_клавиатуру(self):
        assert isinstance(get_cancel_keyboard(), InlineKeyboardMarkup)

    def test_содержит_одну_кнопку(self):
        assert len(_buttons(get_cancel_keyboard())) == 1

    def test_callback_data_кнопки_отмена(self):
        assert _buttons(get_cancel_keyboard())[0].callback_data == "cancel:flow"
