"""Bot yangilangani haqida barcha faol a'zolarga xabar (har biriga o'z tilida).

Ishga tushirish (serverda):
    sudo docker compose exec bot python -m scripts.announce_update          # sinov: kimga ketishini ko'rsatadi
    sudo docker compose exec bot python -m scripts.announce_update --send   # haqiqatan yuborish
    ... --app   # «bot endi ilova ko'rinishida ham» xabari (ilovani ochish tugmasi bilan)
"""

import asyncio
import sys

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError

from bot.keyboards.inline import open_app_kb
from bot.keyboards.reply import master_menu
from bot.utils.i18n import t
from config import settings
from database.engine import create_session_factory
from database.repositories import UserRepository


async def main(send: bool, app: bool = False) -> None:
    sf = create_session_factory()
    async with sf() as session:
        users = await UserRepository(session).list_active()
    report = "%02d:%02d" % settings.report_time
    bot = Bot(settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    ok = 0
    try:
        for u in users:
            print(f"{'→' if send else '·'} {u.full_name} ({u.telegram_id}) til={u.language}")
            if not send:
                continue
            try:
                if app:
                    await bot.send_message(
                        u.telegram_id,
                        t("update_announce_app", u.language),
                        reply_markup=open_app_kb(u.language),
                    )
                else:
                    await bot.send_message(
                        u.telegram_id,
                        t("update_announce", u.language, report=report),
                        reply_markup=master_menu(u.language, u.is_admin),
                    )
                ok += 1
            except TelegramAPIError as e:
                print("   yetmadi:", e)
            await asyncio.sleep(0.1)
    finally:
        await bot.session.close()
    print(f"Jami faol: {len(users)}; yuborildi: {ok}" if send else "Sinov rejimi — --send bilan yuboring")


if __name__ == "__main__":
    asyncio.run(main("--send" in sys.argv, app="--app" in sys.argv))
