"""Buyurtmalar bilan ishlash — barcha SQL shu yerda."""

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Order, OrderStatus, User


class OrderRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_number(self, order_number: int) -> Order | None:
        result = await self.session.execute(
            select(Order).where(Order.order_number == order_number)
        )
        return result.scalar_one_or_none()

    async def next_number(self) -> int:
        """Keyingi taklif qilinadigan buyurtma raqami."""
        result = await self.session.execute(func.max(Order.order_number))
        current_max = result.scalar()
        return (current_max or 0) + 1

    async def create(
        self,
        order_number: int,
        created_by: int,
        customer_name: str | None = None,
        customer_phone: str | None = None,
        description: str | None = None,
    ) -> Order:
        order = Order(
            order_number=order_number,
            status=OrderStatus.PENDING,
            created_by=created_by,
            customer_name=customer_name,
            customer_phone=customer_phone,
            description=description,
        )
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def set_pending_message_id(self, order_id: int, message_id: int) -> None:
        order = await self.session.get(Order, order_id)
        if order is not None:
            order.pending_message_id = message_id
            await self.session.commit()

    async def mark_ready(
        self,
        order_id: int,
        work_done: str,
        price: int,
        completed_by: int,
        ready_message_id: int | None,
    ) -> Order | None:
        order = await self.session.get(Order, order_id)
        if order is None:
            return None
        order.status = OrderStatus.READY
        order.work_done = work_done
        order.price = price
        order.completed_by = completed_by
        order.ready_message_id = ready_message_id
        order.completed_at = datetime.now(timezone.utc)
        await self.session.commit()
        await self.session.refresh(order)
        return order

    async def list_by_status(self, status: OrderStatus, limit: int = 15) -> list[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.status == status)
            .order_by(Order.order_number.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    # ---------- Statistika ----------

    async def count_by_status(self, status: OrderStatus) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(Order).where(Order.status == status)
        )
        return int(result.scalar_one())

    async def count_all(self) -> int:
        result = await self.session.execute(select(func.count()).select_from(Order))
        return int(result.scalar_one())

    async def total_revenue(self) -> int:
        result = await self.session.execute(
            select(func.coalesce(func.sum(Order.price), 0)).where(
                Order.status == OrderStatus.READY
            )
        )
        return int(result.scalar_one())

    async def stats_per_master(self) -> list[dict]:
        """Har bir usta bo'yicha: qabul qilingan va tayyorlangan buyurtmalar soni."""
        created = dict(
            (
                await self.session.execute(
                    select(Order.created_by, func.count()).group_by(Order.created_by)
                )
            ).all()
        )
        completed = dict(
            (
                await self.session.execute(
                    select(Order.completed_by, func.count())
                    .where(Order.completed_by.is_not(None))
                    .group_by(Order.completed_by)
                )
            ).all()
        )
        users = (
            (await self.session.execute(select(User).order_by(User.created_at)))
            .scalars()
            .all()
        )
        return [
            {
                "name": u.full_name,
                "created": created.get(u.id, 0),
                "completed": completed.get(u.id, 0),
            }
            for u in users
        ]
