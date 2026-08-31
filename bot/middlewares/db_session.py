"""Har bir update uchun DB sessiya ochadi va foydalanuvchini yuklaydi."""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from database.repositories import UserRepository


class DbSessionMiddleware(BaseMiddleware):
    """data['session'] ga AsyncSession qo'shadi."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self.session_factory = session_factory

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with self.session_factory() as session:
            data["session"] = session
            return await handler(event, data)


class UserLoaderMiddleware(BaseMiddleware):
    """data['user'] ga bazadagi User obyektini qo'shadi (bo'lmasa None)."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        data["user"] = None
        tg_user = data.get("event_from_user")
        session = data.get("session")
        if tg_user is not None and session is not None:
            data["user"] = await UserRepository(session).get_by_telegram_id(tg_user.id)
        return await handler(event, data)
