"""Usta menyusi: bekor qilish, ro'yxatlar, profil."""

from html import escape

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.reply import (
    BTN_CANCEL,
    BTN_PENDING,
    BTN_PROFILE,
    BTN_READY_LIST,
    master_menu,
)
from bot.utils.formatters import fmt_dt, fmt_price
from database.models import OrderStatus, User
from database.repositories import OrderRepository

router = Router(name="menu")


@router.message(F.text == BTN_CANCEL)
async def cancel_anywhere(message: Message, state: FSMContext, user: User) -> None:
    """Istalgan FSM jarayonini bekor qiladi."""
    await state.clear()
    await message.answer(
        "❌ Amal bekor qilindi.", reply_markup=master_menu(user.is_admin)
    )


@router.message(StateFilter(None), F.text == BTN_PENDING)
async def list_pending(message: Message, session: AsyncSession, user: User) -> None:
    orders = await OrderRepository(session).list_by_status(OrderStatus.PENDING)
    if not orders:
        await message.answer("📋 Hozircha kutayotgan buyurtmalar yo'q.")
        return
    lines = ["📋 <b>KUTAYOTGAN BUYURTMALAR</b>\n"]
    for o in orders:
        lines.append(
            f"⏳ <b>#{o.order_number}</b> — {escape(o.creator.full_name)} "
            f"({fmt_dt(o.created_at)})"
        )
    await message.answer("\n".join(lines))


@router.message(StateFilter(None), F.text == BTN_READY_LIST)
async def list_ready(message: Message, session: AsyncSession, user: User) -> None:
    orders = await OrderRepository(session).list_by_status(OrderStatus.READY, limit=10)
    if not orders:
        await message.answer("✅ Hozircha tayyor buyurtmalar yo'q.")
        return
    lines = ["✅ <b>TAYYOR BUYURTMALAR</b> (oxirgi 10 ta)\n"]
    for o in orders:
        master = o.completer.full_name if o.completer else o.creator.full_name
        lines.append(
            f"✅ <b>#{o.order_number}</b> — {fmt_price(o.price)} — {escape(master)} "
            f"({fmt_dt(o.completed_at)})"
        )
    await message.answer("\n".join(lines))


@router.message(StateFilter(None), F.text == BTN_PROFILE)
async def profile(message: Message, user: User) -> None:
    role = "👑 Administrator" if user.is_admin else "🔧 Usta"
    await message.answer(
        "👤 <b>PROFIL</b>\n\n"
        f"Ism: <b>{escape(user.full_name)}</b>\n"
        f"Rol: {role}\n"
        f"Telegram ID: <code>{user.telegram_id}</code>\n"
        f"Ro'yxatdan o'tgan: {fmt_dt(user.created_at)}"
    )
