"""Admin panel: ustalar boshqaruvi, statistika, buyurtmalar, sozlamalar."""

import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError
from aiogram.filters import StateFilter
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.inline import (
    admin_panel_kb,
    back_to_panel_kb,
    income_period_kb,
    master_detail_kb,
    masters_list_kb,
)
from bot.keyboards.reply import BTN_ADMIN, master_menu
from bot.middlewares import AdminOnlyMiddleware
from bot.utils.formatters import fmt_dt, fmt_price, period_start
from bot.utils.i18n import t
from config import settings
from database.models import OrderStatus, User
from database.repositories import OrderRepository, UserRepository

logger = logging.getLogger(__name__)
router = Router(name="admin")
router.message.middleware(AdminOnlyMiddleware())
router.callback_query.middleware(AdminOnlyMiddleware())

PANEL_TEXT = "⚙️ <b>ADMIN PANEL</b>\n\nBo'limni tanlang:"


@router.message(StateFilter(None), F.text == BTN_ADMIN)
async def open_panel(message: Message) -> None:
    await message.answer(PANEL_TEXT, reply_markup=admin_panel_kb())


@router.callback_query(F.data == "admin:panel")
async def back_to_panel(callback: CallbackQuery) -> None:
    await callback.message.edit_text(PANEL_TEXT, reply_markup=admin_panel_kb())
    await callback.answer()


# ---------- Ustalar ----------

