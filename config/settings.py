"""Loyiha sozlamalari — barchasi .env faylidan o'qiladi.

Majburiy qiymatlar yetishmasa, bot ishga tushishda aniq xabar bilan to'xtaydi.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _int_or_none(value: str) -> int | None:
    value = value.strip()
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_admin_ids(raw: str) -> set[int]:
    ids: set[int] = set()
    for part in raw.replace(";", ",").split(","):
        part = part.strip()
        if part:
            try:
                ids.add(int(part))
            except ValueError:
                continue
    return ids


@dataclass(frozen=True)
class Settings:
    bot_token: str = os.getenv("BOT_TOKEN", "").strip()
    database_url: str = os.getenv("DATABASE_URL", "").strip()

    group_id: int | None = _int_or_none(os.getenv("GROUP_ID", ""))
    pending_topic_id: int | None = _int_or_none(os.getenv("PENDING_TOPIC_ID", ""))
    ready_topic_id: int | None = _int_or_none(os.getenv("READY_TOPIC_ID", ""))
    about_topic_id: int | None = _int_or_none(os.getenv("ABOUT_TOPIC_ID", ""))
    faq_topic_id: int | None = _int_or_none(os.getenv("FAQ_TOPIC_ID", ""))

    admin_ids: set[int] = field(
        default_factory=lambda: _parse_admin_ids(os.getenv("ADMIN_IDS", ""))
    )

    workshop_name: str = os.getenv("WORKSHOP_NAME", "KOMPYUTER SERVISI").strip()
    workshop_phone: str = os.getenv("WORKSHOP_PHONE", "").strip()
    workshop_address: str = os.getenv("WORKSHOP_ADDRESS", "").strip()
    workshop_working_hours: str = os.getenv("WORKSHOP_WORKING_HOURS", "").strip()
    workshop_lat: str = os.getenv("WORKSHOP_LAT", "").strip()
    workshop_lon: str = os.getenv("WORKSHOP_LON", "").strip()

    def validate(self) -> list[str]:
        """Majburiy sozlamalarni tekshiradi, xatolar ro'yxatini qaytaradi."""
        errors: list[str] = []
        if not self.bot_token:
            errors.append("BOT_TOKEN kiritilmagan (.env faylini tekshiring).")
        if not self.database_url:
            errors.append("DATABASE_URL kiritilmagan (.env faylini tekshiring).")
        if not self.admin_ids:
            errors.append("ADMIN_IDS bo'sh — kamida bitta asosiy admin ID kiriting.")
        return errors

    def group_configured(self) -> bool:
        return all(
            v is not None
            for v in (
                self.group_id,
                self.pending_topic_id,
                self.ready_topic_id,
            )
        )


settings = Settings()
