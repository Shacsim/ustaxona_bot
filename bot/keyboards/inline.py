"""Inline klaviaturalar va callback data formatlari."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.models import User


def suggested_number_kb(number: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"✅ #{number} raqamini olish",
                    callback_data=f"neworder:suggest:{number}",
                )
            ]
        ]
    )


def confirm_new_order_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Qabul qilindi", callback_data="neworder:confirm"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="neworder:cancel"),
            ]
        ]
    )


def confirm_complete_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ TAYYOR", callback_data="complete:confirm"),
                InlineKeyboardButton(text="❌ BEKOR QILISH", callback_data="complete:cancel"),
            ]
        ]
    )


def admin_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍🔧 Ustalar", callback_data="admin:masters")],
            [InlineKeyboardButton(text="📊 Statistika", callback_data="admin:stats")],
            [InlineKeyboardButton(text="📦 Buyurtmalar", callback_data="admin:orders")],
            [InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="admin:settings")],
        ]
    )


def masters_list_kb(masters: list[User]) -> InlineKeyboardMarkup:
    rows = []
    for m in masters:
        status = "✅" if m.is_active else "⛔️"
        role = "👑" if m.is_admin else "🔧"
        rows.append(
            [
                InlineKeyboardButton(
                    text=f"{status} {role} {m.full_name}",
                    callback_data=f"admin:master:{m.id}",
                )
            ]
        )
    rows.append([InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin:panel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def master_detail_kb(master: User) -> InlineKeyboardMarkup:
    toggle_text = "⛔️ Bloklash" if master.is_active else "✅ Faollashtirish"
    toggle_action = "block" if master.is_active else "activate"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=toggle_text,
                    callback_data=f"admin:{toggle_action}:{master.id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="🗑 O'chirish", callback_data=f"admin:delete:{master.id}"
                )
            ],
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin:masters")],
        ]
    )


def approve_master_kb(master_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash", callback_data=f"admin:activate:{master_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish", callback_data=f"admin:delete:{master_id}"
                ),
            ]
        ]
    )


def back_to_panel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin:panel")]
        ]
    )
