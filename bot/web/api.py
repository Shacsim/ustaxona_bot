"""Mini App uchun veb-server: JSON API + ilova sahifalari.

Bot jarayonining ichida aiohttp bilan ishlaydi (alohida xizmat kerak emas),
bir xil baza, repozitoriylar va guruhga e'lon logikasidan foydalanadi.

Xavfsizlik: har bir /api so'rovi Telegram WebApp initData imzosi bilan
(bot tokeni orqali HMAC) tekshiriladi; foydalanuvchi bazada faol bo'lishi
shart; /api/admin/* faqat adminlar uchun.
"""

from __future__ import annotations

import asyncio
import logging
import time
from html import escape
from pathlib import Path
from typing import Any

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BufferedInputFile
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from bot.keyboards.reply import master_menu
from bot.services import group_publisher, reminders, reports
from bot.services import orders as orders_service
from bot.services.backup import send_backup
from bot.utils.formatters import period_start
from bot.utils.i18n import LANGS, t
from bot.utils.validators import (
    parse_amount,
    parse_phone,
    parse_price,
    parse_qty,
    valid_description,
    valid_name,
    valid_product_name,
)
from config import settings
from database.models import MoveKind, Order, OrderStatus, Product, StockMove, User
from database.repositories import InventoryRepository, OrderRepository, UserRepository

logger = logging.getLogger(__name__)

BASE = "/ustaxona"
WEBAPP_DIR = Path(__file__).resolve().parents[2] / "webapp"
INIT_DATA_MAX_AGE = 24 * 3600

SF = web.AppKey("session_factory", async_sessionmaker)
BOT = web.AppKey("bot", Bot)


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str = "") -> None:
        super().__init__(code)
        self.status, self.code, self.message = status, code, message


def _iso(dt) -> str | None:
    return dt.isoformat() if dt is not None else None


def order_json(o: Order) -> dict[str, Any]:
    master = o.completer or o.creator
    return {
        "id": o.id,
        "number": o.order_number,
        "status": o.status,
        "customer_name": o.customer_name,
        "customer_phone": o.customer_phone,
        "description": o.description,
        "work_done": o.work_done,
        "price": o.price,
        "created_at": _iso(o.created_at),
        "completed_at": _iso(o.completed_at),
        "created_by": o.creator.full_name if o.creator else None,
        "completed_by": o.completer.full_name if o.completer else None,
        "master": master.full_name if master else None,
    }


def product_json(p: Product) -> dict[str, Any]:
    return {"id": p.id, "name": p.name, "quantity": p.quantity, "avg_cost": p.avg_cost}


def move_json(m: StockMove) -> dict[str, Any]:
    return {
        "id": m.id,
        "kind": m.kind,
        "product_id": m.product_id,
        "product": m.product.name,
        "quantity": m.quantity,
        "unit_price": m.unit_price,
        "total": m.total,
        "profit": m.profit,
        "created_at": _iso(m.created_at),
    }


def user_json(u: User) -> dict[str, Any]:
    return {
        "id": u.id,
        "name": u.full_name,
        "username": u.username,
        "telegram_id": u.telegram_id,
        "role": u.role,
        "is_admin": u.is_admin,
        "is_active": u.is_active,
        "language": u.language,
        "created_at": _iso(u.created_at),
    }


# ---------- Middleware: xatolar va avtorizatsiya ----------


@web.middleware
async def error_mw(request: web.Request, handler):
    try:
        return await handler(request)
    except ApiError as e:
        return web.json_response({"error": e.code, "message": e.message}, status=e.status)
    except web.HTTPException:
        raise
    except Exception:  # noqa: BLE001
        logger.exception("API xatosi: %s %s", request.method, request.path)
        return web.json_response({"error": "server", "message": "Server error"}, status=500)


@web.middleware
async def auth_mw(request: web.Request, handler):
    if not request.path.startswith(f"{BASE}/api/"):
        return await handler(request)
    raw = request.headers.get("X-Telegram-Init-Data", "")
    try:
        init = safe_parse_webapp_init_data(settings.bot_token, raw)
    except ValueError:
        raise ApiError(401, "auth", "Telegram orqali oching / Откройте через Telegram")
    if init.user is None or time.time() - init.auth_date.timestamp() > INIT_DATA_MAX_AGE:
        raise ApiError(401, "auth", "Sessiya eskirgan / Сессия устарела")
    async with request.app[SF]() as session:
        user = await UserRepository(session).get_by_telegram_id(init.user.id)
        if user is None:
            raise ApiError(403, "not_registered", "/start")
        if not user.is_active:
            raise ApiError(403, "inactive", t("pending_approval", user.language))
        if request.path.startswith(f"{BASE}/api/admin/") and not user.is_admin:
            raise ApiError(403, "admin_only", t("admin_only", user.language))
        request["session"] = session
        request["user"] = user
        return await handler(request)


