"""Ro'yxatdan o'tish: /start → ism → (admin tasdig'i) → menyu.

ADMIN_IDS dagi foydalanuvchilar ro'yxatdan o'tishi bilan faol ADMIN bo'ladi.
Boshqalar MASTER sifatida yoziladi, lekin admin tasdiqlaguncha nofaol turadi.
"""

import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import approve_master_kb
from bot.keyboards.reply import master_menu
from bot.states import RegistrationStates
from bot.utils.validators import valid_name
from config import settings
from database.models import User, UserRole
from database.repositories import UserRepository

logger = logging.getLogger(__name__)
router = Router(name="registration")
router.message.filter(F.chat.type == "private")

WELCOME_TEXT = (
    "Assalomu alaykum!\n\n"
    "Kompyuter servis boshqaruv botiga xush kelibsiz.\n\n"
    "Avval tizimda ro'yxatdan o'tishingiz kerak.\n\n"
    "Iltimos, ismingizni kiriting:"
)


@router.message(CommandStart())
async def cmd_start(
    message: Message, state: FSMContext, user: User | None
) -> None:
    await state.clear()
    if user is not None:
        if user.is_active:
            await message.answer(
                f"Xush kelibsiz, <b>{escape(user.full_name)}</b>! 👋",
                reply_markup=master_menu(user.is_admin),
            )
        else:
            await message.answer(
                "⏳ Profilingiz administrator tasdig'ini kutmoqda.\n"
                "Tasdiqlangach sizga xabar beramiz."
            )
        return
    await message.answer(WELCOME_TEXT, reply_markup=ReplyKeyboardRemove())
    await state.set_state(RegistrationStates.waiting_name)


@router.message(RegistrationStates.waiting_name, F.text)
async def process_name(
    message: Message, state: FSMContext, session: AsyncSession, bot: Bot
) -> None:
    name = valid_name(message.text or "")
    if name is None:
        await message.answer(
            "❌ Ism 2 tadan 50 tagacha belgidan iborat bo'lishi kerak.\n"
            "Iltimos, qayta kiriting:"
        )
        return

    repo = UserRepository(session)
    # Ikki marta /start bosib qayta ro'yxatdan o'tishga urinish
    if await repo.get_by_telegram_id(message.from_user.id) is not None:
        await state.clear()
        await message.answer("Siz allaqachon ro'yxatdan o'tgansiz.")
        return

    is_bootstrap_admin = message.from_user.id in settings.admin_ids
    new_user = await repo.create(
        telegram_id=message.from_user.id,
        full_name=name,
        username=message.from_user.username,
        role=UserRole.ADMIN if is_bootstrap_admin else UserRole.MASTER,
        is_active=is_bootstrap_admin,
    )
    await state.clear()
    logger.info(
        "User %s registered as %s (role=%s, active=%s)",
        message.from_user.id,
        name,
        new_user.role,
        new_user.is_active,
    )

    if is_bootstrap_admin:
        await message.answer(
            f"✅ Xush kelibsiz, <b>{escape(name)}</b>!\n\n"
            "Siz <b>administrator</b> sifatida ro'yxatdan o'tdingiz.",
            reply_markup=master_menu(is_admin=True),
        )
        return

    await message.answer(
        f"✅ Rahmat, <b>{escape(name)}</b>!\n\n"
        "Ma'lumotlaringiz qabul qilindi.\n"
        "⏳ Administrator profilingizni tasdiqlagach, sizga xabar beramiz."
    )

    # Adminlarga tasdiqlash so'rovi yuboramiz
    admin_tg_ids = {a.telegram_id for a in await repo.list_active_admins()}
    admin_tg_ids |= settings.admin_ids
    notify_text = (
        "🆕 <b>Yangi usta ro'yxatdan o'tdi</b>\n\n"
        f"👤 Ism: <b>{escape(name)}</b>\n"
        f"🆔 Telegram ID: <code>{message.from_user.id}</code>\n"
        f"👤 Username: @{message.from_user.username or '—'}\n\n"
        "Tasdiqlaysizmi?"
    )
    for admin_id in admin_tg_ids:
        try:
            await bot.send_message(
                admin_id, notify_text, reply_markup=approve_master_kb(new_user.id)
            )
        except TelegramAPIError:
            logger.warning("Adminga (%s) xabar yuborib bo'lmadi", admin_id)
