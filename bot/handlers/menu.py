"""Usta menyusi: bekor qilish, ro'yxatlar, profil (ikki tilda)."""

from html import escape

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.reply import master_menu
from bot.utils.formatters import fmt_dt, fmt_price, pending_list_text, period_start
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
    orders = await OrderRepository(session).list_by_status(
        OrderStatus.PENDING, limit=50, oldest_first=True
    )
    if not orders:
        await message.answer(t("none_pending", lang))
        return
    for chunk in pending_list_text(orders, lang):
        await message.answer(chunk)


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


INCOME_PERIODS = [
    ("📅", "period_today", "today"),
    ("🗓", "period_week", "week"),
    ("📆", "period_month", "month"),
    ("∑", "period_all", "all"),
]


@router.message(StateFilter(None), F.text.in_(btn_variants("my_income")))
async def my_income(message: Message, session: AsyncSession, user: User) -> None:
    """Ustaning o'z daromadi: bugun / hafta / oy / jami."""
    lang = user.language
    repo = OrderRepository(session)
    lines = [t("income_header", lang, name=escape(user.full_name))]
    for icon, label_key, period in INCOME_PERIODS:
        count, total = await repo.master_income(user.id, period_start(period))
        lines.append(
            t(
                "income_row",
                lang,
                icon=icon,
                label=t(label_key, lang),
                total=fmt_price(total),
                count=count,
            )
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
