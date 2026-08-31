"""Yangi buyurtma yaratish oqimi (FSM).

➕ Yangi buyurtma → raqam (bot keyingisini taklif qiladi) → tasdiqlash →
guruhdagi «Kutayotgan buyurtmalar» topic'iga e'lon.
"""

import logging

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import confirm_new_order_kb, suggested_number_kb
from bot.keyboards.reply import BTN_NEW_ORDER, cancel_kb, master_menu
from bot.services import group_publisher
from bot.states import NewOrderStates
from bot.utils.validators import parse_order_number
from database.models import User
from database.repositories import OrderRepository

logger = logging.getLogger(__name__)
router = Router(name="new_order")


@router.message(StateFilter(None), F.text == BTN_NEW_ORDER)
async def start_new_order(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    next_number = await OrderRepository(session).next_number()
    await state.set_state(NewOrderStates.waiting_order_number)
    await message.answer(
        "📥 <b>Yangi buyurtma</b>\n\n"
        "Buyurtma raqamini kiriting:\n\n"
        f"Keyingi buyurtma raqami: <b>#{next_number}</b>",
        reply_markup=cancel_kb(),
    )
    await message.answer(
        "Yoki taklif qilingan raqamni oling:",
        reply_markup=suggested_number_kb(next_number),
    )


async def _ask_confirmation(
    target_message: Message, state: FSMContext, number: int
) -> None:
    await state.update_data(order_number=number)
    await state.set_state(NewOrderStates.confirming_order)
    await target_message.answer(
        f"Mijoz uchun buyurtma raqami: <b>#{number}</b>\n\n"
        "Buyurtma qabul qilinsinmi?",
        reply_markup=confirm_new_order_kb(),
    )


@router.callback_query(
    NewOrderStates.waiting_order_number, F.data.startswith("neworder:suggest:")
)
async def use_suggested_number(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
) -> None:
    number = int(callback.data.split(":")[2])
    existing = await OrderRepository(session).get_by_number(number)
    if existing is not None:
        # Taklif eskirgan bo'lishi mumkin — yangisini beramiz
        fresh = await OrderRepository(session).next_number()
        await callback.message.edit_reply_markup(
            reply_markup=suggested_number_kb(fresh)
        )
        await callback.answer(f"#{number} band. Yangi taklif: #{fresh}")
        return
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=None)
    await _ask_confirmation(callback.message, state, number)


@router.message(NewOrderStates.waiting_order_number, F.text)
async def process_order_number(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    number = parse_order_number(message.text or "")
    if number is None:
        await message.answer(
            "❌ Buyurtma raqami faqat raqamlardan iborat bo'lishi kerak.\n\n"
            "Masalan: <b>27</b>"
        )
        return
    existing = await OrderRepository(session).get_by_number(number)
    if existing is not None:
        await message.answer(
            f"❌ <b>#{number}</b> raqamli buyurtma allaqachon mavjud "
            f"(holati: {existing.status}).\n\n"
            "Boshqa raqam kiriting:"
        )
        return
    await _ask_confirmation(message, state, number)


@router.callback_query(NewOrderStates.confirming_order, F.data == "neworder:confirm")
async def confirm_order(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    bot: Bot,
) -> None:
    data = await state.get_data()
    number: int = data["order_number"]
    repo = OrderRepository(session)

    # Poyga holati: tasdiqlash orasida boshqa usta shu raqamni olgan bo'lishi mumkin
    if await repo.get_by_number(number) is not None:
        await state.clear()
        await callback.message.edit_text(
            f"❌ <b>#{number}</b> raqami hozirgina band qilindi. Qaytadan urinib ko'ring."
        )
        await callback.answer()
        return

    order = await repo.create(order_number=number, created_by=user.id)
    logger.info("Order #%s created by %s", number, user.full_name)

    message_id = await group_publisher.publish_pending(bot, order)
    if message_id is not None:
        await repo.set_pending_message_id(order.id, message_id)
        group_note = "📤 Guruhdagi «Kutayotgan buyurtmalar» bo'limiga e'lon yuborildi."
    else:
        group_note = (
            "⚠️ Guruhga e'lon yuborib bo'lmadi (guruh sozlamalarini tekshiring). "
            "Buyurtma bazaga saqlandi."
        )

    await state.clear()
    await callback.message.edit_text(
        f"✅ Buyurtma <b>#{number}</b> qabul qilindi!\n\n{group_note}"
    )
    await callback.message.answer(
        "Davom etamiz 👇", reply_markup=master_menu(user.is_admin)
    )
    await callback.answer()


@router.callback_query(NewOrderStates.confirming_order, F.data == "neworder:cancel")
async def cancel_order_creation(
    callback: CallbackQuery, state: FSMContext, user: User
) -> None:
    await state.clear()
    await callback.message.edit_text("❌ Buyurtma yaratish bekor qilindi.")
    await callback.message.answer(
        "Menyu 👇", reply_markup=master_menu(user.is_admin)
    )
    await callback.answer()
