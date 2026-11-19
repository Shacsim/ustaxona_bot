"""Reply klaviaturalar — usta tiliga mos tugmalar."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, WebAppInfo

from bot.utils.i18n import btn, t
from config import settings

# Admin panel tugmasi barcha tillarda bir xil
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
            KeyboardButton(text=btn("inventory", lang)),
            KeyboardButton(text=btn("my_income", lang)),
        ],
        [
            KeyboardButton(text=btn("search", lang)),
            KeyboardButton(text=btn("profile", lang)),
        ],
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


def phone_kb(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Telefon so'rash: Mini App (sonli klaviatura) + bekor qilish."""
    rows: list[list[KeyboardButton]] = []
    if settings.phone_webapp_url:
        rows.append(
            [
                KeyboardButton(
                    text=btn("dial_phone", lang),
                    web_app=WebAppInfo(url=f"{settings.phone_webapp_url}?lang={lang}"),
                )
            ]
        )
    rows.append([KeyboardButton(text=btn("cancel", lang))])
    return ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="+998 90 123 45 67",
    )


def suggest_kb(suggestion: str, lang: str = "uz") -> ReplyKeyboardMarkup:
    """Taklif qilingan qiymat (masalan, mijozning ma'lum ismi) + bekor qilish."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=suggestion)],
            [KeyboardButton(text=btn("cancel", lang))],
        ],
        resize_keyboard=True,
    )
