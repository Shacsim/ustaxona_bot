"""Global error handler — bot hech qachon yiqilib qolmasligi kerak."""

import logging

from aiogram import Router
from aiogram.types import ErrorEvent

logger = logging.getLogger(__name__)
router = Router(name="errors")

USER_ERROR_TEXT = (
    "⚠️ Kutilmagan xatolik yuz berdi.\n\n"
    "Iltimos, qaytadan urinib ko'ring. Muammo takrorlansa, administratorga ayting."
)


@router.errors()
async def global_error_handler(event: ErrorEvent) -> bool:
    logger.exception("Unhandled error: %s", event.exception)

    # Foydalanuvchiga muloyim xabar berishga harakat qilamiz
    try:
        if event.update.message is not None:
            await event.update.message.answer(USER_ERROR_TEXT)
        elif event.update.callback_query is not None:
            await event.update.callback_query.answer(
                "⚠️ Xatolik yuz berdi. Qaytadan urinib ko'ring.", show_alert=True
            )
    except Exception:  # noqa: BLE001 — xabar berish ham muvaffaqiyatsiz bo'lsa, jim log
        logger.exception("Failed to notify user about the error")
    return True
