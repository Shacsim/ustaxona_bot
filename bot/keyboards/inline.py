"""Inline klaviaturalar va callback data formatlari."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from bot.utils.i18n import btn, t
from config import settings
from database.models import Product, User

IB = InlineKeyboardButton


def _kb(rows: list[list[InlineKeyboardButton]]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=rows)


def open_app_kb(lang: str) -> InlineKeyboardMarkup | None:
    """«📱 Ilovani ochish» — to'liq Mini App (WEBAPP_URL sozlangan bo'lsa)."""
    if not settings.webapp_url:
        return None
    return _kb([[IB(text=t("open_app", lang), web_app=WebAppInfo(url=settings.webapp_url))]])


def language_kb() -> InlineKeyboardMarkup:
    return _kb(
        [
            [
                IB(text="🇺🇿 O'zbekcha", callback_data="lang:uz"),
                IB(text="🇷🇺 Русский", callback_data="lang:ru"),
                IB(text="🇬🇧 English", callback_data="lang:en"),
            ]
        ]
    )


def confirm_new_order_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    return _kb(
        [
            [
                IB(text=btn("confirm_accept", lang), callback_data="neworder:confirm"),
                IB(text=btn("cancel", lang), callback_data="neworder:cancel"),
            ]
        ]
    )


def confirm_complete_kb(lang: str = "uz") -> InlineKeyboardMarkup:
    return _kb(
        [
            [
                IB(text=btn("confirm_ready", lang), callback_data="complete:confirm"),
                IB(text=btn("cancel", lang), callback_data="complete:cancel"),
            ]
        ]
    )


def period_buttons(prefix: str, lang: str, active: str | None = None) -> list[list[InlineKeyboardButton]]:
    """Bugun / Hafta / Oy / Jami — callback: '{prefix}:{period}'."""
    row = [
        IB(
            text=(f"• {t(f'period_btn_{p}', lang)} •" if p == active else t(f"period_btn_{p}", lang)),
            callback_data=f"{prefix}:{p}",
        )
        for p in ("today", "week", "month", "all")
    ]
    return [row[:2], row[2:]]


# ---------- Ro'yxatlar uchun PDF ----------


def pending_pdf_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb([[IB(text=t("pdf_btn", lang), callback_data="pdf:pending")]])


def ready_pdf_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb(period_buttons("pdf:ready", lang))


def income_pdf_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb(period_buttons("inv:pdf", lang))


# ---------- Ombor ----------


def inventory_menu_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb(
        [
            [
                IB(text=t("inv_btn_buy", lang), callback_data="inv:buy"),
                IB(text=t("inv_btn_sell", lang), callback_data="inv:sell"),
            ],
            [IB(text=t("inv_btn_stock", lang), callback_data="inv:stock")],
            [
                IB(text=t("inv_btn_buys", lang), callback_data="inv:list:in"),
                IB(text=t("inv_btn_sales", lang), callback_data="inv:list:out"),
            ],
            [IB(text=t("pdf_btn", lang), callback_data="inv:pdfmenu")],
            [IB(text=t("inv_btn_undo", lang), callback_data="inv:undo")],
        ]
    )


def inventory_back_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb([[IB(text=btn("back", lang), callback_data="inv:menu")]])


def inventory_pdf_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb(
        period_buttons("inv:pdf", lang)
        + [[IB(text=btn("back", lang), callback_data="inv:menu")]]
    )


def product_pick_kb(
    products: list[Product], action: str, lang: str, allow_new: bool
) -> InlineKeyboardMarkup:
    rows = [
        [IB(text=f"{p.name} · {p.quantity}", callback_data=f"inv:{action}:p:{p.id}")]
        for p in products[:40]
    ]
    if allow_new:
        rows.append([IB(text=t("inv_btn_new", lang), callback_data=f"inv:{action}:new")])
    rows.append([IB(text=btn("cancel", lang), callback_data="inv:cancel")])
    return _kb(rows)


def inventory_confirm_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb(
        [
            [
                IB(text=btn("confirm", lang), callback_data="inv:confirm"),
                IB(text=btn("cancel", lang), callback_data="inv:cancel"),
            ]
        ]
    )


def undo_confirm_kb(move_id: int, lang: str) -> InlineKeyboardMarkup:
    return _kb(
        [
            [
                IB(text=btn("confirm", lang), callback_data=f"inv:undo:{move_id}"),
                IB(text=btn("back", lang), callback_data="inv:menu"),
            ]
        ]
    )


# ---------- Admin panel ----------


def admin_panel_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb(
        [
            [IB(text=t("adm_btn_masters", lang), callback_data="admin:masters")],
            [
                IB(text=t("adm_btn_stats", lang), callback_data="admin:stats"),
                IB(text=t("adm_btn_income", lang), callback_data="admin:income:all"),
            ],
            [IB(text=t("adm_btn_orders", lang), callback_data="admin:orders")],
            [IB(text=t("adm_btn_broadcast", lang), callback_data="admin:bc")],
            [IB(text=t("adm_btn_backup", lang), callback_data="admin:backup")],
            [IB(text=t("adm_btn_settings", lang), callback_data="admin:settings")],
        ]
    )


def income_period_kb(active: str, lang: str) -> InlineKeyboardMarkup:
    return _kb(
        period_buttons("admin:income", lang, active)
        + [[IB(text=btn("back", lang), callback_data="admin:panel")]]
    )


def masters_list_kb(masters: list[User], lang: str) -> InlineKeyboardMarkup:
    rows = []
    for m in masters:
        status = "✅" if m.is_active else "⛔️"
        role = "👑" if m.is_admin else "🔧"
        rows.append([IB(text=f"{status} {role} {m.full_name}", callback_data=f"admin:master:{m.id}")])
    rows.append([IB(text=btn("back", lang), callback_data="admin:panel")])
    return _kb(rows)


def master_detail_kb(master: User, lang: str) -> InlineKeyboardMarkup:
    if master.is_active:
        toggle = IB(text=t("adm_btn_block", lang), callback_data=f"admin:block:{master.id}")
    else:
        toggle = IB(text=t("adm_btn_activate", lang), callback_data=f"admin:activate:{master.id}")
    return _kb(
        [
            [toggle],
            [IB(text=t("adm_btn_delete", lang), callback_data=f"admin:delete:{master.id}")],
            [IB(text=btn("back", lang), callback_data="admin:masters")],
        ]
    )


def approve_master_kb(master_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    return _kb(
        [
            [
                IB(text=t("adm_btn_approve", lang), callback_data=f"admin:activate:{master_id}"),
                IB(text=t("adm_btn_reject", lang), callback_data=f"admin:delete:{master_id}"),
            ]
        ]
    )


def settings_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb(
        [
            [IB(text=t("adm_btn_reminder", lang), callback_data="admin:rem")],
            [IB(text=btn("back", lang), callback_data="admin:panel")],
        ]
    )


def reminder_kb(cfg, lang: str) -> InlineKeyboardMarkup:
    target = t("rem_target_all" if cfg.target == "all" else "rem_target_admins", lang)
    toggle = "rem_btn_disable" if cfg.enabled else "rem_btn_enable"
    return _kb(
        [
            [IB(text=t(toggle, lang), callback_data="admin:rem:toggle")],
            [IB(text=t("rem_btn_time", lang, time=cfg.time_text), callback_data="admin:rem:time")],
            [IB(text=t("rem_btn_days", lang, days=cfg.overdue_days), callback_data="admin:rem:days")],
            [IB(text=t("rem_btn_target", lang, target=target), callback_data="admin:rem:target")],
            [IB(text=t("rem_btn_test", lang), callback_data="admin:rem:test")],
            [IB(text=btn("back", lang), callback_data="admin:settings")],
        ]
    )


REMINDER_TIMES = ("17:00", "18:00", "18:30", "19:00", "19:30", "20:00", "20:30", "21:00")


def reminder_time_kb(current: str, lang: str) -> InlineKeyboardMarkup:
    buttons = [
        IB(text=(f"• {v} •" if v == current else v), callback_data="admin:rem:at:" + v.replace(":", ""))
        for v in REMINDER_TIMES
    ]
    return _kb(
        [buttons[i : i + 4] for i in range(0, len(buttons), 4)]
        + [[IB(text=t("rem_btn_custom", lang), callback_data="admin:rem:custom")]]
        + [[IB(text=btn("back", lang), callback_data="admin:rem")]]
    )


def reminder_days_kb(current: int, lang: str) -> InlineKeyboardMarkup:
    row = [
        IB(text=(f"• {d} •" if d == current else str(d)), callback_data=f"admin:rem:d:{d}")
        for d in (1, 2, 3, 5, 7, 10)
    ]
    return _kb([row[:3], row[3:], [IB(text=btn("back", lang), callback_data="admin:rem")]])


def back_to_panel_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb([[IB(text=btn("back", lang), callback_data="admin:panel")]])


def broadcast_target_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb(
        [
            [IB(text=t("bc_btn_masters", lang), callback_data="admin:bc:masters")],
            [IB(text=t("bc_btn_group", lang), callback_data="admin:bc:group")],
            [IB(text=btn("back", lang), callback_data="admin:panel")],
        ]
    )


def broadcast_confirm_kb(lang: str) -> InlineKeyboardMarkup:
    return _kb(
        [
            [
                IB(text=btn("confirm", lang), callback_data="admin:bc:send"),
                IB(text=btn("cancel", lang), callback_data="admin:bc:cancel"),
            ]
        ]
    )
