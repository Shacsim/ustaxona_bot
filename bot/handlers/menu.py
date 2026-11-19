"""Usta menyusi: bekor qilish, ro'yxatlar (+PDF), daromad, profil."""

from html import escape

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import income_pdf_kb, pending_pdf_kb, ready_pdf_kb
from bot.keyboards.reply import master_menu
from bot.services import reports
from bot.utils.formatters import fmt_dt, fmt_price, pending_list_text, period_start
from bot.utils.i18n import LANG_NAMES, btn_variants, t
from database.models import OrderStatus, User
from database.repositories import InventoryRepository, OrderRepository

router = Router(name="menu")


@router.message(F.text.in_(btn_variants("cancel")))
async def cancel_anywhere(message: Message, state: FSMContext, user: User) -> None:
    """Istalgan FSM jarayonini bekor qiladi."""
    lang = user.language
    await state.clear()
    await message.answer(t("cancelled", lang), reply_markup=master_menu(lang, user.is_admin))


@router.message(StateFilter(None), F.text.in_(btn_variants("pending")))
async def list_pending(message: Message, session: AsyncSession, user: User) -> None:
    lang = user.language
    orders = await OrderRepository(session).list_by_status(
        OrderStatus.PENDING, limit=50, oldest_first=True
    )
    if not orders:
        await message.answer(t("none_pending", lang))
        return
    chunks = pending_list_text(orders, lang)
    for i, chunk in enumerate(chunks):
        last = i == len(chunks) - 1
        await message.answer(chunk, reply_markup=pending_pdf_kb(lang) if last else None)


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
            f"✅ <b>#{o.order_number}</b> — {fmt_price(o.price, lang)} — {escape(master)} "
            f"({fmt_dt(o.completed_at)})"
        )
    lines += ["", t("pdf_ready_offer", lang)]
    await message.answer("\n".join(lines), reply_markup=ready_pdf_kb(lang))


@router.callback_query(F.data == "pdf:pending")
async def pending_pdf(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    await callback.answer(t("pdf_making", lang))
    pdf, count = await reports.build_pending_pdf(session, lang)
    if count == 0:
        await callback.message.answer(t("none_pending", lang))
        return
    await callback.message.answer_document(
        BufferedInputFile(pdf, filename=reports.pdf_filename("kutayotgan", lang)),
        caption=f"📋 {t('pdf_btn', lang)} — {count}",
    )


@router.callback_query(F.data.startswith("pdf:ready:"))
async def ready_pdf(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    period = callback.data.split(":")[2]
    if period not in reports.PERIODS:
        period = "all"
    await callback.answer(t("pdf_making", lang))
    pdf, count = await reports.build_ready_pdf(session, period, lang)
    if count == 0:
        await callback.message.answer(t("pdf_empty", lang))
        return
    await callback.message.answer_document(
        BufferedInputFile(pdf, filename=reports.pdf_filename("tayyor", lang)),
        caption=f"✅ {reports.period_label(period, lang)} — {count}",
    )


INCOME_PERIODS = [
    ("📅", "period_today", "today"),
    ("🗓", "period_week", "week"),
    ("📆", "period_month", "month"),
    ("∑", "period_all", "all"),
]


@router.message(StateFilter(None), F.text.in_(btn_variants("my_income")))
async def my_income(message: Message, session: AsyncSession, user: User) -> None:
    """Ustaning o'z daromadi: bugun / hafta / oy / jami (+ bugungi ombor sotuvi)."""
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
                total=fmt_price(total, lang),
                count=count,
            )
        )
    sales = await InventoryRepository(session).totals(user.id, since=period_start("today"))
    if sales.out_units:
        lines += [
            "",
            t(
                "income_sales_row",
                lang,
                total=fmt_price(sales.out_sum, lang),
                profit=fmt_price(sales.profit, lang),
            ),
        ]
    lines += ["", t("inv_pdf_offer", lang)]
    await message.answer("\n".join(lines), reply_markup=income_pdf_kb(lang))


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
            language=LANG_NAMES.get(lang, lang),
            tg_id=user.telegram_id,
            created=fmt_dt(user.created_at),
        )
    )