def _ctx(request: web.Request) -> tuple[AsyncSession, User, str]:
    user: User = request["user"]
    return request["session"], user, user.language


async def _body(request: web.Request) -> dict[str, Any]:
    try:
        data = await request.json()
    except ValueError:
        raise ApiError(400, "bad_json")
    if not isinstance(data, dict):
        raise ApiError(400, "bad_json")
    return data


def _period(value: str | None) -> str:
    return value if value in reports.PERIODS else "all"


routes = web.RouteTableDef()


# ---------- Sahifalar ----------


def _page(name: str) -> web.FileResponse:
    return web.FileResponse(WEBAPP_DIR / name, headers={"Cache-Control": "no-cache"})


@routes.get(f"{BASE}/app/")
@routes.get(f"{BASE}/app")
async def app_page(_: web.Request) -> web.StreamResponse:
    return _page("app.html")


@routes.get(f"{BASE}/tel.html")
async def tel_page(_: web.Request) -> web.StreamResponse:
    return _page("tel.html")


@routes.get(f"{BASE}/health")
async def health(_: web.Request) -> web.Response:
    return web.json_response({"ok": True})


# ---------- Profil ----------


@routes.get(f"{BASE}/api/me")
async def me(request: web.Request) -> web.Response:
    session, user, _ = _ctx(request)
    orders = OrderRepository(session)
    return web.json_response(
        {
            "user": user_json(user),
            "workshop": settings.workshop_name,
            "report_time": "%02d:%02d" % settings.report_time,
            "counts": {
                "pending": await orders.count_by_status(OrderStatus.PENDING),
                "my_pending": await orders.count_pending_by(user.id),
            },
        }
    )


@routes.post(f"{BASE}/api/lang")
async def set_lang(request: web.Request) -> web.Response:
    session, user, _ = _ctx(request)
    lang = (await _body(request)).get("lang")
    if lang not in LANGS:
        raise ApiError(400, "bad_lang")
    await UserRepository(session).set_language(user.id, lang)
    # Chatdagi menyu tugmalari ham yangi tilga o'tsin
    try:
        await request.app[BOT].send_message(
            user.telegram_id, t("lang_set", lang), reply_markup=master_menu(lang, user.is_admin)
        )
    except TelegramAPIError:
        pass
    return web.json_response({"ok": True, "language": lang})


# ---------- Buyurtmalar ----------


@routes.get(f"{BASE}/api/orders")
async def list_orders(request: web.Request) -> web.Response:
    session, _, _ = _ctx(request)
    repo = OrderRepository(session)
    status = request.query.get("status", "pending")
    if status == "ready":
        items = await repo.list_ready_between(period_start(_period(request.query.get("period"))))
        items = list(reversed(items))[:300]
    else:
        items = await repo.list_by_status(OrderStatus.PENDING, limit=300, oldest_first=True)
    return web.json_response({"orders": [order_json(o) for o in items]})


@routes.get(f"{BASE}/api/orders/{{number:\\d+}}")
async def get_order(request: web.Request) -> web.Response:
    session, _, lang = _ctx(request)
    number = int(request.match_info["number"])
    order = await OrderRepository(session).get_by_number(number)
    if order is None:
        raise ApiError(404, "not_found", t("order_not_found", lang, n=number))
    return web.json_response({"order": order_json(order)})


@routes.get(f"{BASE}/api/customer")
async def customer(request: web.Request) -> web.Response:
    session, _, _ = _ctx(request)
    phone = parse_phone(request.query.get("phone", ""))
    if phone is None:
        return web.json_response({"phone": None, "name": None, "count": 0})
    name, count = await OrderRepository(session).known_customer(phone)
    return web.json_response({"phone": phone, "name": name, "count": count})


@routes.post(f"{BASE}/api/orders")
async def create_order(request: web.Request) -> web.Response:
    session, user, lang = _ctx(request)
    data = await _body(request)
    phone = parse_phone(str(data.get("phone", "")))
    if phone is None:
        raise ApiError(400, "phone", t("invalid_phone", lang))
    name = valid_name(str(data.get("name", "")))
    if name is None:
        raise ApiError(400, "name", t("invalid_customer_name", lang))
    desc = valid_description(str(data.get("description", "")))
    if desc is None:
        raise ApiError(400, "description", t("invalid_description", lang))
    order, published = await orders_service.create_order(
        session, request.app[BOT], user, phone=phone, name=name, description=desc
    )
    return web.json_response({"order": order_json(order), "published": published})


