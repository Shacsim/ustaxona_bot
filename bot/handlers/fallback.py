"""Hech qaysi handler'ga tushmagan shaxsiy xabarlar uchun oxirgi qatlam."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.reply import BTN_CANCEL, master_menu
from bot.middlewares.auth import DENIED_TEXT, INACTIVE_TEXT
from database.models import User

router = Router(name="fallback")
router.message.filter(F.chat.type == "private")


@router.message(Command("post_about", "close_topics", "groupid", "topicid"))
async def group_only_command(message: Message) -> None:
    await message.answer(
        "ℹ️ Bu buyruq faqat guruhda ishlaydi.\n\n"
        "Uni guruh ichida (kerak bo'lsa tegishli topic ichida) yozing."
    )


@router.message()
async def unknown_message(
    message: Message, state: FSMContext, user: User | None
) -> None:
    if user is None:
        await message.answer(DENIED_TEXT + "\n\nRo'yxatdan o'tish uchun: /start")
        return
    if not user.is_active:
        await message.answer(INACTIVE_TEXT)
        return
    if await state.get_state() is not None:
        await message.answer(
            "Iltimos, so'ralgan ma'lumotni matn ko'rinishida yuboring "
            f"yoki «{BTN_CANCEL}» tugmasini bosing."
        )
        return
    await message.answer(
        "Quyidagi menyudan foydalaning 👇", reply_markup=master_menu(user.is_admin)
    )
