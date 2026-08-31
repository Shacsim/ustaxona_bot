"""Foydalanuvchi (usta/admin) modeli."""

from datetime import datetime
from enum import StrEnum

from sqlalchemy import BigInteger, Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class UserRole(StrEnum):
    ADMIN = "admin"
    MASTER = "master"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str | None] = mapped_column(String(64))
    role: Mapped[str] = mapped_column(
        String(16), nullable=False, default=UserRole.MASTER
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN

    def __repr__(self) -> str:  # log uchun; sensitive maydonlar yo'q
        return f"<User id={self.id} tg={self.telegram_id} role={self.role}>"
