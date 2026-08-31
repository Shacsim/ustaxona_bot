"""Buyurtmani raqam bo'yicha qidirish."""

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.reply import BTN_SEARCH, cancel_kb, master_menu
from bot.states import SearchStates
from bot.utils.formatters import order_card
from bot.utils.validators import parse_order_number
from database.models import User
from database.repositories import OrderRepository

router = Router(name="search")


@router.message(StateFilter(None), F.text == BTN_SEARCH)
async def start_search(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchStates.waiting_order_number)
    await message.answer("🔎 Buyurtma raqamini kiriting:", reply_markup=cancel_kb())


@router.message(SearchStates.waiting_order_number, F.text)
async def process_search(
    message: Message, state: FSMContext, session: AsyncSession, user: User
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
            "Boshqa raqam kiriting yoki bekor qiling."
        )
        return
    await state.clear()
    await message.answer(order_card(order), reply_markup=master_menu(user.is_admin))
