"""Ro'yxatdan o'tish: /start → til tanlash → ism → (admin tasdig'i) → menyu.

/start har safar til tanlovini ko'rsatadi (uz/ru/en) — ro'yxatdan o'tgan usta
ham tilni istalgan payt almashtirishi mumkin.

ADMIN_IDS dagi foydalanuvchilar ro'yxatdan o'tishi bilan faol ADMIN bo'ladi.
Boshqalar MASTER sifatida yoziladi, lekin admin tasdiqlaguncha nofaol turadi.
"""

import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import approve_master_kb, language_kb, open_app_kb
from bot.keyboards.reply import master_menu
from bot.states import RegistrationStates
from bot.utils.i18n import LANG_NAMES, LANGS, t
from bot.utils.validators import valid_name
from config import settings
from database.models import User, UserRole
from database.repositories import UserRepository

logger = logging.getLogger(__name__)
router = Router(name="registration")
router.message.filter(F.chat.type == "private")


async def _offer_app(message: Message, lang: str) -> None:
    kb = open_app_kb(lang)
    if kb is not None:
        await message.answer(t("app_hint", lang), reply_markup=kb)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        t("choose_language", "uz"),
        reply_markup=language_kb(),
    )


@router.callback_query(F.data.startswith("lang:"))
async def choose_language(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User | None,
) -> None:
    lang = callback.data.split(":")[1]
    if lang not in LANGS:
        lang = "uz"
    await callback.answer()

    if user is not None:
        # Ro'yxatdan o'tgan foydalanuvchi tilni almashtirdi
        await UserRepository(session).set_language(user.id, lang)
        await callback.message.edit_text(t("lang_set", lang))
        if user.is_active:
            await callback.message.answer(
                t("welcome_back", lang, name=escape(user.full_name)),
                reply_markup=master_menu(lang, user.is_admin),
            )
            await _offer_app(callback.message, lang)
        else:
            await callback.message.answer(t("pending_approval", lang))
        return

    # Yangi foydalanuvchi — ism so'raymiz
    await state.update_data(language=lang)
    await state.set_state(RegistrationStates.waiting_name)
    await callback.message.edit_text(t("lang_set", lang))
    await callback.message.answer(
        t("reg_ask_name", lang), reply_markup=ReplyKeyboardRemove()
    )


@router.message(RegistrationStates.waiting_name, F.text)
async def process_name(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    data = await state.get_data()
    lang = data.get("language", "uz")

    name = valid_name(message.text or "")
    if name is None:
        await message.answer(t("reg_name_invalid", lang))
        return

    repo = UserRepository(session)
    # Ikki marta /start bosib qayta ro'yxatdan o'tishga urinish
    if await repo.get_by_telegram_id(message.from_user.id) is not None:
        await state.clear()
        await message.answer(t("reg_already", lang))
        return

    is_bootstrap_admin = message.from_user.id in settings.admin_ids
    new_user = await repo.create(
        telegram_id=message.from_user.id,
        full_name=name,
        username=message.from_user.username,
        role=UserRole.ADMIN if is_bootstrap_admin else UserRole.MASTER,
        is_active=is_bootstrap_admin,
        language=lang,
    )
    await state.clear()
    logger.info(
        "User %s registered as %s (role=%s, active=%s, lang=%s)",
        message.from_user.id,
        name,
        new_user.role,
        new_user.is_active,
        lang,
    )

    if is_bootstrap_admin:
        await message.answer(
            t("reg_admin_welcome", lang, name=escape(name)),
            reply_markup=master_menu(lang, is_admin=True),
        )
        await _offer_app(message, lang)
        return

    await message.answer(t("reg_wait_approval", lang, name=escape(name)))

    # Adminlarga tasdiqlash so'rovi — har biriga o'z tilida
    admins = {tg: "uz" for tg in settings.admin_ids}
    for a in await repo.list_active_admins():
        admins[a.telegram_id] = a.language
    for admin_id, admin_lang in admins.items():
        notify_text = t(
            "adm_new_master",
            admin_lang,
            name=escape(name),
            language=LANG_NAMES.get(lang, lang),
            tg_id=message.from_user.id,
            username=escape(message.from_user.username or "—"),
        )
        try:
            await bot.send_message(
                admin_id, notify_text, reply_markup=approve_master_kb(new_user.id, admin_lang)
            )
        except TelegramAPIError:
            logger.warning("Adminga (%s) xabar yuborib bo'lmadi", admin_id)
