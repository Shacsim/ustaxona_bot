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
    ]
