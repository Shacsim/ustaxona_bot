"""Hisobotlarni bazadan yig'ish va yuborish (handler'lar va rejalashtiruvchi uchun)."""

from __future__ import annotations

import asyncio
import logging
from html import escape

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.types import BufferedInputFile
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.services.pdf_reports import MasterReport, master_pdf, pending_pdf, ready_pdf
from bot.utils.formatters import fmt_price, now_local, period_start
from bot.utils.i18n import t
from database.models import MoveKind, OrderStatus, User
from database.repositories import InventoryRepository, OrderRepository, UserRepository

logger = logging.getLogger(__name__)

PERIODS = ("today", "week", "month", "all")
PERIOD_KEYS = {
    "today": "period_today",
    "week": "period_week",
    "month": "period_month",
    "all": "period_all",
}
FILE_PREFIX = {"uz": "hisobot", "ru": "otchet", "en": "report"}


def period_label(period: str, lang: str) -> str:
    """'Bugun (20.11.2026)', 'Shu hafta (17.11.2026 — 20.11.2026)', 'Jami'."""
    name = t(PERIOD_KEYS.get(period, "period_all"), lang)
    start = period_start(period)
    today = now_local().strftime("%d.%m.%Y")
    if start is None:
        return name
    if period == "today":
        return f"{name} ({today})"
    return f"{name} ({start.strftime('%d.%m.%Y')} — {today})"


def pdf_filename(kind: str, lang: str) -> str:
    return f"{FILE_PREFIX.get(lang, 'hisobot')}_{kind}_{now_local().strftime('%Y%m%d_%H%M')}.pdf"


async def build_pending_pdf(session: AsyncSession, lang: str) -> tuple[bytes, int]:
    orders = await OrderRepository(session).list_by_status(
        OrderStatus.PENDING, limit=1000, oldest_first=True
    )
    return pending_pdf(orders, lang), len(orders)


async def build_ready_pdf(session: AsyncSession, period: str, lang: str) -> tuple[bytes, int]:
    orders = await OrderRepository(session).list_ready_between(period_start(period))
    return ready_pdf(orders, period_label(period, lang), lang), len(orders)


async def build_master_report(
    session: AsyncSession, user: User, period: str, daily: bool = False
) -> tuple[bytes, MasterReport]:
    lang = user.language
    since = period_start(period)
    orders = OrderRepository(session)
    inv = InventoryRepository(session)
    rep = MasterReport(
        master_name=user.full_name,
        period_label=period_label(period, lang),
        orders_done=await orders.list_ready_between(since, completed_by=user.id),
        sales=await inv.list_moves(user.id, kind=MoveKind.OUT, since=since),
        purchases=await inv.list_moves(user.id, kind=MoveKind.IN, since=since),
        stock=await inv.list_products(user.id, in_stock_only=True),
        pending_count=await orders.count_pending_by(user.id),
        daily=daily,
    )
    return master_pdf(rep, lang), rep


def daily_caption(rep: MasterReport, lang: str) -> str:
    return t(
        "daily_caption",
        lang,
        date=now_local().strftime("%d.%m.%Y"),
        name=escape(rep.master_name),
        orders=len(rep.orders_done),
        income=fmt_price(sum(o.price or 0 for o in rep.orders_done), lang),
        sold=sum(m.quantity for m in rep.sales),
        sales=fmt_price(sum(m.total for m in rep.sales), lang),
        profit=fmt_price(sum(m.profit for m in rep.sales), lang),
        bought=sum(m.quantity for m in rep.purchases),
        buys=fmt_price(sum(m.total for m in rep.purchases), lang),
        units=sum(p.quantity for p in rep.stock),
        value=fmt_price(sum(p.quantity * p.avg_cost for p in rep.stock), lang),
    )


async def send_daily_reports(bot: Bot, session_factory: async_sessionmaker[AsyncSession]) -> int:
    """Har bir faol ustaga bugungi hisobot (PDF + qisqa matn). Yuborilganlar sonini qaytaradi."""
    async with session_factory() as session:
        users = await UserRepository(session).list_active()
    sent = 0
    for user in users:
        try:
            async with session_factory() as session:
                pdf, rep = await build_master_report(session, user, "today", daily=True)
            doc = BufferedInputFile(pdf, filename=pdf_filename("kunlik", user.language))
            caption = daily_caption(rep, user.language)
            try:
                await bot.send_document(user.telegram_id, doc, caption=caption)
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after + 1)
                await bot.send_document(user.telegram_id, doc, caption=caption)
            sent += 1
        except TelegramAPIError as e:
            logger.warning("Kunlik hisobot %s ga yetmadi: %s", user.telegram_id, e)
        except Exception:  # noqa: BLE001 — bitta usta xatosi boshqalarni to'xtatmasin
            logger.exception("Kunlik hisobot tuzishda xato (user %s)", user.id)
        await asyncio.sleep(0.1)
    logger.info("Kunlik hisobot yuborildi: %s / %s", sent, len(users))
    return sent
