"""Anonim savol modeli: mijoz ↔ guruh xabari bog'lanishi."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import Base


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Savol beruvchining Telegram ID'si — guruhga chiqmaydi, faqat javobni
    # qaytarish uchun saqlanadi
    asker_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    language: Mapped[str] = mapped_column(String(2), nullable=False, default="uz")
    text: Mapped[str] = mapped_column(Text, nullable=False)
    group_message_id: Mapped[int | None] = mapped_column(
        BigInteger, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
