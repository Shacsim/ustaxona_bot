"""Buyurtmani tayyor qilish oqimi (FSM).

🛠 Tayyor qilish → raqam → bajarilgan ishlar → xizmat haqqi → tasdiqlash →
«Tayyor buyurtmalar» topic'iga e'lon + eski «kutayotgan» xabar yangilanadi.
"""

import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import confirm_complete_kb
from bot.keyboards.reply import BTN_COMPLETE, cancel_kb, master_menu
from bot.services import group_publisher
from bot.states import CompleteOrderStates
from bot.utils.formatters import fmt_price, fmt_work_done
from bot.utils.validators import parse_order_number, parse_price
from database.models import OrderStatus, User
from database.repositories import OrderRepository

logger = logging.getLogger(__name__)
router = Router(name="complete_order")


@router.message(StateFilter(None), F.text == BTN_COMPLETE)
async def start_complete(message: Message, state: FSMContext) -> None:
    await state.set_state(CompleteOrderStates.waiting_order_number)
    await message.answer(
        "🔢 Tayyor bo'lgan buyurtma raqamini kiriting:",
        reply_markup=cancel_kb(),
    )


@router.message(CompleteOrderStates.waiting_order_number, F.text)
async def process_number(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    number = parse_order_number(message.text or "")
    if number is None:
        await message.answer(
            "❌ Buyurtma raqami faqat raqamlardan iborat bo'lishi kerak.\n\n"
            "Masalan: <b>27</b>"
        )
        return
    order = await OrderRepository(session).get_by_number(number)
    if order is None:
        await message.answer(
            f"❌ <b>#{number}</b> raqamli buyurtma topilmadi.\n\n"
            "Iltimos, buyurtma raqamini tekshirib qayta kiriting."
        )
        return
    if order.status == OrderStatus.READY:
        await message.answer(
            f"ℹ️ <b>#{number}</b> raqamli buyurtma allaqachon tayyor deb belgilangan."
        )
        return
    if order.status == OrderStatus.CANCELLED:
        await message.answer(
            f"ℹ️ <b>#{number}</b> raqamli buyurtma bekor qilingan."
        )
        return
    await state.update_data(order_id=order.id, order_number=number)
    await state.set_state(CompleteOrderStates.waiting_work_description)
    await message.answer(
        f"🔧 <b>Buyurtma #{number}</b>\n\n"
        "Qanday ishlar bajarildi?\n\n"
        "Bajarilgan ishlarni batafsil yozing (har birini yangi qatordan):"
    )


@router.message(CompleteOrderStates.waiting_work_description, F.text)
async def process_work(message: Message, state: FSMContext) -> None:
    work = (message.text or "").strip()
    if len(work) < 3:
        await message.answer(
            "❌ Bajarilgan ishlar tavsifi juda qisqa. Batafsilroq yozing:"
        )
        return
    if len(work) > 2000:
        await message.answer("❌ Tavsif juda uzun (maksimum 2000 belgi). Qisqartiring:")
        return
    await state.update_data(work_done=work)
    await state.set_state(CompleteOrderStates.waiting_price)
    await message.answer(
        "💰 Xizmat haqqini kiriting:\n\nMasalan:\n<b>250000</b>"
    )


@router.message(CompleteOrderStates.waiting_price, F.text)
async def process_price(message: Message, state: FSMContext) -> None:
    price = parse_price(message.text or "")
    if price is None:
        await message.answer(
            "❌ Iltimos, summani faqat raqam bilan kiriting.\n\n"
            "Masalan:\n<b>250000</b>"
        )
        return
    data = await state.update_data(price=price)
    await state.set_state(CompleteOrderStates.confirming)
    await message.answer(
        f"📋 <b>Buyurtma #{data['order_number']}</b>\n\n"
        "🔧 <b>Bajarilgan ishlar:</b>\n"
        f"{fmt_work_done(data['work_done'])}\n\n"
        f"💰 Xizmat haqqi: <b>{fmt_price(price)}</b>\n\n"
        "Buyurtma tayyormi?",
        reply_markup=confirm_complete_kb(),
    )


@router.callback_query(CompleteOrderStates.confirming, F.data == "complete:confirm")
async def confirm_complete(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    bot: Bot,
) -> None:
    data = await state.get_data()
    repo = OrderRepository(session)

    order = await repo.mark_ready(
        order_id=data["order_id"],
        work_done=data["work_done"],
        price=data["price"],
        completed_by=user.id,
        ready_message_id=None,
    )
    if order is None:
        await state.clear()
        await callback.message.edit_text("❌ Buyurtma topilmadi. Qaytadan urinib ko'ring.")
        await callback.answer()
        return

    logger.info("Order #%s marked as ready by %s", order.order_number, user.full_name)

    ready_msg_id = await group_publisher.publish_ready(bot, order)
    if ready_msg_id is not None:
        order.ready_message_id = ready_msg_id
        await session.commit()
        await group_publisher.update_pending_as_done(bot, order)
        group_note = "📤 Guruhdagi «Tayyor buyurtmalar» bo'limiga e'lon yuborildi."
    else:
        group_note = (
            "⚠️ Guruhga e'lon yuborib bo'lmadi (guruh sozlamalarini tekshiring). "
            "Buyurtma bazada TAYYOR deb belgilandi."
        )

    await state.clear()
    await callback.message.edit_text(
        f"✅ Buyurtma <b>#{order.order_number}</b> tayyor deb belgilandi!\n\n"
        f"{group_note}"
    )
    await callback.message.answer(
        "Davom etamiz 👇", reply_markup=master_menu(user.is_admin)
    )
    await callback.answer()


@router.callback_query(CompleteOrderStates.confirming, F.data == "complete:cancel")
async def cancel_complete(
    callback: CallbackQuery, state: FSMContext, user: User
) -> None:
    await state.clear()
    await callback.message.edit_text("❌ Amal bekor qilindi. Buyurtma o'zgartirilmadi.")
    await callback.message.answer(
        "Menyu 👇", reply_markup=master_menu(user.is_admin)
    )
    await callback.answer()
