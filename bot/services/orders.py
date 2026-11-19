"""Buyurtma yaratish va tayyor qilish — chat bot va Mini App uchun yagona logika."""

from __future__ import annotations

import logging

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from bot.services import group_publisher
from database.models import Order, OrderStatus, User
from database.repositories import OrderRepository

logger = logging.getLogger(__name__)


async def create_order(
    session: AsyncSession,
    bot: Bot,
    user: User,
    phone: str,
    name: str,
    description: str,
    number: int | None = None,
) -> tuple[Order, bool]:
    """Buyurtma yaratadi va guruhga e'lon qiladi. (buyurtma, e'lon_yuborildimi)."""
    repo = OrderRepository(session)
    # Poyga holati: taklif qilingan raqam band bo'lsa — navbatdagisini olamiz
    if number is None or await repo.get_by_number(number) is not None:
        number = await repo.next_number()
    order = await repo.create(
        order_number=number,
        created_by=user.id,
        customer_name=name,
        customer_phone=phone,
        description=description,
    )
    logger.info("Order #%s created by %s", number, user.full_name)
    message_id = await group_publisher.publish_pending(bot, order)
    if message_id is not None:
        await repo.set_pending_message_id(order.id, message_id)
    return order, message_id is not None


class OrderStateError(Exception):
    """Buyurtmani tayyor qilib bo'lmaydi (allaqachon tayyor / bekor qilingan)."""

    def __init__(self, status: str) -> None:
        super().__init__(status)
        self.status = status


async def complete_order(
    session: AsyncSession,
    bot: Bot,
    user: User,
    order_id: int,
    work_done: str,
    price: int,
) -> tuple[Order, bool] | None:
    """Tayyor deb belgilaydi va guruhga e'lon qiladi. Topilmasa None."""
    repo = OrderRepository(session)
    current = await session.get(Order, order_id)
    if current is None:
        return None
    if current.status != OrderStatus.PENDING:
        raise OrderStateError(current.status)
    order = await repo.mark_ready(
        order_id=order_id,
        work_done=work_done,
        price=price,
        completed_by=user.id,
        ready_message_id=None,
    )
    if order is None:
        return None
    logger.info("Order #%s marked as ready by %s", order.order_number, user.full_name)
    ready_msg_id = await group_publisher.publish_ready(bot, order)
    if ready_msg_id is not None:
        order.ready_message_id = ready_msg_id
        await session.commit()
        await group_publisher.update_pending_as_done(bot, order)
    return order, ready_msg_id is not None