@router.callback_query(F.data == "admin:masters")
async def show_masters(callback: CallbackQuery, session: AsyncSession) -> None:
    masters = await UserRepository(session).list_all()
    await callback.message.edit_text(
        "👨‍🔧 <b>USTALAR</b>\n\n"
        "✅ — faol, ⛔️ — bloklangan/tasdiqlanmagan\n"
        "👑 — admin, 🔧 — usta\n\n"
        "Boshqarish uchun ustani tanlang:",
        reply_markup=masters_list_kb(masters),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:master:"))
async def master_detail(callback: CallbackQuery, session: AsyncSession) -> None:
    master_id = int(callback.data.split(":")[2])
    master = await UserRepository(session).get_by_id(master_id)
    if master is None:
        await callback.answer("Usta topilmadi.", show_alert=True)
        return
    status = "✅ Faol" if master.is_active else "⛔️ Nofaol"
    role = "👑 Admin" if master.is_admin else "🔧 Usta"
    await callback.message.edit_text(
        f"👤 <b>{escape(master.full_name)}</b>\n\n"
        f"Holati: {status}\n"
        f"Rol: {role}\n"
        f"Username: @{master.username or '—'}\n"
        f"Telegram ID: <code>{master.telegram_id}</code>\n"
        f"Qo'shilgan: {fmt_dt(master.created_at)}",
        reply_markup=master_detail_kb(master),
    )
    await callback.answer()


async def _notify_master(bot: Bot, master: User, text: str, with_menu: bool) -> None:
    try:
        await bot.send_message(
            master.telegram_id,
            text,
            reply_markup=(
                master_menu(master.language, master.is_admin) if with_menu else None
            ),
        )
    except TelegramAPIError:
        logger.warning("Ustaga (%s) xabar yuborib bo'lmadi", master.telegram_id)


@router.callback_query(F.data.startswith("admin:activate:"))
async def activate_master(
    callback: CallbackQuery, session: AsyncSession, bot: Bot
) -> None:
    master_id = int(callback.data.split(":")[2])
    master = await UserRepository(session).set_active(master_id, True)
    if master is None:
        await callback.answer("Usta topilmadi.", show_alert=True)
        return
    logger.info("Master %s activated", master.full_name)
    await callback.message.edit_text(
        f"✅ <b>{escape(master.full_name)}</b> faollashtirildi."
    )
    await _notify_master(
        bot, master, t("approved_notice", master.language), with_menu=True
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:block:"))
async def block_master(
    callback: CallbackQuery, session: AsyncSession, bot: Bot, user: User
) -> None:
    master_id = int(callback.data.split(":")[2])
    master = await UserRepository(session).get_by_id(master_id)
    if master is None:
        await callback.answer("Usta topilmadi.", show_alert=True)
        return
    if master.id == user.id:
        await callback.answer("O'zingizni bloklay olmaysiz.", show_alert=True)
        return
    await UserRepository(session).set_active(master_id, False)
    logger.info("Master %s blocked", master.full_name)
    await callback.message.edit_text(
        f"⛔️ <b>{escape(master.full_name)}</b> bloklandi."
    )
    await _notify_master(
        bot, master, t("blocked_notice", master.language), with_menu=False
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin:delete:"))
async def delete_master(
    callback: CallbackQuery, session: AsyncSession, user: User
) -> None:
    master_id = int(callback.data.split(":")[2])
    repo = UserRepository(session)
    master = await repo.get_by_id(master_id)
    if master is None:
        await callback.answer("Usta topilmadi.", show_alert=True)
        return
    if master.id == user.id:
        await callback.answer("O'zingizni o'chira olmaysiz.", show_alert=True)
        return
    name = master.full_name
    deleted = await repo.delete(master_id)
    if not deleted:
        # Buyurtmalari bor ustani FK cheklovi tufayli o'chirib bo'lmasligi mumkin
        await callback.answer(
            "O'chirib bo'lmadi — bu ustaga bog'langan buyurtmalar bor. "
            "Buning o'rniga bloklang.",
            show_alert=True,
        )
        return
    logger.info("Master %s deleted", name)
    await callback.message.edit_text(f"🗑 <b>{escape(name)}</b> tizimdan o'chirildi.")
    await callback.answer()


# ---------- Statistika ----------

@router.callback_query(F.data == "admin:stats")
async def show_stats(callback: CallbackQuery, session: AsyncSession) -> None:
    orders = OrderRepository(session)
    users = UserRepository(session)

    total = await orders.count_all()
    pending = await orders.count_by_status(OrderStatus.PENDING)
    ready = await orders.count_by_status(OrderStatus.READY)
    active_users = await users.count_active()
    revenue = await orders.total_revenue()
    per_master = await orders.stats_per_master()

    lines = [
        "📊 <b>STATISTIKA</b>",
        "",
        f"📦 Jami buyurtmalar: <b>{total}</b>",
        f"⏳ Kutayotganlar: <b>{pending}</b>",
        f"✅ Tayyorlar: <b>{ready}</b>",
        f"👨‍🔧 Faol xodimlar: <b>{active_users}</b>",
        f"💰 Jami tushum: <b>{fmt_price(revenue)}</b>",
    ]
    stats_rows = [m for m in per_master if m["created"] or m["completed"]]
    if stats_rows:
        lines += ["", "👨‍🔧 <b>Ustalar kesimida:</b>"]
        for m in stats_rows:
            lines += [
                "",
                f"<b>{escape(m['name'])}</b>",
                f"Qabul qilgan: {m['created']}",
                f"Tayyorlagan: {m['completed']}",
            ]
    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_panel_kb())
    await callback.answer()


# ---------- Daromadlar (ustalar kesimida) ----------

INCOME_PERIOD_LABELS = {
    "today": "📅 Bugun",
    "week": "🗓 Shu hafta",
    "month": "📆 Shu oy",
    "all": "∑ Jami (hozirgacha)",
}


@router.callback_query(F.data.startswith("admin:income:"))
async def show_income(callback: CallbackQuery, session: AsyncSession) -> None:
    period = callback.data.split(":")[2]
    if period not in INCOME_PERIOD_LABELS:
        period = "all"
    rows = await OrderRepository(session).income_per_master(period_start(period))

    lines = [f"💰 <b>DAROMADLAR</b> — {INCOME_PERIOD_LABELS[period]}", ""]
    if rows:
        total_sum = 0
        total_count = 0
        for i, r in enumerate(rows, start=1):
            lines.append(
                f"{i}. <b>{escape(r['name'])}</b> — {fmt_price(r['total'])} "
                f"({r['count']} ta)"
            )
            total_sum += r["total"]
            total_count += r["count"]
        lines += ["", f"Jami: <b>{fmt_price(total_sum)}</b> ({total_count} ta)"]
    else:
        lines.append("Bu davrda tayyor buyurtmalar yo'q.")

    await callback.message.edit_text(
        "\n".join(lines), reply_markup=income_period_kb(period)
    )
    await callback.answer()


# ---------- Buyurtmalar ----------

@router.callback_query(F.data == "admin:orders")
async def show_orders(callback: CallbackQuery, session: AsyncSession) -> None:
    repo = OrderRepository(session)
    pending = await repo.list_by_status(OrderStatus.PENDING, limit=15)
    ready = await repo.list_by_status(OrderStatus.READY, limit=10)

    lines = ["📦 <b>BUYURTMALAR</b>", "", "⏳ <b>Kutayotganlar:</b>"]
    if pending:
        for o in pending:
            lines.append(
                f"#{o.order_number} — {escape(o.creator.full_name)} ({fmt_dt(o.created_at)})"
            )
    else:
        lines.append("yo'q")
    lines += ["", "✅ <b>Oxirgi tayyorlar:</b>"]
    if ready:
        for o in ready:
            lines.append(f"#{o.order_number} — {fmt_price(o.price)}")
    else:
        lines.append("yo'q")
    lines += ["", "Batafsil ko'rish: 🔎 Buyurtmani topish"]
    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_panel_kb())
    await callback.answer()


# ---------- Sozlamalar ----------

@router.callback_query(F.data == "admin:settings")
async def show_settings(callback: CallbackQuery) -> None:
    def mark(value) -> str:
        return f"<code>{value}</code>" if value is not None else "❌ sozlanmagan"

    await callback.message.edit_text(
        "⚙️ <b>SOZLAMALAR</b>\n\n"
        f"Guruh ID: {mark(settings.group_id)}\n"
        f"Kutayotganlar topic: {mark(settings.pending_topic_id)}\n"
        f"Tayyorlar topic: {mark(settings.ready_topic_id)}\n"
        f"Biz haqimizda topic: {mark(settings.about_topic_id)}\n"
        f"Savol-javob topic: {mark(settings.faq_topic_id)}\n\n"
        f"🖥 Nomi: {escape(settings.workshop_name)}\n"
        f"📞 Telefon: {escape(settings.workshop_phone) or '—'}\n"
        f"📍 Manzil: {escape(settings.workshop_address) or '—'}\n"
        f"🕐 Ish vaqti: {escape(settings.workshop_working_hours) or '—'}\n\n"
        "Qiymatlar <code>.env</code> fayli orqali o'zgartiriladi.\n"
        "ID olish: guruhda /groupid, kerakli topic ichida /topicid\n"
        "«Biz haqimizda» e'lonini yuborish: /post_about",
        reply_markup=back_to_panel_kb(),
    )
    await callback.answer()
