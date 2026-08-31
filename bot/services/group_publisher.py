"""Guruhga topic bo'yicha e'lon yuborish — yagona nuqta.

Barcha Telegram API xatolari shu yerda ushlanadi va log qilinadi;
handler'lar None qaytganini ko'rib ustaga xabar beradi.
"""

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from bot.utils import formatters
from config import settings
from database.models import Order

logger = logging.getLogger(__name__)


async def ensure_topic_closed(bot: Bot, topic_id: int | None) -> None:
    """Himoyalangan topic yopiqligiga ishonch hosil qiladi.

    Telegram mijoz-ilovalari admin yozganda yopiq topic'ni qayta ochib
    yuborishi mumkin — shuning uchun har e'londan keyin qayta yopamiz.
    Allaqachon yopiq bo'lsa (TOPIC_NOT_MODIFIED) — jimgina o'tamiz.
    """
    if settings.group_id is None or topic_id is None:
        return
    try:
        await bot.close_forum_topic(
            chat_id=settings.group_id, message_thread_id=topic_id
        )
    except TelegramAPIError:
        pass


async def _send_to_topic(bot: Bot, topic_id: int | None, text: str) -> int | None:
    """Xabar yuboradi, muvaffaqiyatda message_id qaytaradi."""
    if settings.group_id is None:
        logger.error("GROUP_ID sozlanmagan — guruhga xabar yuborilmadi.")
        return None
    try:
        message = await bot.send_message(
            chat_id=settings.group_id,
            message_thread_id=topic_id,
            text=text,
        )
        await ensure_topic_closed(bot, topic_id)
        return message.message_id
    except TelegramAPIError as e:
        logger.error("Guruhga xabar yuborishda xato (topic=%s): %s", topic_id, e)
        return None


async def publish_pending(bot: Bot, order: Order) -> int | None:
    """«Kutayotgan buyurtmalar» topic'iga e'lon."""
    return await _send_to_topic(
        bot, settings.pending_topic_id, formatters.pending_group_text(order)
    )


async def publish_ready(bot: Bot, order: Order) -> int | None:
    """«Tayyor buyurtmalar» topic'iga e'lon."""
    return await _send_to_topic(
        bot, settings.ready_topic_id, formatters.ready_group_text(order)
    )


async def update_pending_as_done(bot: Bot, order: Order) -> bool:
    """Eski «kutayotgan» xabarni «tayyor bo'ldi» deb yangilaydi.

    Telegram cheklovi tufayli imkoni bo'lmasa — jimgina log qilinadi,
    tizim ishlashda davom etadi.
    """
    if settings.group_id is None or not order.pending_message_id:
        return False
    try:
        await bot.edit_message_text(
            chat_id=settings.group_id,
            message_id=order.pending_message_id,
            text=formatters.pending_done_note(order),
        )
        return True
    except TelegramAPIError as e:
        logger.warning(
            "Kutayotgan xabarni yangilab bo'lmadi (order #%s): %s",
            order.order_number,
            e,
        )
        return False


async def publish_about(bot: Bot) -> bool:
    """«Biz haqimizda» topic'iga ma'lumot + lokatsiya yuboradi."""
    msg_id = await _send_to_topic(bot, settings.about_topic_id, formatters.about_text())
    if msg_id is None:
        return False
    if settings.workshop_lat and settings.workshop_lon:
        try:
            await bot.send_location(
                chat_id=settings.group_id,
                message_thread_id=settings.about_topic_id,
                latitude=float(settings.workshop_lat),
                longitude=float(settings.workshop_lon),
            )
        except (TelegramAPIError, ValueError) as e:
            logger.warning("Lokatsiya yuborilmadi: %s", e)
    return True