@routes.post(f"{BASE}/api/orders/{{number:\\d+}}/complete")
async def complete_order(request: web.Request) -> web.Response:
    session, user, lang = _ctx(request)
    number = int(request.match_info["number"])
    data = await _body(request)
    work = str(data.get("work_done", "")).strip()
    if len(work) < 3:
        raise ApiError(400, "work", t("work_too_short", lang))
    if len(work) > 2000:
        raise ApiError(400, "work", t("work_too_long", lang))
    price = parse_price(str(data.get("price", "")))
    if price is None:
        raise ApiError(400, "price", t("invalid_price", lang))
    order = await OrderRepository(session).get_by_number(number)
    if order is None:
        raise ApiError(404, "not_found", t("order_not_found", lang, n=number))
    try:
        result = await orders_service.complete_order(
            session, request.app[BOT], user, order.id, work, price
        )
    except orders_service.OrderStateError:
        raise ApiError(409, "not_pending", t("already_ready", lang, n=number))
    if result is None:
        raise ApiError(404, "not_found", t("order_vanished", lang))
    done, published = result
    return web.json_response({"order": order_json(done), "published": published})


# ---------- Daromad ----------


@routes.get(f"{BASE}/api/income")
async def income(request: web.Request) -> web.Response:
    session, user, _ = _ctx(request)
    repo = OrderRepository(session)
    inv = InventoryRepository(session)
    out = {}
    for p in reports.PERIODS:
        since = period_start(p)
        count, total = await repo.master_income(user.id, since)
        s = await inv.totals(user.id, since=since)
        out[p] = {
            "orders": count,
            "income": total,
            "sales": s.out_sum,
            "sold_units": s.out_units,
            "profit": s.profit,
            "bought": s.in_sum,
            "bought_units": s.in_units,
        }
    return web.json_response({"periods": out})


@routes.post(f"{BASE}/api/pdf")
async def pdf(request: web.Request) -> web.Response:
    """PDF hisobotni foydalanuvchining bot chatiga yuboradi."""
    session, user, lang = _ctx(request)
    data = await _body(request)
    kind = data.get("kind")
    period = _period(data.get("period"))
    if kind == "pending":
        content, count = await reports.build_pending_pdf(session, lang)
        fname, caption = "kutayotgan", f"📋 {t('pdf_btn', lang)} — {count}"
    elif kind == "ready":
        content, count = await reports.build_ready_pdf(session, period, lang)
        fname, caption = "tayyor", f"✅ {reports.period_label(period, lang)} — {count}"
    elif kind == "master":
        content, _ = await reports.build_master_report(session, user, period)
        fname = "usta"
        caption = f"📄 {escape(user.full_name)} — {reports.period_label(period, lang)}"
    else:
        raise ApiError(400, "bad_kind")
    try:
        await request.app[BOT].send_document(
            user.telegram_id,
            BufferedInputFile(content, filename=reports.pdf_filename(fname, lang)),
            caption=caption,
        )
    except TelegramAPIError as e:
        raise ApiError(502, "telegram", str(e))
    return web.json_response({"ok": True})


# ---------- Ombor ----------


@routes.get(f"{BASE}/api/inventory")
async def inventory(request: web.Request) -> web.Response:
    session, user, _ = _ctx(request)
    repo = InventoryRepository(session)
    kinds, units, value = await repo.stock_summary(user.id)
    today = await repo.totals(user.id, since=period_start("today"))
    last = await repo.last_move(user.id)
    return web.json_response(
        {
            "summary": {"kinds": kinds, "units": units, "value": value},
            "today": today.__dict__,
            "products": [product_json(p) for p in await repo.list_products(user.id)],
            "last_move": move_json(last) if last else None,
        }
    )


@routes.get(f"{BASE}/api/inventory/moves")
async def inventory_moves(request: web.Request) -> web.Response:
    session, user, _ = _ctx(request)
    kind_raw = request.query.get("kind")
    kind = MoveKind.IN if kind_raw == "in" else MoveKind.OUT if kind_raw == "out" else None
    moves = await InventoryRepository(session).list_moves(user.id, kind=kind, limit=200)
    return web.json_response({"moves": [move_json(m) for m in moves]})


