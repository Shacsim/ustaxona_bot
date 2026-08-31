"""Mijozlar uchun anonim savol berish oqimi.

Mijoz botga savol yozadi → bot uni guruhning «Savol-javoblar» topic'iga
ANONIM e'lon qiladi (mijoz ismi ko'rinmaydi) → usta guruhda o'sha xabarga
reply qilib javob beradi → bot javobni mijozga shaxsiy yetkazadi
(qarang: group_tools.py dagi relay).
"""

import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.reply import cancel_kb, customer_menu, master_menu
from bot.states import CustomerStates
from bot.utils.i18n import btn_variants, t
from config import settings
from database.models import User
from database.repositories import QuestionRepository

logger = logging.getLogger(__name__)
router = Router(name="customer")
router.message.filter(F.chat.type == "private")


def _lang_of(user: User | None, data: dict) -> str:
    if user is not None:
        return user.language
    return data.get("language", "uz")


def _menu_for(user: User | None, lang: str):
    if user is not None:
        return master_menu(user.language, user.is_admin)
    return customer_menu(lang)


def question_group_text(question_id: int, lang: str, text: str) -> str:
    flag = "🇺🇿" if lang == "uz" else "🇷🇺"
    return (
        f"❓ <b>ANONIM SAVOL #{question_id}</b> {flag}\n\n"
        f"{escape(text)}\n\n"
        "<i>Javob berish uchun shu xabarga reply qiling — javob "
        "so'rovchiga botda yetkaziladi.\n"
        "Чтобы ответить, сделайте reply на это сообщение — ответ "
        "дойдёт до клиента в боте.</i>"
    )


@router.message(StateFilter(None), F.text.in_(btn_variants("ask_question")))
async def start_question(
    message: Message, state: FSMContext, user: User | None
) -> None:
    data = await state.get_data()
    lang = _lang_of(user, data)
    await state.set_state(CustomerStates.waiting_question)
    await message.answer(t("ask_question_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(CustomerStates.waiting_question, F.text.in_(btn_variants("cancel")))
async def cancel_question(
    message: Message, state: FSMContext, user: User | None
) -> None:
    data = await state.get_data()
    lang = _lang_of(user, data)
    await state.set_state(None)  # tilni saqlab, holatni tozalaymiz
    await message.answer(t("cancelled", lang), reply_markup=_menu_for(user, lang))


@router.message(CustomerStates.waiting_question, F.text)
async def process_question(
    message: Message,
    state: FSMContext,
    session,
    user: User | None,
    bot: Bot,
) -> None:
    data = await state.get_data()
    lang = _lang_of(user, data)

    text = (message.text or "").strip()
    if text in btn_variants("ask_question"):
        await message.answer(t("ask_question_prompt", lang))
        return
    if not (5 <= len(text) <= 1000):
        await message.answer(t("question_invalid", lang))
        return

    if settings.group_id is None or settings.faq_topic_id is None:
        await message.answer(t("question_send_failed", lang))
        return

    repo = QuestionRepository(session)
    question = await repo.create(
        asker_id=message.from_user.id, language=lang, text=text
    )
    try:
        group_msg = await bot.send_message(
            chat_id=settings.group_id,
            message_thread_id=settings.faq_topic_id,
            text=question_group_text(question.id, lang, text),
        )
    except TelegramAPIError as e:
        logger.error("Anonim savolni guruhga yuborib bo'lmadi: %s", e)
        await state.set_state(None)
        await message.answer(
            t("question_send_failed", lang), reply_markup=_menu_for(user, lang)
        )
        return

    await repo.set_group_message_id(question.id, group_msg.message_id)
    logger.info("Anonymous question #%s posted to group", question.id)

    await state.set_state(None)
    await message.answer(t("question_sent", lang), reply_markup=_menu_for(user, lang))
