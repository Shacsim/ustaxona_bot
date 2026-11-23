"""Kunlik «qolgan ishlar» eslatmasi: kutayotgan buyurtmalar va qancha vaqtdan beri kutayotgani.

Sozlamalar bazadagi bot_state jadvalida (admin panel orqali o'zgartiriladi):
  reminder_enabled       "1" / "0"            (standart: yoqilgan)
  reminder_time          "HH:MM"              (standart: 19:30)
  reminder_overdue_days  1..30                (standart: 3 — shundan ortig'i ⚠️ kechikkan)
  reminder_target        "all" / "admins"     (standart: barcha faol ustalar)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from html import escape

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.utils.formatters import fmt_dt, now_local, wait_days
from bot.utils.i18n import t
from database.models import Order, OrderStatus, User
from database.repositories import OrderRepository, StateRepository, UserRepository

logger = logging.getLogger(__name__)

KEY_ENABLED = "reminder_enabled"
KEY_TIME = "reminder_time"
KEY_OVERDUE = "reminder_overdue_days"
KEY_TARGET = "reminder_target"
TARGETS = ("all", "admins")
MESSAGE_LIMIT = 3800


@dataclass
class ReminderSettings:
    enabled: bool = True
    hour: int = 19
    minute: int = 30
    overdue_days: int = 3
    target: str = "all"

    @property
    def time_text(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}"


def parse_time(text: str) -> tuple[int, int] | None:
    """'19:30', '9:05', '1930' → (soat, daqiqa); noto'g'ri bo'lsa None."""
    raw = text.strip().replace(".", ":").replace(" ", "")
    if ":" not in raw and raw.isdigit() and len(raw) in (3, 4):
        raw = f"{raw[:-2]}:{raw[-2:]}"
    parts = raw.split(":")
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        return None
    hour, minute = int(parts[0]), int(parts[1])
    if 0 <= hour < 24 and 0 <= minute < 60:
        return hour, minute
    return None


async def load_settings(session: AsyncSession) -> ReminderSettings:
    repo = StateRepository(session)
    result = ReminderSettings()
    enabled = await repo.get(KEY_ENABLED)
    if enabled is not None:
        result.enabled = enabled == "1"
    at = parse_time(await repo.get(KEY_TIME) or "")
    if at:
        result.hour, result.minute = at
    overdue = await repo.get(KEY_OVERDUE)
    if overdue and overdue.isdigit() and 1 <= int(overdue) <= 30:
        result.overdue_days = int(overdue)
    target = await repo.get(KEY_TARGET)
    if target in TARGETS:
        result.target = target
    return result


async def save_settings(session: AsyncSession, value: ReminderSettings) -> None:
    repo = StateRepository(session)
    await repo.set(KEY_ENABLED, "1" if value.enabled else "0")
    await repo.set(KEY_TIME, value.time_text)
    await repo.set(KEY_OVERDUE, str(value.overdue_days))
    await repo.set(KEY_TARGET, value.target)


def reminder_messages(orders: list[Order], lang: str, overdue_days: int) -> list[str]:
    """Eslatma matni (Telegram chegarasi uchun bir nechta xabarga bo'linadi)."""
    date = now_local().strftime("%d.%m.%Y")
    if not orders:
        return [t("rem_none", lang, date=date)]
    overdue = [o for o in orders if wait_days(o.created_at) >= overdue_days]
    header = t(
        "rem_header", lang, date=date, total=len(orders), overdue=len(overdue), days=overdue_days
    )
    lines = []
    for o in orders:
        days = wait_days(o.created_at)
        icon = "⚠️" if days >= overdue_days else "⏳"
        age = t("rem_today", lang) if days == 0 else t("rem_days", lang, n=days)
        master = o.creator.full_name if o.creator else "—"
        lines.append(
            t(
                "rem_row",
                lang,
                icon=icon,
                n=o.order_number,
                age=age,
                when=fmt_dt(o.created_at),
                customer=escape(o.customer_name or "—"),
                task=escape((o.description or "—")[:120]),
                master=escape(master),
            )
        )
    footer = t("rem_footer", lang)
    messages, current = [], header
    for line in lines:
        if len(current) + len(line) + 2 > MESSAGE_LIMIT:
            messages.append(current)
            current = line
        else:
            current = f"{current}\n\n{line}"
    current = f"{current}\n\n{footer}"
    messages.append(current)
    return messages


async def recipients(session: AsyncSession, target: str) -> list[User]:
    users = await UserRepository(session).list_active()
    if target == "admins":
        users = [u for u in users if u.is_admin]
    return users


async def send_pending_reminders(
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
    only_to: User | None = None,
) -> int:
    """Eslatmani yuboradi. only_to — faqat bitta foydalanuvchiga (admin sinovi)."""
    async with session_factory() as session:
        config = await load_settings(session)
        orders = await OrderRepository(session).list_by_status(
            OrderStatus.PENDING, limit=500, oldest_first=True
        )
        users = [only_to] if only_to else await recipients(session, config.target)
    sent = 0
    for user in users:
        try:
            for text in reminder_messages(orders, user.language, config.overdue_days):
                try:
                    await bot.send_message(user.telegram_id, text)
                except TelegramRetryAfter as e:
                    await asyncio.sleep(e.retry_after + 1)
                    await bot.send_message(user.telegram_id, text)
            sent += 1
        except TelegramAPIError as e:
            logger.warning("Eslatma %s ga yetmadi: %s", user.telegram_id, e)
        await asyncio.sleep(0.1)
    logger.info("Qolgan ishlar eslatmasi: %s ta buyurtma, %s / %s ga", len(orders), sent, len(users))
    return sent
