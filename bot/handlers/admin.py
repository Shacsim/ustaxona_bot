"""Admin panel: ustalar, statistika, daromadlar, buyurtmalar, e'lon, zaxira, sozlamalar.

Panel admin tanlagan tilda (uz/ru/en) ko'rsatiladi.
"""

import asyncio
import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramRetryAfter
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.keyboards.inline import (
    admin_panel_kb,
    back_to_panel_kb,
    broadcast_confirm_kb,
    broadcast_target_kb,
    income_period_kb,
    master_detail_kb,
    masters_list_kb,
)
from bot.keyboards.reply import BTN_ADMIN, cancel_kb, master_menu
from bot.middlewares import AdminOnlyMiddleware
from bot.services import group_publisher
from bot.services.backup import send_backup
from bot.services.reports import PERIOD_KEYS
from bot.states import BroadcastStates
from bot.utils.formatters import fmt_dt, fmt_price, period_start
from bot.utils.i18n import BUTTONS, LANG_NAMES, t
from config import settings
from database.models import OrderStatus, User
from database.repositories import OrderRepository, UserRepository

logger = logging.getLogger(__name__)
router = Router(name="admin")
router.message.middleware(AdminOnlyMiddleware())
router.callback_query.middleware(AdminOnlyMiddleware())

ALL_BUTTON_TEXTS = {v for variants in BUTTONS.values() for v in variants.values()} | {BTN_ADMIN}


async def _edit(callback: CallbackQuery, text: str, markup=None) -> None:
    try:
        await callback.message.edit_text(text, reply_markup=markup)
    except TelegramBadRequest:
        pass


@router.message(StateFilter(None), F.text == BTN_ADMIN)
async def open_panel(message: Message, user: User) -> None:
    await message.answer(t("adm_panel", user.language), reply_markup=admin_panel_kb(user.language))


@router.callback_query(F.data == "admin:panel")
async def back_to_panel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    await _edit(callback, t("adm_panel", user.language), admin_panel_kb(user.language))
    await callback.answer()


# ---------- Ustalar ----------