@routes.post(f"{BASE}/api/inventory/buy")
async def inventory_buy(request: web.Request) -> web.Response:
    session, user, lang = _ctx(request)
    data = await _body(request)
    qty = parse_qty(str(data.get("qty", "")))
    if qty is None:
        raise ApiError(400, "qty", t("inv_invalid_qty", lang))
    price = parse_amount(str(data.get("price", "")), allow_zero=True)
    if price is None:
        raise ApiError(400, "price", t("invalid_price", lang))
    product_id = data.get("product_id")
    name = None
    if not product_id:
        name = valid_product_name(str(data.get("name", "")))
        if name is None:
            raise ApiError(400, "name", t("inv_invalid_name", lang))
    try:
        product, move = await InventoryRepository(session).buy(
            user.id, quantity=qty, unit_price=price,
            product_id=int(product_id) if product_id else None, new_name=name,
        )
    except LookupError:
        await session.rollback()
        raise ApiError(404, "not_found", t("session_expired", lang))
    return web.json_response({"product": product_json(product), "move": move_json(move)})


@routes.post(f"{BASE}/api/inventory/sell")
async def inventory_sell(request: web.Request) -> web.Response:
    session, user, lang = _ctx(request)
    data = await _body(request)
    qty = parse_qty(str(data.get("qty", "")))
    if qty is None:
        raise ApiError(400, "qty", t("inv_invalid_qty", lang))
    price = parse_amount(str(data.get("price", "")))
    if price is None:
        raise ApiError(400, "price", t("invalid_price", lang))
    try:
        product, move = await InventoryRepository(session).sell(
            user.id, int(data.get("product_id") or 0), quantity=qty, unit_price=price
        )
    except ValueError as e:
        await session.rollback()
        raise ApiError(409, "not_enough", t("inv_not_enough", lang, stock=e.args[0]))
    except LookupError:
        await session.rollback()
        raise ApiError(404, "not_found", t("session_expired", lang))
    return web.json_response({"product": product_json(product), "move": move_json(move)})


@routes.post(f"{BASE}/api/inventory/undo")
async def inventory_undo(request: web.Request) -> web.Response:
    session, user, lang = _ctx(request)
    move_id = int((await _body(request)).get("move_id") or 0)
    repo = InventoryRepository(session)
    last = await repo.last_move(user.id)
    if last is None or last.id != move_id:
        raise ApiError(409, "stale", t("session_expired", lang))
    try:
        product = await repo.undo_move(user.id, move_id)
    except ValueError:
        await session.rollback()
        raise ApiError(409, "impossible", t("inv_undo_impossible", lang))
    if product is None:
        raise ApiError(404, "not_found", t("inv_undo_none", lang))
    return web.json_response({"product": product_json(product)})


# ---------- Admin ----------


@routes.get(f"{BASE}/api/admin/overview")
async def admin_overview(request: web.Request) -> web.Response:
    session, _, _ = _ctx(request)
    orders = OrderRepository(session)
    period = _period(request.query.get("period"))
    return web.json_response(
        {
            "stats": {
                "total": await orders.count_all(),
                "pending": await orders.count_by_status(OrderStatus.PENDING),
                "ready": await orders.count_by_status(OrderStatus.READY),
                "active_users": await UserRepository(session).count_active(),
                "revenue": await orders.total_revenue(),
            },
            "income": await orders.income_per_master(period_start(period)),
            "per_master": await orders.stats_per_master(),
            "period": period,
        }
    )


@routes.get(f"{BASE}/api/admin/masters")
async def admin_masters(request: web.Request) -> web.Response:
    session, _, _ = _ctx(request)
    return web.json_response(
        {"masters": [user_json(u) for u in await UserRepository(session).list_all()]}
    )


@routes.post(f"{BASE}/api/admin/masters/{{uid:\\d+}}")
async def admin_master_action(request: web.Request) -> web.Response:
    session, user, lang = _ctx(request)
    uid = int(request.match_info["uid"])
    action = (await _body(request)).get("action")
    repo = UserRepository(session)
    master = await repo.get_by_id(uid)
    if master is None:
        raise ApiError(404, "not_found", t("adm_not_found", lang))
    bot = request.app[BOT]
    if action in ("block", "delete") and master.id == user.id:
        raise ApiError(400, "self", t("adm_self_block" if action == "block" else "adm_self_delete", lang))
    if action == "activate":
        await repo.set_active(uid, True)
        notice, menu = t("approved_notice", master.language), master_menu(master.language, master.is_admin)
    elif action == "block":
        await repo.set_active(uid, False)
        notice, menu = t("blocked_notice", master.language), None
    elif action == "delete":
        if not await repo.delete(uid):
            raise ApiError(409, "has_orders", t("adm_delete_failed", lang))
        return web.json_response({"ok": True})
    else:
        raise ApiError(400, "bad_action")
    try:
        await bot.send_message(master.telegram_id, notice, reply_markup=menu)
    except TelegramAPIError:
        pass
    logger.info("Admin %s: %s master %s (Mini App)", user.id, action, uid)
    return web.json_response({"ok": True})


