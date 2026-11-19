"""Usta ombori: mahsulotlar va kirim/sotuv harakatlari."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base


class MoveKind(StrEnum):
    IN = "in"  # sotib olindi (kirim)
    OUT = "out"  # sotildi


class Product(Base):
    """Bitta ustaning omboridagi mahsulot turi (har bir usta — o'z ombori)."""

    __tablename__ = "products"
    __table_args__ = (UniqueConstraint("owner_id", "name_key", name="uq_products_owner_name"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Takrorlanmaslik uchun kichik harfdagi nom
    name_key: Mapped[str] = mapped_column(String(100), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # O'rtacha tannarx (bir dona, so'm) — foydani hisoblash uchun
    avg_cost: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    def __repr__(self) -> str:
        return f"<Product {self.name!r} qty={self.quantity}>"


class StockMove(Base):
    """Ombor harakati: kirim (sotib olindi) yoki sotuv — sana-vaqti bilan."""

    __tablename__ = "stock_moves"

    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False
    )
    kind: Mapped[str] = mapped_column(String(8), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[int] = mapped_column(BigInteger, nullable=False)
    # Sotuvda: o'sha paytdagi o'rtacha tannarx (foyda = (narx - tannarx) * soni)
    unit_cost: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )

    product: Mapped[Product] = relationship(lazy="joined")

    @property
    def total(self) -> int:
        return self.quantity * self.unit_price

    @property
    def profit(self) -> int:
        if self.kind != MoveKind.OUT or self.unit_cost is None:
            return 0
        return (self.unit_price - self.unit_cost) * self.quantity


class BotState(Base):
    """Kichik kalit-qiymat jadvali: rejalashtirilgan ishlarning oxirgi bajarilgan sanasi."""

    __tablename__ = "bot_state"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
