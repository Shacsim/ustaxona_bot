"""Buyurtma modeli."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base
from database.models.user import User


class OrderStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    CANCELLED = "cancelled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[int] = mapped_column(
        Integer, unique=True, index=True, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(16), nullable=False, default=OrderStatus.PENDING, index=True
    )

    customer_name: Mapped[str | None] = mapped_column(String(100))
    customer_phone: Mapped[str | None] = mapped_column(String(32))
    description: Mapped[str | None] = mapped_column(Text)

    work_done: Mapped[str | None] = mapped_column(Text)
    price: Mapped[int | None] = mapped_column(BigInteger)

    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    completed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    pending_message_id: Mapped[int | None] = mapped_column(BigInteger)
    ready_message_id: Mapped[int | None] = mapped_column(BigInteger)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    creator: Mapped[User] = relationship(foreign_keys=[created_by], lazy="joined")
    completer: Mapped[User | None] = relationship(
        foreign_keys=[completed_by], lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<Order #{self.order_number} status={self.status}>"
