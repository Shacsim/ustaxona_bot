"""Hech qaysi handler'ga tushmagan shaxsiy xabarlar uchun oxirgi qatlam."""

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.reply import customer_menu, master_menu
from bot.middlewares.auth import INACTIVE_TEXT
from bot.utils.i18n import t
from database.models import User

router = Router(name="fallback")
router.message.filter(F.chat.type == "private")


@router.message(Command("post_about", "close_topics", "groupid", "topicid"))
async def group_only_command(message: Message) -> None:
    await message.answer(
        "ℹ️ Bu buyruq faqat guruhda ishlaydi. / Эта команда работает только в группе.\n\n"
        "Uni guruh ichida (kerak bo'lsa tegishli topic ichida) yozing."
    )


@router.message()
async def unknown_message(
    message: Message, state: FSMContext, user: User | None
) -> None:
    if user is None:
        # Ro'yxatda yo'q — bu mijoz: savol berish menyusini ko'rsatamiz
        lang = (await state.get_data()).get("language", "uz")
        await message.answer(
            t("customer_welcome", lang), reply_markup=customer_menu(lang)
        )
        return
    lang = user.language
    if not user.is_active:
        await message.answer(INACTIVE_TEXT)
        return
    if await state.get_state() is not None:
        await message.answer(t("fsm_hint", lang))
        return
    await message.answer(
        t("use_menu", lang), reply_markup=master_menu(lang, user.is_admin)
    )