@router.callback_query(F.data == "admin:masters")
async def show_masters(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    masters = await UserRepository(session).list_all()
    await _edit(callback, t("adm_masters", user.language), masters_list_kb(masters, user.language))
    await callback.answer()


@router.callback_query(F.data.startswith("admin:master:"))
async def master_detail(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    master = await UserRepository(session).get_by_id(int(callback.data.split(":")[2]))
    if master is None:
        await callback.answer(t("adm_not_found", lang), show_alert=True)
        return
    await _edit(
        callback,
        t(
            "adm_master_card",
            lang,
            name=escape(master.full_name),
            status=t("adm_active" if master.is_active else "adm_inactive", lang),
            role=t("role_admin" if master.is_admin else "role_master", lang),
            language=LANG_NAMES.get(master.language, master.language),
            username=escape(master.username or "—"),
            tg_id=master.telegram_id,
            created=fmt_dt(master.created_at),
        ),
        master_detail_kb(master, lang),
    )
    await callback.answer()


async def _notify_master(bot: Bot, master: User, text: str, with_menu: bool) -> None:
    try:
        await bot.send_message(
            master.telegram_id,
            text,
            reply_markup=master_menu(master.language, master.is_admin) if with_menu else None,
        )
    except TelegramAPIError:
        logger.warning("Ustaga (%s) xabar yuborib bo'lmadi", master.telegram_id)


@router.callback_query(F.data.startswith("admin:activate:"))
async def activate_master(
    callback: CallbackQuery, session: AsyncSession, bot: Bot, user: User
) -> None:
    lang = user.language
    master = await UserRepository(session).set_active(int(callback.data.split(":")[2]), True)
    if master is None:
        await callback.answer(t("adm_not_found", lang), show_alert=True)
        return
    logger.info("Master %s activated", master.full_name)
    await _edit(callback, t("adm_activated", lang, name=escape(master.full_name)))
    await _notify_master(bot, master, t("approved_notice", master.language), with_menu=True)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:block:"))
async def block_master(
    callback: CallbackQuery, session: AsyncSession, bot: Bot, user: User
) -> None:
    lang = user.language
    repo = UserRepository(session)
    master = await repo.get_by_id(int(callback.data.split(":")[2]))
    if master is None:
        await callback.answer(t("adm_not_found", lang), show_alert=True)
        return
    if master.id == user.id:
        await callback.answer(t("adm_self_block", lang), show_alert=True)
        return
    await repo.set_active(master.id, False)
    logger.info("Master %s blocked", master.full_name)
    await _edit(callback, t("adm_blocked", lang, name=escape(master.full_name)))
    await _notify_master(bot, master, t("blocked_notice", master.language), with_menu=False)
    await callback.answer()


@router.callback_query(F.data.startswith("admin:delete:"))
async def delete_master(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    repo = UserRepository(session)
    master = await repo.get_by_id(int(callback.data.split(":")[2]))
    if master is None:
        await callback.answer(t("adm_not_found", lang), show_alert=True)
        return
    if master.id == user.id:
        await callback.answer(t("adm_self_delete", lang), show_alert=True)
        return
    name = master.full_name
    if not await repo.delete(master.id):
        # Buyurtmalari bor ustani FK cheklovi tufayli o'chirib bo'lmaydi
        await callback.answer(t("adm_delete_failed", lang), show_alert=True)
        return
    logger.info("Master %s deleted", name)
    await _edit(callback, t("adm_deleted", lang, name=escape(name)))
    await callback.answer()


# ---------- Statistika ----------


@router.callback_query(F.data == "admin:stats")
async def show_stats(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    orders = OrderRepository(session)
    lines = [
        t(
            "adm_stats",
            lang,
            total=await orders.count_all(),
            pending=await orders.count_by_status(OrderStatus.PENDING),
            ready=await orders.count_by_status(OrderStatus.READY),
            users=await UserRepository(session).count_active(),
            revenue=fmt_price(await orders.total_revenue(), lang),
        )
    ]
    rows = [m for m in await orders.stats_per_master() if m["created"] or m["completed"]]
    if rows:
        lines += ["", t("adm_stats_per_master", lang)]
        for m in rows:
            lines += [
                "",
                t("adm_stats_row", lang, name=escape(m["name"]), created=m["created"], completed=m["completed"]),
            ]
    await _edit(callback, "\n".join(lines), back_to_panel_kb(lang))
    await callback.answer()


# ---------- Daromadlar (ustalar kesimida) ----------


@router.callback_query(F.data.startswith("admin:income:"))
async def show_income(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    period = callback.data.split(":")[2]
    if period not in PERIOD_KEYS:
        period = "all"
    rows = await OrderRepository(session).income_per_master(period_start(period))
    lines = [t("adm_income_title", lang, period=t(PERIOD_KEYS[period], lang)), ""]
    if rows:
        for i, r in enumerate(rows, start=1):
            lines.append(
                t("adm_income_row", lang, i=i, name=escape(r["name"]),
                  total=fmt_price(r["total"], lang), count=r["count"])
            )
        lines += [
            "",
            t("adm_income_total", lang, total=fmt_price(sum(r["total"] for r in rows), lang),
              count=sum(r["count"] for r in rows)),
        ]
    else:
        lines.append(t("adm_income_none", lang))
    await _edit(callback, "\n".join(lines), income_period_kb(period, lang))
    await callback.answer()


# ---------- Buyurtmalar ----------


@router.callback_query(F.data == "admin:orders")
async def show_orders(callback: CallbackQuery, session: AsyncSession, user: User) -> None:
    lang = user.language
    repo = OrderRepository(session)
    pending = await repo.list_by_status(OrderStatus.PENDING, limit=15)
    ready = await repo.list_by_status(OrderStatus.READY, limit=10)
    lines = [t("adm_orders", lang), "", t("adm_orders_pending", lang)]
    lines += [
        f"#{o.order_number} — {escape(o.creator.full_name)} ({fmt_dt(o.created_at)})" for o in pending
    ] or [t("adm_none", lang)]
    lines += ["", t("adm_orders_ready", lang)]
    lines += [f"#{o.order_number} — {fmt_price(o.price, lang)}" for o in ready] or [t("adm_none", lang)]
    lines += ["", t("adm_orders_hint", lang)]
    await _edit(callback, "\n".join(lines), back_to_panel_kb(lang))
    await callback.answer()


# ---------- Zaxira nusxa (qo'lda) ----------


@router.callback_query(F.data == "admin:backup")
async def backup_now(
    callback: CallbackQuery,
    bot: Bot,
    user: User,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    await callback.answer(t("backup_making", user.language))
    await send_backup(bot, session_factory, only_to=user.telegram_id)


# ---------- E'lon yuborish ----------


def _target_name(target: str, lang: str) -> str:
    return t("bc_target_masters" if target == "masters" else "bc_target_group", lang)


@router.callback_query(F.data == "admin:bc")
async def broadcast_start(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    await state.clear()
    await _edit(callback, t("bc_choose_target", user.language), broadcast_target_kb(user.language))
    await callback.answer()


@router.callback_query(F.data.in_({"admin:bc:masters", "admin:bc:group"}))
async def broadcast_target(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    target = callback.data.split(":")[2]
    if target == "group" and settings.group_id is None:
        await callback.answer(t("bc_no_group", lang), show_alert=True)
        return
    await state.set_state(BroadcastStates.waiting_content)
    await state.update_data(bc_target=target)
    await _edit(callback, t("bc_choose_target", lang) + f"\n\n👉 <b>{_target_name(target, lang)}</b>")
    await callback.message.answer(
        t("bc_ask_content", lang, target=_target_name(target, lang)), reply_markup=cancel_kb(lang)
    )
    await callback.answer()


SUPPORTED = {"text", "photo", "video", "document", "animation", "audio", "voice"}


@router.message(BroadcastStates.waiting_content)
async def broadcast_content(message: Message, state: FSMContext, bot: Bot, user: User) -> None:
    lang = user.language
    if message.content_type not in SUPPORTED:
        await message.answer(t("bc_unsupported", lang))
        return
    if message.text in ALL_BUTTON_TEXTS:  # menyu tugmasi tasodifan bosilgan
        await message.answer(t("fsm_hint", lang))
        return
    data = await state.update_data(
        bc_chat=message.chat.id,
        bc_msg=message.message_id,
        bc_html=message.html_text if (message.text or message.caption) else "",
        bc_is_text=message.content_type == "text",
    )
    await state.set_state(BroadcastStates.confirming)
    await bot.copy_message(message.chat.id, message.chat.id, message.message_id)
    await message.answer(
        t("bc_preview", lang, target=_target_name(data["bc_target"], lang)),
        reply_markup=broadcast_confirm_kb(lang),
    )


async def _send_to_master(bot: Bot, master: User, data: dict) -> None:
    header = t("bc_from_admin", master.language)
    body = data["bc_html"]
    if data["bc_is_text"]:
        await bot.send_message(master.telegram_id, f"{header}\n\n{body}")
        return
    caption = f"{header}\n\n{body}" if body else header
    if len(caption) > 1024:  # Telegram izoh chegarasi — sarlavhasiz asl izoh
        caption = None
    await bot.copy_message(
        master.telegram_id, data["bc_chat"], data["bc_msg"], caption=caption
    )


@router.callback_query(BroadcastStates.confirming, F.data == "admin:bc:send")
async def broadcast_send(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot, user: User
) -> None:
    lang = user.language
    data = await state.get_data()
    await state.clear()
    await _edit(callback, t("bc_sending", lang))
    await callback.answer()

    if data["bc_target"] == "group":
        try:
            await bot.copy_message(
                settings.group_id,
                data["bc_chat"],
                data["bc_msg"],
                message_thread_id=settings.elon_topic_id,
            )
            await group_publisher.ensure_topic_closed(bot, settings.elon_topic_id)
            result = t("bc_done_group", lang)
        except TelegramAPIError as e:
            logger.error("E'lon guruhga yuborilmadi: %s", e)
            result = t("bc_group_failed", lang, err=escape(str(e)))
    else:
        masters = [m for m in await UserRepository(session).list_active() if m.id != user.id]
        ok = failed = 0
        for m in masters:
            try:
                await _send_to_master(bot, m, data)
                ok += 1
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after + 1)
                try:
                    await _send_to_master(bot, m, data)
                    ok += 1
                except TelegramAPIError:
                    failed += 1
            except TelegramAPIError as e:
                logger.warning("E'lon %s ga yetmadi: %s", m.telegram_id, e)
                failed += 1
            await asyncio.sleep(0.05)
        result = t(
            "bc_done_masters", lang, ok=ok,
            failed=t("bc_failed_part", lang, n=failed) if failed else "",
        )
    logger.info("Broadcast (%s) by %s: %s", data["bc_target"], user.id, result)
    await _edit(callback, result)
    await callback.message.answer(t("continue", lang), reply_markup=master_menu(lang, user.is_admin))


@router.callback_query(F.data.in_({"admin:bc:cancel", "admin:bc:send"}))
async def broadcast_cancel(callback: CallbackQuery, state: FSMContext, user: User) -> None:
    lang = user.language
    await state.clear()
    await _edit(callback, t("cancelled", lang))
    await callback.message.answer(t("use_menu", lang), reply_markup=master_menu(lang, user.is_admin))
    await callback.answer()


# ---------- Sozlamalar ----------


@router.callback_query(F.data == "admin:settings")
async def show_settings(callback: CallbackQuery, user: User) -> None:
    lang = user.language

    def mark(value) -> str:
        return f"<code>{value}</code>" if value is not None else t("adm_not_set", lang)

    await _edit(
        callback,
        t(
            "adm_settings",
            lang,
            group=mark(settings.group_id),
            pending=mark(settings.pending_topic_id),
            ready=mark(settings.ready_topic_id),
            about=mark(settings.about_topic_id),
            faq=mark(settings.faq_topic_id),
            elon=mark(settings.elon_topic_id),
            wname=escape(settings.workshop_name),
            wphone=escape(settings.workshop_phone) or "—",
            waddr=escape(settings.workshop_address) or "—",
            whours=escape(settings.workshop_working_hours) or "—",
            report="%02d:%02d" % settings.report_time,
            backup="%02d:%02d" % settings.backup_time,
        ),
        back_to_panel_kb(lang),
    )
    await callback.answer()
