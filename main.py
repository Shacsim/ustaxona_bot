"""Ustaxona bot — kirish nuqtasi.

Ishga tushirish tartibi:
  1) Konfiguratsiya tekshiruvi (yetishmasa aniq xabar bilan to'xtaydi);
  2) DB sessiya fabrikasi;
  3) Middlewarelar (sessiya → foydalanuvchi → authorization);
  4) Routerlar (tartib muhim!);
  5) Polling.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from bot.handlers import (
    admin,
    complete_order,
    errors,
    fallback,
    group_tools,
    menu,
    new_order,
    registration,
    search,
)
from bot.middlewares import AuthMiddleware, DbSessionMiddleware, UserLoaderMiddleware
from config import settings
from database.engine import create_session_factory

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


async def main() -> None:
    config_errors = settings.validate()
    if config_errors:
        for e in config_errors:
            logger.error("KONFIGURATSIYA XATOSI: %s", e)
        sys.exit(1)
    if not settings.group_configured():
        logger.warning(
            "GROUP_ID/TOPIC_ID'lar to'liq sozlanmagan — guruhga e'lonlar yuborilmaydi. "
            "Guruhda /groupid va /topicid buyruqlari bilan ID'larni olib .env ga yozing."
        )

    session_factory = create_session_factory()

    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewarelar: sessiya → foydalanuvchi (har bir update uchun)
    dp.update.outer_middleware(DbSessionMiddleware(session_factory))
    dp.update.outer_middleware(UserLoaderMiddleware())

    # Himoyalangan routerlar: faqat ro'yxatdan o'tgan faol xodimlar
    auth = AuthMiddleware()
    for protected in (menu, new_order, complete_order, search, admin):
        protected.router.message.middleware(auth)
        protected.router.callback_query.middleware(auth)

    # Tartib muhim: xatolar → guruh → registratsiya → asosiy oqimlar → fallback
    dp.include_router(errors.router)
    dp.include_router(group_tools.router)
    dp.include_router(registration.router)
    dp.include_router(menu.router)
    dp.include_router(new_order.router)
    dp.include_router(complete_order.router)
    dp.include_router(search.router)
    dp.include_router(admin.router)
    dp.include_router(fallback.router)

    await bot.set_my_commands(
        [BotCommand(command="start", description="Botni ishga tushirish")]
    )

    logger.info("Bot started")
    await bot.delete_webhook(drop_pending_updates=True)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Bot stopped")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi")
