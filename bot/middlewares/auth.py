"""Authorization middlewarelari.

AuthMiddleware — himoyalangan routerlarga faqat ro'yxatdan o'tgan va
faol foydalanuvchilarni o'tkazadi. Guruh xabarlariga aralashmaydi
(ular alohida group_guard routerida ko'riladi).

AdminOnlyMiddleware — faqat adminlar uchun.
"""

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

DENIED_TEXT = (
    "❌ Siz ushbu tizimdan foydalanish huquqiga ega emassiz.\n\n"
    "Administrator bilan bog'laning."
)
INACTIVE_TEXT = (
    "⏳ Profilingiz hali administrator tomonidan tasdiqlanmagan.\n\n"
    "Iltimos, tasdiqlanishini kuting."
)


def _is_private(event: TelegramObject) -> bool:
    if isinstance(event, Message):
        return event.chat.type == "private"
    if isinstance(event, CallbackQuery):
        return event.message is not None and event.message.chat.type == "private"
    return False


async def _deny(event: TelegramObject, text: str) -> None:
    if isinstance(event, Message):
        await event.answer(text)
    elif isinstance(event, CallbackQuery):
        await event.answer(text, show_alert=True)


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not _is_private(event):
            return None  # guruh xabarlari bu routerlarga tegishli emas
        user = data.get("user")
        if user is None:
            await _deny(event, DENIED_TEXT)
            return None
        if not user.is_active:
            await _deny(event, INACTIVE_TEXT)
            return None
        return await handler(event, data)


class AdminOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("user")
        if user is None or not user.is_active or not user.is_admin:
            await _deny(event, "❌ Bu bo'lim faqat adminlar uchun.")
            return None
        return await handler(event, data)
