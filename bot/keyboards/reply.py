"""Reply klaviaturalar va tugma matnlari."""

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

BTN_NEW_ORDER = "➕ Yangi buyurtma"
BTN_PENDING = "📋 Kutayotgan buyurtmalar"
BTN_READY_LIST = "✅ Tayyor buyurtmalar"
BTN_COMPLETE = "🛠 Buyurtmani tayyor qilish"
BTN_SEARCH = "🔎 Buyurtmani topish"
BTN_PROFILE = "👤 Profil"
BTN_ADMIN = "⚙️ Admin panel"
BTN_CANCEL = "❌ Bekor qilish"


def master_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text=BTN_NEW_ORDER), KeyboardButton(text=BTN_COMPLETE)],
        [KeyboardButton(text=BTN_PENDING), KeyboardButton(text=BTN_READY_LIST)],
        [KeyboardButton(text=BTN_SEARCH), KeyboardButton(text=BTN_PROFILE)],
    ]
    if is_admin:
        keyboard.append([KeyboardButton(text=BTN_ADMIN)])
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Amalni tanlang…",
    )


def cancel_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BTN_CANCEL)]],
        resize_keyboard=True,
    )
