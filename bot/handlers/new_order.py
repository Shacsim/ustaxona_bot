"""Yangi buyurtma yaratish oqimi (FSM).

➕ Yangi buyurtma → mijoz telefon raqami → mijoz ismi → nima qilish kerak →
avtomatik raqam bilan tasdiqlash → guruhdagi «Kutayotgan buyurtmalar»
topic'iga e'lon.

Telefon uch xil yo'l bilan kiritiladi:
  • «📱 Raqamni terish» — Mini App, telefonning sonli klaviaturasi ochiladi;
  • oddiy matn (901234567, +998 90 123 45 67 ...);
  • kontakt ulashish (📎 → Kontakt) — ism ham taklif qilinadi.
Raqam bazada bo'lsa, mijozning oldingi ismi tugma sifatida taklif qilinadi.

Buyurtma raqami avtomatik beriladi (navbatdagi bo'sh raqam).
Mijoz telefon raqami guruhga chiqarilmaydi — faqat bazada saqlanadi.
"""

import json
import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import confirm_new_order_kb
from bot.keyboards.reply import cancel_kb, master_menu, phone_kb, suggest_kb
from bot.services import group_publisher
from bot.states import NewOrderStates
from bot.utils.i18n import btn_variants, t
from bot.utils.validators import parse_phone, valid_description, valid_name
from database.models import User
from database.repositories import OrderRepository

logger = logging.getLogger(__name__)
router = Router(name="new_order")


@router.message(StateFilter(None), F.text.in_(btn_variants("new_order")))
async def start_new_order(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.set_state(NewOrderStates.waiting_customer_phone)
    await message.answer(t("ask_customer_phone", lang), reply_markup=phone_kb(lang))


async def _accept_phone(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    raw_phone: str,
    contact_name: str | None = None,
) -> None:
    lang = user.language
    phone = parse_phone(raw_phone)
    if phone is None:
        await message.answer(t("invalid_phone", lang), reply_markup=phone_kb(lang))
        return
    await state.update_data(customer_phone=phone)
    await state.set_state(NewOrderStates.waiting_customer_name)

    text = t("ask_customer_name", lang, phone=escape(phone))
    known_name, count = await OrderRepository(session).known_customer(phone)
    suggestion = valid_name(known_name or "") or valid_name(contact_name or "")
    if known_name and suggestion:
        text += "\n\n" + t("customer_known", lang, name=escape(suggestion), count=count)
    elif suggestion:
        text += "\n\n" + t("contact_name_hint", lang, name=escape(suggestion))
    markup = suggest_kb(suggestion, lang) if suggestion else cancel_kb(lang)
    await message.answer(text, reply_markup=markup)


@router.message(NewOrderStates.waiting_customer_phone, F.web_app_data)
async def phone_from_webapp(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    raw = message.web_app_data.data or ""
    try:  # Mini App {"phone": "..."} yuboradi; oddiy satr ham qabul qilinadi
        raw = str(json.loads(raw).get("phone", ""))
    except (ValueError, AttributeError):
        pass
    await _accept_phone(message, state, session, user, raw)


@router.message(NewOrderStates.waiting_customer_phone, F.contact)
async def phone_from_contact(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    c = message.contact
    name = " ".join(x for x in (c.first_name, c.last_name) if x)
    await _accept_phone(message, state, session, user, c.phone_number, contact_name=name)


@router.message(NewOrderStates.waiting_customer_phone, F.text)
async def phone_from_text(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    await _accept_phone(message, state, session, user, message.text or "")


@router.message(NewOrderStates.waiting_customer_name, F.text)
async def process_customer_name(message: Message, state: FSMContext, user: User) -> None:
    lang = user.language
    name = valid_name(message.text or "")
    if name is None:
        await message.answer(t("invalid_customer_name", lang))
        return
    await state.update_data(customer_name=name)
    await state.set_state(NewOrderStates.waiting_description)
    await message.answer(t("ask_description", lang), reply_markup=cancel_kb(lang))


@router.message(NewOrderStates.waiting_description, F.text)
async def process_description(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    lang = user.language
    description = valid_description(message.text or "")
    if description is None:
        await message.answer(t("invalid_description", lang))
        return

    # Raqam avtomatik: navbatdagi bo'sh raqam
    number = await OrderRepository(session).next_number()
    data = await state.update_data(description=description, order_number=number)
    await state.set_state(NewOrderStates.confirming_order)
    await message.answer(
        t(
            "order_summary",
            lang,
            n=number,
            phone=escape(data["customer_phone"]),
            name=escape(data["customer_name"]),
            task=escape(description),
        ),
        reply_markup=confirm_new_order_kb(lang),
    )


@router.callback_query(NewOrderStates.confirming_order, F.data == "neworder:confirm")
async def confirm_order(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
    bot: Bot,
) -> None:
    lang = user.language
    data = await state.get_data()
    repo = OrderRepository(session)

    # Poyga holati: tasdiqlash orasida boshqa usta buyurtma yaratgan bo'lishi
    # mumkin — raqam band bo'lsa, avtomatik ravishda yangisini olamiz.
    number: int = data["order_number"]
    if await repo.get_by_number(number) is not None:
        number = await repo.next_number()

    order = await repo.create(
        order_number=number,
        created_by=user.id,
        customer_name=data["customer_name"],
        customer_phone=data["customer_phone"],
        description=data["description"],
    )
    logger.info("Order #%s created by %s", number, user.full_name)

    message_id = await group_publisher.publish_pending(bot, order)
    if message_id is not None:
        await repo.set_pending_message_id(order.id, message_id)
        note = t("group_sent_pending", lang)
    else:
        note = t("group_send_failed", lang)

    await state.clear()
    await callback.message.edit_text(t("order_created", lang, n=number, note=note))
    await callback.message.answer(
        t("continue", lang), reply_markup=master_menu(lang, user.is_admin)
    )
    await callback.answer()


@router.callback_query(NewOrderStates.confirming_order, F.data == "neworder:cancel")
async def cancel_order_creation(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.clear()
    await callback.message.edit_text(t("order_create_cancelled", lang))
    await callback.message.answer(
        t("use_menu", lang), reply_markup=master_menu(lang, user.is_admin)
    )
    await callback.answer()
