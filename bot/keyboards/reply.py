"""Reply klaviaturalar — usta tiliga mos tugmalar."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

from bot.utils.i18n import btn, t

# Admin panel tugmasi ikkala tilda bir xil
BTN_ADMIN = "⚙️ Admin panel"


def master_menu(lang: str = "uz", is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [
            KeyboardButton(text=btn("new_order", lang)),
            KeyboardButton(text=btn("complete", lang)),
        ],
        [
            KeyboardButton(text=btn("pending", lang)),
            KeyboardButton(text=btn("ready_list", lang)),
        ],
        [
            KeyboardButton(text=btn("search", lang)),
            KeyboardButton(text=btn("my_income", lang)),
        ],
        [KeyboardButton(text=btn("profile", lang))],
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text=BTN_ADMIN)])
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder=t("menu_placeholder", lang),
    )


def cancel_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=btn("cancel", lang))]],
        resize_keyboard=True,
    )
