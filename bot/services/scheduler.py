"""Kunlik avtomatik ishlar: ustalarga hisobot va adminlarga zaxira.

Har bir ish uchun oxirgi bajarilgan sana bot_state jadvalida saqlanadi:
bot qayta ishga tushsa ham bir kunda ikki marta yuborilmaydi, belgilangan
vaqtda bot o'chiq bo'lsa — o'sha kuni yonishi bilan yuboriladi.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.services.backup import send_backup
from bot.services.reminders import load_settings, send_pending_reminders
from bot.services.reports import send_daily_reports
from bot.utils.formatters import now_local
from config import settings
from database.repositories import StateRepository

logger = logging.getLogger(__name__)

CHECK_EVERY = 30  # soniya


async def _daily_job(
    name: str,
    at: tuple[int, int],
    job: Callable[[], Awaitable[object]],
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    key = f"last_run:{name}"
    logger.info("Rejalashtirildi: %s — har kuni %02d:%02d", name, *at)
    while True:
        try:
            now = now_local()
            today = now.date().isoformat()
            if (now.hour, now.minute) >= at:
                async with session_factory() as session:
                    last = await StateRepository(session).get(key)
                if last != today:
                    # Avval belgilaymiz — ish yiqilsa ham qayta-qayta urinib spam qilmaydi
                    async with session_factory() as session:
                        await StateRepository(session).set(key, today)
                    logger.info("Ish boshlandi: %s", name)
                    await job()
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            logger.exception("Rejalashtirilgan ish xatosi: %s", name)
        await asyncio.sleep(CHECK_EVERY)


async def _reminder_job(
    bot: Bot, session_factory: async_sessionmaker[AsyncSession]
) -> None:
    """«Qolgan ishlar» eslatmasi: vaqt va holat har safar bazadan o'qiladi (admin sozlamasi)."""
    key = "last_run:pending_reminder"
    logger.info("Rejalashtirildi: pending_reminder (vaqt admin sozlamalaridan)")
    try:
        # Funksiya birinchi marta ishga tushyapti va bugungi vaqt o'tib ketgan bo'lsa —
        # darhol yubormaymiz, ertangi kundan boshlaymiz.
        async with session_factory() as session:
            config = await load_settings(session)
            repo = StateRepository(session)
            if await repo.get(key) is None:
                now = now_local()
                past = (now.hour, now.minute) >= (config.hour, config.minute)
                await repo.set(key, now.date().isoformat() if past else "init")
    except Exception:  # noqa: BLE001
        logger.exception("pending_reminder boshlang'ich holati o'rnatilmadi")
    while True:
        try:
            now = now_local()
            today = now.date().isoformat()
            async with session_factory() as session:
                config = await load_settings(session)
                last = await StateRepository(session).get(key)
            due = config.enabled and (now.hour, now.minute) >= (config.hour, config.minute)
            if due and last != today:
                async with session_factory() as session:
                    await StateRepository(session).set(key, today)
                logger.info("Ish boshlandi: pending_reminder")
                await send_pending_reminders(bot, session_factory)
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001
            logger.exception("Rejalashtirilgan ish xatosi: pending_reminder")
        await asyncio.sleep(CHECK_EVERY)


def start_scheduler(
    bot: Bot, session_factory: async_sessionmaker[AsyncSession]
) -> list[asyncio.Task]:
    return [
        asyncio.create_task(
            _daily_job(
                "daily_report",
                settings.report_time,
                lambda: send_daily_reports(bot, session_factory),
                session_factory,
            )
        ),
        asyncio.create_task(
            _daily_job(
                "daily_backup",
                settings.backup_time,
                lambda: send_backup(bot, session_factory),
                session_factory,
            )
        ),
        asyncio.create_task(_reminder_job(bot, session_factory)),
    ]
