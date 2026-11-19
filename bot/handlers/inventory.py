"""Usta ombori: 📦 Omborim.

Har bir usta o'z omboriga ega:
  📥 Sotib oldim — mahsulot tanlash yoki yangi nom → soni → bir dona narxi → tasdiq
  📤 Sotdim      — qoldig'i bor mahsulot → soni (qoldiqdan oshmaydi) → narx → tasdiq
  📦 Qoldiq, 🧾 Sotib olinganlar, 💸 Sotilganlar — sana-vaqti bilan ro'yxatlar
  📄 PDF hisobot — davr bo'yicha (daromad + sotuv + kirim + qoldiq)
  ↩️ Oxirgi yozuvni bekor qilish — xato kiritilganini tuzatish uchun
"""

import logging
from html import escape

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import BufferedInputFile, CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import (
    inventory_back_kb,
    inventory_confirm_kb,
    inventory_menu_kb,
    inventory_pdf_kb,
    product_pick_kb,
    undo_confirm_kb,
)
from bot.keyboards.reply import cancel_kb, master_menu
from bot.services import reports
from bot.states import InventoryStates
from bot.utils.formatters import fmt_dt, fmt_price, period_start
from bot.utils.i18n import btn_variants, t
from bot.utils.validators import parse_amount, parse_qty, valid_product_name
from database.models import MoveKind, StockMove, User
from database.repositories import InventoryRepository

logger = logging.getLogger(__name__)
router = Router(name="inventory")


async def _overview_text(session: AsyncSession, user: User) -> str:
    lang = user.language
    repo = InventoryRepository(session)
    kinds, units, value = await repo.stock_summary(user.id)
    today = await repo.totals(user.id, since=period_start("today"))
    return t(
        "inv_title",
        lang,
        kinds=kinds,
        units=units,
        value=fmt_price(value, lang),
        in_units=today.in_units,
        in_sum=fmt_price(today.in_sum, lang),
        out_units=today.out_units,
        out_sum=fmt_price(today.out_sum, lang),
        profit=fmt_price(today.profit, lang),
    )


async def _edit(callback: CallbackQuery, text: str, markup=None) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest:  # "message is not modified" va shu kabilar
        pass


def _move_line(m: StockMove, lang: str) -> str:
    line = (
        f"🕐 {fmt_dt(m.created_at)} — <b>{escape(m.product.name)}</b> × {m.quantity} — "
        f"{fmt_price(m.total, lang)}"
    )
    if m.kind == MoveKind.OUT:
        line += f" (📈 {fmt_price(m.profit, lang)})"
    return line


# ---------- Bosh sahifa ----------


@router.message(StateFilter(None), F.text.in_(btn_variants("inventory")))
async def open_inventory(message: Message, session: AsyncSession, user: User) -> None:
    await message.answer(
        await _overview_text(session, user), reply_markup=inventory_menu_kb(user.language)
    )


