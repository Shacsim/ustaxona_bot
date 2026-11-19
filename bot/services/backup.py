"""Bazaning zaxira nusxasi: pg_dump → gzip → adminlarga Telegram orqali.

Server butunlay yo'qolsa ham (region-reinstall kabi) oxirgi nusxa
adminning Telegram chatida saqlanib qoladi.
"""

from __future__ import annotations

import asyncio
import gzip
import logging
from html import escape

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BufferedInputFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.utils.formatters import now_local
from bot.utils.i18n import t
from config import settings
from database.models import Order, Product, User
from database.repositories import UserRepository

logger = logging.getLogger(__name__)

TELEGRAM_FILE_LIMIT = 49 * 1024 * 1024


def _libpq_url() -> str:
    """SQLAlchemy URL'idan pg_dump tushunadigan URL ('+asyncpg' siz)."""
    return settings.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)


async def make_dump() -> bytes:
    proc = await asyncio.create_subprocess_exec(
        "pg_dump",
        "--clean",
        "--if-exists",
        "--no-owner",
        "--dbname",
        _libpq_url(),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, err = await asyncio.wait_for(proc.communicate(), timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(err.decode(errors="replace").strip()[:500] or "pg_dump failed")
    return gzip.compress(out, compresslevel=9)


async def _admin_recipients(session: AsyncSession) -> dict[int, str]:
    """telegram_id → til. ADMIN_IDS + bazadagi faol adminlar."""
    recipients = {tg: "uz" for tg in settings.admin_ids}
    for admin in await UserRepository(session).list_active_admins():
        recipients[admin.telegram_id] = admin.language
    for tg in settings.admin_ids:
        user = await UserRepository(session).get_by_telegram_id(tg)
        if user is not None:
            recipients[tg] = user.language
    return recipients


async def send_backup(
    bot: Bot,
    session_factory: async_sessionmaker[AsyncSession],
    only_to: int | None = None,
) -> bool:
    """Zaxira oladi va adminlarga yuboradi. only_to — faqat bitta adminga (qo'lda so'rov)."""
    async with session_factory() as session:
        recipients = await _admin_recipients(session)
        counts = [
            int((await session.execute(select(func.count()).select_from(model))).scalar_one())
            for model in (Order, User, Product)
        ]
    if only_to is not None:
        recipients = {only_to: recipients.get(only_to, "uz")}

    stamp = now_local()
    filename = f"ustaxona_{stamp.strftime('%Y%m%d_%H%M')}.sql.gz"
    try:
        data = await make_dump()
        if len(data) > TELEGRAM_FILE_LIMIT:
            raise RuntimeError(f"dump too large for Telegram: {len(data)} bytes")
    except Exception as e:  # noqa: BLE001
        logger.exception("Zaxira olinmadi")
        for tg, lang in recipients.items():
            try:
                await bot.send_message(tg, t("backup_failed", lang, err=escape(str(e))))
            except TelegramAPIError:
                pass
        return False

    ok = False
    for tg, lang in recipients.items():
        caption = t(
            "backup_caption",
            lang,
            when=stamp.strftime("%d.%m.%Y %H:%M"),
            orders=counts[0],
            users=counts[1],
            products=counts[2],
            file=filename,
        )
        try:
            await bot.send_document(
                tg, BufferedInputFile(data, filename=filename), caption=caption
            )
            ok = True
        except TelegramAPIError as e:
            logger.warning("Zaxira %s ga yuborilmadi: %s", tg, e)
    logger.info("Zaxira yuborildi (%s bayt, %s ta adminga)", len(data), len(recipients))
    return ok
