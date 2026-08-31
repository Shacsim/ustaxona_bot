"""Buyurtmani tayyor qilish oqimi (FSM).

🛠 Tayyor qilish → raqam → bajarilgan ishlar → xizmat haqqi → tasdiqlash →
«Tayyor buyurtmalar» topic'iga e'lon + eski «kutayotgan» xabar yangilanadi.
"""

import logging

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import confirm_complete_kb
from bot.keyboards.reply import cancel_kb, master_menu
from bot.services import group_publisher
from bot.states import CompleteOrderStates
from bot.utils.formatters import fmt_price, fmt_work_done
from bot.utils.i18n import btn_variants, t
from bot.utils.validators import parse_order_number, parse_price
from database.models import OrderStatus, User
from database.repositories import OrderRepository

logger = logging.getLogger(__name__)
router = Router(name="complete_order")


@router.message(StateFilter(None), F.text.in_(btn_variants("complete")))
async def start_complete(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.set_state(CompleteOrderStates.waiting_order_number)
    await message.answer(t("ask_ready_number", lang), reply_markup=cancel_kb(lang))


@router.message(CompleteOrderStates.waiting_order_number, F.text)
async def process_number(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    lang = user.language
    number = parse_order_number(message.text or "")
    if number is None:
        await message.answer(t("invalid_number", lang))
        return
    order = await OrderRepository(session).get_by_number(number)
    if order is None:
        await message.answer(t("order_not_found", lang, n=number))
        return
    if order.status == OrderStatus.READY:
        await message.answer(t("already_ready", lang, n=number))
        return
    if order.status == OrderStatus.CANCELLED:
        await message.answer(t("was_cancelled", lang, n=number))
        return
    await state.update_data(order_id=order.id, order_number=number)
    await state.set_state(CompleteOrderStates.waiting_work_description)
    await message.answer(t("ask_work_done", lang, n=number))


@router.message(CompleteOrderStates.waiting_work_description, F.text)
async def process_work(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    work = (message.text or "").strip()
    if len(work) < 3:
        await message.answer(t("work_too_short", lang))
        return
    if len(work) > 2000:
        await message.answer(t("work_too_long", lang))
        return
    await state.update_data(work_done=work)
    await state.set_state(CompleteOrderStates.waiting_price)
    await message.answer(t("ask_price", lang))


@router.message(CompleteOrderStates.waiting_price, F.text)
async def process_price(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    price = parse_price(message.text or "")
    if price is None:
        await message.answer(t("invalid_price", lang))
        return
    data = await state.update_data(price=price)
    await state.set_state(CompleteOrderStates.confirming)
    await message.answer(
        t(
            "ready_summary",
            lang,
            n=data["order_number"],
            work=fmt_work_done(data["work_done"]),
            price=fmt_price(price),
        ),
        reply_markup=confirm_complete_kb(lang),
    )


@router.callback_query(CompleteOrderStates.confirming, F.data == "complete:confirm")
async def confirm_complete(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    bot: Bot,
) -> None:
    lang = user.language
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
        await callback.message.edit_text(t("order_vanished", lang))
        await callback.answer()
        return

    logger.info("Order #%s marked as ready by %s", order.order_number, user.full_name)

    ready_msg_id = await group_publisher.publish_ready(bot, order)
    if ready_msg_id is not None:
        order.ready_message_id = ready_msg_id
        await session.commit()
        await group_publisher.update_pending_as_done(bot, order)
        note = t("group_sent_ready", lang)
    else:
        note = t("group_send_failed_ready", lang)

    await state.clear()
    await callback.message.edit_text(
        t("ready_done", lang, n=order.order_number, note=note)
    )
    await callback.message.answer(
        t("continue", lang), reply_markup=master_menu(lang, user.is_admin)
    )
    await callback.answer()


@router.callback_query(CompleteOrderStates.confirming, F.data == "complete:cancel")
async def cancel_complete(
    callback: CallbackQuery, state: FSMContext, user: User
) -> None:
    lang = user.language
    await state.clear()
    await callback.message.edit_text(t("complete_cancelled", lang))
    await callback.message.answer(
        t("use_menu", lang), reply_markup=master_menu(lang, user.is_admin)
    )
    await callback.answer()
