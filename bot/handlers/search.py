"""Buyurtmani raqam bo'yicha qidirish (ikki tilda)."""

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.reply import cancel_kb, master_menu
from bot.states import SearchStates
from bot.utils.formatters import order_card
from bot.utils.i18n import btn_variants, t
from bot.utils.validators import parse_order_number
from database.models import User
from database.repositories import OrderRepository

router = Router(name="search")


@router.message(StateFilter(None), F.text.in_(btn_variants("search")))
async def start_search(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.set_state(SearchStates.waiting_order_number)
    await message.answer(t("search_prompt", lang), reply_markup=cancel_kb(lang))


@router.message(SearchStates.waiting_order_number, F.text)
async def process_search(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    lang = user.language
    number = parse_order_number(message.text or "")
    if number is None:
        await message.answer(t("invalid_number", lang))
        return
    order = await OrderRepository(session).get_by_number(number)
    if order is None:
        await message.answer(t("search_not_found", lang, n=number))
        return
    await state.clear()
    await message.answer(
        order_card(order, lang), reply_markup=master_menu(lang, user.is_admin)
    )
