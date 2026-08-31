"""Usta menyusi: bekor qilish, ro'yxatlar, profil (ikki tilda)."""

from html import escape

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.reply import master_menu
from bot.utils.formatters import fmt_dt, fmt_price
from bot.utils.i18n import btn_variants, t
from database.models import OrderStatus, User
from database.repositories import OrderRepository

router = Router(name="menu")


@router.message(F.text.in_(btn_variants("cancel")))
async def cancel_anywhere(message: Message, state: FSMContext, user: User) -> None:
    """Istalgan FSM jarayonini bekor qiladi."""
    lang = user.language
    await state.clear()
    await message.answer(
        t("cancelled", lang), reply_markup=master_menu(lang, user.is_admin)
    )


@router.message(StateFilter(None), F.text.in_(btn_variants("pending")))
async def list_pending(message: Message, session: AsyncSession, user: User) -> None:
    lang = user.language
    orders = await OrderRepository(session).list_by_status(OrderStatus.PENDING)
    if not orders:
        await message.answer(t("none_pending", lang))
        return
    lines = [t("pending_header", lang)]
    for o in orders:
        customer = f" — {escape(o.customer_name)}" if o.customer_name else ""
        lines.append(
            f"⏳ <b>#{o.order_number}</b>{customer} · {escape(o.creator.full_name)} "
            f"({fmt_dt(o.created_at)})"
        )
    await message.answer("\n".join(lines))


@router.message(StateFilter(None), F.text.in_(btn_variants("ready_list")))
async def list_ready(message: Message, session: AsyncSession, user: User) -> None:
    lang = user.language
    orders = await OrderRepository(session).list_by_status(OrderStatus.READY, limit=10)
    if not orders:
        await message.answer(t("none_ready", lang))
        return
    lines = [t("ready_header", lang)]
    for o in orders:
        master = o.completer.full_name if o.completer else o.creator.full_name
        lines.append(
            f"✅ <b>#{o.order_number}</b> — {fmt_price(o.price)} — {escape(master)} "
            f"({fmt_dt(o.completed_at)})"
        )
    await message.answer("\n".join(lines))


@router.message(StateFilter(None), F.text.in_(btn_variants("profile")))
async def profile(message: Message, user: User) -> None:
    lang = user.language
    role = t("role_admin", lang) if user.is_admin else t("role_master", lang)
    await message.answer(
        t(
            "profile_card",
            lang,
            name=escape(user.full_name),
            role=role,
            tg_id=user.telegram_id,
            created=fmt_dt(user.created_at),
        )
    )