@routes.post(f"{BASE}/api/admin/broadcast")
async def admin_broadcast(request: web.Request) -> web.Response:
    session, user, lang = _ctx(request)
    data = await _body(request)
    text = str(data.get("text", "")).strip()
    if not 2 <= len(text) <= 3500:
        raise ApiError(400, "text", t("invalid_description", lang))
    bot = request.app[BOT]
    if data.get("target") == "group":
        if settings.group_id is None:
            raise ApiError(400, "no_group", t("bc_no_group", lang))
        try:
            await bot.send_message(
                settings.group_id, escape(text), message_thread_id=settings.elon_topic_id
            )
            await group_publisher.ensure_topic_closed(bot, settings.elon_topic_id)
        except TelegramAPIError as e:
            raise ApiError(502, "telegram", t("bc_group_failed", lang, err=escape(str(e))))
        return web.json_response({"ok": True, "sent": 1, "failed": 0})
    sent = failed = 0
    for m in await UserRepository(session).list_active():
        if m.id == user.id:
            continue
        try:
            await bot.send_message(
                m.telegram_id, f"{t('bc_from_admin', m.language)}\n\n{escape(text)}"
            )
            sent += 1
        except TelegramAPIError:
            failed += 1
        await asyncio.sleep(0.05)
    logger.info("Broadcast (Mini App) by %s: sent=%s failed=%s", user.id, sent, failed)
    return web.json_response({"ok": True, "sent": sent, "failed": failed})


def _reminder_json(cfg: reminders.ReminderSettings) -> dict[str, Any]:
    return {
        "enabled": cfg.enabled,
        "time": cfg.time_text,
        "overdue_days": cfg.overdue_days,
        "target": cfg.target,
    }


@routes.get(f"{BASE}/api/admin/reminder")
async def admin_reminder_get(request: web.Request) -> web.Response:
    session, _, _ = _ctx(request)
    return web.json_response(_reminder_json(await reminders.load_settings(session)))


@routes.post(f"{BASE}/api/admin/reminder")
async def admin_reminder_set(request: web.Request) -> web.Response:
    session, user, lang = _ctx(request)
    data = await _body(request)
    cfg = await reminders.load_settings(session)
    if "enabled" in data:
        cfg.enabled = bool(data["enabled"])
    if "time" in data:
        at = reminders.parse_time(str(data["time"]))
        if at is None:
            raise ApiError(400, "time", t("rem_bad_time", lang))
        cfg.hour, cfg.minute = at
    if "overdue_days" in data:
        try:
            days = int(data["overdue_days"])
        except (TypeError, ValueError):
            days = 0
        if not 1 <= days <= 30:
            raise ApiError(400, "days", t("rem_bad_time", lang))
        cfg.overdue_days = days
    if "target" in data:
        if data["target"] not in reminders.TARGETS:
            raise ApiError(400, "target")
        cfg.target = data["target"]
    await reminders.save_settings(session, cfg)
    logger.info("Reminder settings changed by %s (Mini App): %s", user.id, cfg)
    return web.json_response(_reminder_json(cfg))


@routes.post(f"{BASE}/api/admin/reminder/test")
async def admin_reminder_test(request: web.Request) -> web.Response:
    _, user, _ = _ctx(request)
    sent = await reminders.send_pending_reminders(
        request.app[BOT], request.app[SF], only_to=user
    )
    return web.json_response({"ok": bool(sent)})


@routes.post(f"{BASE}/api/admin/backup")
async def admin_backup(request: web.Request) -> web.Response:
    _, user, _ = _ctx(request)
    ok = await send_backup(request.app[BOT], request.app[SF], only_to=user.telegram_id)
    return web.json_response({"ok": ok})


# ---------- Ishga tushirish ----------


def create_app(bot: Bot, session_factory: async_sessionmaker[AsyncSession]) -> web.Application:
    app = web.Application(middlewares=[error_mw, auth_mw], client_max_size=1024 * 1024)
    app[BOT] = bot
    app[SF] = session_factory
    app.add_routes(routes)
    return app


async def start_web(
    bot: Bot, session_factory: async_sessionmaker[AsyncSession]
) -> web.AppRunner:
    runner = web.AppRunner(create_app(bot, session_factory), access_log=None)
    await runner.setup()
    site = web.TCPSite(runner, settings.web_host, settings.web_port)
    await site.start()
    logger.info("Mini App server: http://%s:%s%s/app/", settings.web_host, settings.web_port, BASE)
    return runner