@router.callback_query(F.data == "inv:menu")
async def back_to_menu(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    await _edit(callback, await _overview_text(session, user), inventory_menu_kb(user.language))
    await callback.answer()


# ---------- Sotib oldim / Sotdim: mahsulot tanlash ----------


@router.callback_query(F.data == "inv:buy")
async def pick_for_buy(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User
) -> None:
    lang = user.language
    await state.clear()
    products = await InventoryRepository(session).list_products(user.id)
    await _edit(callback, t("inv_pick_buy", lang), product_pick_kb(products, "buy", lang, allow_new=True))
    await callback.answer()


@router.callback_query(F.data == "inv:sell")
async def pick_for_sell(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User
) -> None:
    lang = user.language
    await state.clear()
    products = await InventoryRepository(session).list_products(user.id, in_stock_only=True)
    if not products:
        await callback.answer(t("inv_nothing_to_sell", lang), show_alert=True)
        return
    await _edit(callback, t("inv_pick_sell", lang), product_pick_kb(products, "sell", lang, allow_new=False))
    await callback.answer()


@router.callback_query(F.data.regexp(r"^inv:(buy|sell):p:\d+$"))
async def product_chosen(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User
) -> None:
    lang = user.language
    _, action, _, pid = callback.data.split(":")
    product = await InventoryRepository(session).get_product(user.id, int(pid))
    if product is None:
        await callback.answer(t("session_expired", lang), show_alert=True)
        return
    if action == "sell" and product.quantity <= 0:
        await callback.answer(t("inv_nothing_to_sell", lang), show_alert=True)
        return
    await state.set_state(InventoryStates.waiting_qty)
    await state.update_data(action=action, product_id=product.id, product_name=product.name)
    key = "inv_ask_buy_qty" if action == "buy" else "inv_ask_sell_qty"
    await _edit(callback, f"📦 <b>{escape(product.name)}</b>")
    await callback.message.answer(
        t(key, lang, name=escape(product.name), stock=product.quantity),
        reply_markup=cancel_kb(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "inv:buy:new")
async def new_product(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.set_state(InventoryStates.waiting_name)
    await state.update_data(action="buy", product_id=None)
    await _edit(callback, t("inv_btn_new", lang))
    await callback.message.answer(t("inv_ask_name", lang), reply_markup=cancel_kb(lang))
    await callback.answer()


# ---------- Kiritish bosqichlari ----------


@router.message(InventoryStates.waiting_name, F.text)
async def product_name(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    lang = user.language
    name = valid_product_name(message.text or "")
    if name is None:
        await message.answer(t("inv_invalid_name", lang))
        return
    existing = await InventoryRepository(session).find_by_name(user.id, name)
    stock = 0
    if existing is not None:  # shu nomli mahsulot bor — o'shanga qo'shamiz
        await state.update_data(product_id=existing.id, product_name=existing.name)
        stock = existing.quantity
        name = existing.name
    else:
        await state.update_data(product_id=None, product_name=name)
    await state.set_state(InventoryStates.waiting_qty)
    await message.answer(t("inv_ask_buy_qty", lang, name=escape(name), stock=stock))


@router.message(InventoryStates.waiting_qty, F.text)
async def quantity(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    lang = user.language
    qty = parse_qty(message.text or "")
    if qty is None:
        await message.answer(t("inv_invalid_qty", lang))
        return
    data = await state.get_data()
    if data["action"] == "sell":
        product = await InventoryRepository(session).get_product(user.id, data["product_id"])
        stock = product.quantity if product else 0
        if qty > stock:
            await message.answer(t("inv_not_enough", lang, stock=stock))
            return
    await state.update_data(qty=qty)
    await state.set_state(InventoryStates.waiting_price)
    key = "inv_ask_buy_price" if data["action"] == "buy" else "inv_ask_sell_price"
    await message.answer(t(key, lang))


@router.message(InventoryStates.waiting_price, F.text)
async def unit_price(
    message: Message, state: FSMContext, session: AsyncSession, user: User
) -> None:
    lang = user.language
    data = await state.get_data()
    is_buy = data["action"] == "buy"
    price = parse_amount(message.text or "", allow_zero=is_buy)
    if price is None:
        await message.answer(t("invalid_price", lang))
        return
    data = await state.update_data(price=price)
    qty = data["qty"]
    fields = dict(
        name=escape(data["product_name"]),
        qty=qty,
        price=fmt_price(price, lang),
        total=fmt_price(price * qty, lang),
    )
    if is_buy:
        text = t("inv_buy_summary", lang, **fields)
    else:
        product = await InventoryRepository(session).get_product(user.id, data["product_id"])
        cost = product.avg_cost if product else 0
        text = t("inv_sell_summary", lang, profit=fmt_price((price - cost) * qty, lang), **fields)
    await state.set_state(InventoryStates.confirming)
    await message.answer(text, reply_markup=inventory_confirm_kb(lang))


@router.callback_query(InventoryStates.confirming, F.data == "inv:confirm")
async def confirm(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, user: User
) -> None:
    lang = user.language
    data = await state.get_data()
    repo = InventoryRepository(session)
    try:
        if data["action"] == "buy":
            product, move = await repo.buy(
                user.id,
                quantity=data["qty"],
                unit_price=data["price"],
                product_id=data.get("product_id"),
                new_name=data["product_name"],
            )
            text = t(
                "inv_buy_saved", lang, name=escape(product.name), qty=move.quantity,
                stock=product.quantity, when=fmt_dt(move.created_at),
            )
        else:
            product, move = await repo.sell(
                user.id, data["product_id"], quantity=data["qty"], unit_price=data["price"]
            )
            text = t(
                "inv_sell_saved", lang, name=escape(product.name), qty=move.quantity,
                total=fmt_price(move.total, lang), stock=product.quantity,
                when=fmt_dt(move.created_at),
            )
    except ValueError as e:  # sotuv paytida qoldiq yetmay qoldi
        await session.rollback()
        await callback.answer(t("inv_not_enough", lang, stock=e.args[0]), show_alert=True)
        return
    except LookupError:
        await session.rollback()
        await state.clear()
        await callback.answer(t("session_expired", lang), show_alert=True)
        return
    logger.info("Inventory %s by %s: %s x%s", data["action"], user.id, product.name, move.quantity)
    await state.clear()
    await _edit(callback, text)
    await callback.message.answer(
        t("continue", lang), reply_markup=master_menu(lang, user.is_admin)
    )
    await callback.message.answer(
        await _overview_text(session, user), reply_markup=inventory_menu_kb(lang)
    )
    await callback.answer()


@router.callback_query(F.data.in_({"inv:cancel", "inv:confirm"}))
async def cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    """Bekor qilish (yoki eskirgan tasdiqlash tugmasi)."""
    lang = user.language
    await state.clear()
    await _edit(callback, t("inv_cancelled", lang))
    await callback.message.answer(t("use_menu", lang), reply_markup=master_menu(lang, user.is_admin))
    await callback.answer()


# ---------- Ro'yxatlar ----------


@router.callback_query(F.data == "inv:stock")
async def show_stock(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    repo = InventoryRepository(session)
    products = await repo.list_products(user.id, in_stock_only=True)
    if not products:
        await _edit(callback, t("inv_stock_empty", lang), inventory_back_kb(lang))
        await callback.answer()
        return
    lines = [t("inv_stock_header", lang)]
    for p in products:
        lines.append(
            t("inv_stock_row", lang, name=escape(p.name), qty=p.quantity, cost=fmt_price(p.avg_cost, lang))
        )
    _, units, value = await repo.stock_summary(user.id)
    lines.append(t("inv_stock_total", lang, units=units, value=fmt_price(value, lang)))
    await _edit(callback, "\n".join(lines)[:4000], inventory_back_kb(lang))
    await callback.answer()


@router.callback_query(F.data.in_({"inv:list:in", "inv:list:out"}))
async def show_moves(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    kind = MoveKind.IN if callback.data.endswith(":in") else MoveKind.OUT
    moves = await InventoryRepository(session).list_moves(user.id, kind=kind, limit=25)
    if not moves:
        await _edit(callback, t("inv_moves_empty", lang), inventory_back_kb(lang))
        await callback.answer()
        return
    header = t("inv_buys_header" if kind == MoveKind.IN else "inv_sales_header", lang, n=len(moves))
    text = "\n".join([header] + [_move_line(m, lang) for m in moves])
    await _edit(callback, text[:4000], inventory_back_kb(lang))
    await callback.answer()


# ---------- PDF ----------


@router.callback_query(F.data == "inv:pdfmenu")
async def pdf_menu(callback: CallbackQuery, user: User) -> None:
    lang = user.language
    await _edit(callback, t("inv_pdf_offer", lang), inventory_pdf_kb(lang))
    await callback.answer()


@router.callback_query(F.data.startswith("inv:pdf:"))
async def pdf_report(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    period = callback.data.split(":")[2]
    if period not in reports.PERIODS:
        period = "all"
    await callback.answer(t("pdf_making", lang))
    pdf, _ = await reports.build_master_report(session, user, period)
    await callback.message.answer_document(
        BufferedInputFile(pdf, filename=reports.pdf_filename("usta", lang)),
        caption=f"📄 {escape(user.full_name)} — {reports.period_label(period, lang)}",
    )


# ---------- Oxirgi yozuvni bekor qilish ----------


@router.callback_query(F.data == "inv:undo")
async def undo_ask(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    move = await InventoryRepository(session).last_move(user.id)
    if move is None:
        await callback.answer(t("inv_undo_none", lang), show_alert=True)
        return
    kind = t("move_in" if move.kind == MoveKind.IN else "move_out", lang)
    await _edit(
        callback,
        t("inv_undo_confirm", lang, move=f"{kind}\n{_move_line(move, lang)}"),
        undo_confirm_kb(move.id, lang),
    )
    await callback.answer()


@router.callback_query(F.data.regexp(r"^inv:undo:\d+$"))
async def undo_do(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    move_id = int(callback.data.split(":")[2])
    repo = InventoryRepository(session)
    last = await repo.last_move(user.id)
    if last is None or last.id != move_id:  # faqat eng oxirgi yozuv bekor qilinadi
        await callback.answer(t("session_expired", lang), show_alert=True)
        return
    try:
        product = await repo.undo_move(user.id, move_id)
    except ValueError:
        await session.rollback()
        await callback.answer(t("inv_undo_impossible", lang), show_alert=True)
        return
    if product is None:
        await callback.answer(t("inv_undo_none", lang), show_alert=True)
        return
    logger.info("Inventory move %s undone by %s", move_id, user.id)
    await _edit(
        callback,
        t("inv_undo_done", lang, name=escape(product.name), stock=product.quantity),
        inventory_back_kb(lang),
    )
    await callback.answer()
