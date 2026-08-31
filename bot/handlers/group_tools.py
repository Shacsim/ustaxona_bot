"""Guruh bilan ishlash vositalari.

1) /groupid va /topicid — sozlash paytida guruh va topic ID'larini olish.
2) /post_about — «Biz haqimizda» bo'limiga ma'lumot yuborish (faqat admin).
3) Qo'riqchi — himoyalangan topic'larda begona (ro'yxatda yo'q) foydalanuvchi
   xabarini o'chiradi. Savol-javob topic'iga tegilmaydi.
"""

import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services import group_publisher
from config import settings
from database.models import User
from database.repositories import UserRepository

logger = logging.getLogger(__name__)
router = Router(name="group_tools")
router.message.filter(F.chat.type.in_({"group", "supergroup"}))


@router.message(Command("groupid"))
async def cmd_groupid(message: Message) -> None:
    await message.reply(
        f"🆔 Guruh ID: <code>{message.chat.id}</code>\n\n"
        "Bu qiymatni .env faylidagi GROUP_ID ga yozing."
    )


@router.message(Command("topicid"))
async def cmd_topicid(message: Message) -> None:
    topic_id = message.message_thread_id
    if topic_id is None:
        await message.reply(
            "Bu buyruqni forum topic ichida yuboring.\n"
            "General bo'limda topic ID bo'lmaydi."
        )
        return
    await message.reply(
        f"🆔 Ushbu topic ID: <code>{topic_id}</code>\n\n"
        "Bu qiymatni .env faylidagi tegishli *_TOPIC_ID ga yozing."
    )


def _is_anon_admin(message: Message) -> bool:
    """Guruhda anonim admin nomidan yozilgan xabarmi?

    Anonim admin xabarlarida from_user o'rniga sender_chat guruhning
    o'zi bo'ladi — bunday foydalanuvchini bazadan topib bo'lmaydi,
    lekin u aniq admin.
    """
    return (
        message.sender_chat is not None
        and message.sender_chat.id == message.chat.id
    )


def _is_admin(message: Message, user: User | None) -> bool:
    if _is_anon_admin(message):
        return True
    return user is not None and user.is_active and user.is_admin


@router.message(Command("close_topics"))
async def cmd_close_topics(message: Message, user: User | None, bot: Bot) -> None:
    """Himoyalangan 3 ta topic'ni yopadi — yopiq topic'ga faqat adminlar yozadi.

    Botga «Manage topics» admin huquqi kerak. Savol-javob ochiq qoladi.
    """
    if not _is_admin(message, user):
        return
    topics = {
        "📋 Kutayotganlar": settings.pending_topic_id,
        "✅ Tayyorlar": settings.ready_topic_id,
        "🏢 Biz haqimizda": settings.about_topic_id,
    }
    results = []
    for name, topic_id in topics.items():
        if topic_id is None:
            results.append(f"⚠️ {name}: topic ID .env da sozlanmagan")
            continue
        try:
            await bot.close_forum_topic(
                chat_id=message.chat.id, message_thread_id=topic_id
            )
            results.append(f"✅ {name}: yopildi")
        except TelegramAPIError as e:
            results.append(f"❌ {name}: {e}")
    results.append("\n❓ Savol-javoblar ochiq qoldi — mijozlar shu yerda yozadi.")
    await message.reply("\n".join(results))


@router.message(Command("post_about"))
async def cmd_post_about(message: Message, user: User | None, bot: Bot) -> None:
    if not _is_admin(message, user):
        return
    if settings.about_topic_id is None:
        await message.reply("ABOUT_TOPIC_ID sozlanmagan (.env).")
        return
    ok = await group_publisher.publish_about(bot)
    if ok:
        await message.reply("✅ «Biz haqimizda» ma'lumoti yuborildi.")
    else:
        await message.reply("❌ Yuborib bo'lmadi — loglarni tekshiring.")


@router.message()
async def guard_protected_topics(message: Message, user: User | None) -> None:
    """Himoyalangan topic'larda faqat xodimlar yozadi.

    Asosiy himoya Telegram guruh permissionlari orqali qilinadi (README).
    Bu qo'riqchi qo'shimcha qatlam: agar permission noto'g'ri sozlangan
    bo'lsa ham, begona xabarlar o'chiriladi.
    """
    if settings.group_id is None or message.chat.id != settings.group_id:
        return
    # Savol-javob bo'limi hammaga ochiq
    if settings.faq_topic_id is not None and message.message_thread_id == settings.faq_topic_id:
        return
    # Xodimlar (faol usta/admin) va anonim adminlar yozishi mumkin
    if user is not None and user.is_active:
        return
    if _is_anon_admin(message):
        return
    # Kanal nomidan yozilgan yoki servis xabarlariga tegmaymiz
    if message.sender_chat is not None or message.from_user is None:
        return
    try:
        await message.delete()
        logger.info(
            "Deleted message from non-staff user %s in protected topic %s",
            message.from_user.id,
            message.message_thread_id,
        )
    except TelegramAPIError as e:
        logger.warning("Begona xabarni o'chirib bo'lmadi: %s", e)
