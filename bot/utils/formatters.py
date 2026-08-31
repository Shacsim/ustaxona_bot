"""Xabar shablonlari va formatlash. Barcha matnlar HTML parse mode uchun."""

from datetime import datetime, timedelta, timezone
from html import escape

from config import settings
from database.models import Order, OrderStatus

# Toshkent vaqti (UTC+5)
TZ = timezone(timedelta(hours=5))


def fmt_dt(dt: datetime | None) -> str:
    if dt is None:
        return "—"
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(TZ).strftime("%d.%m.%Y %H:%M")


def fmt_price(price: int | None) -> str:
    if price is None:
        return "—"
    return f"{price:,}".replace(",", " ") + " so'm"


def fmt_work_done(work_done: str) -> str:
    """Har bir qatorni • bilan ro'yxatga aylantiradi."""
    lines = [ln.strip().lstrip("•-*").strip() for ln in work_done.splitlines()]
    lines = [ln for ln in lines if ln]
    return "\n".join(f"• {escape(ln)}" for ln in lines)


STATUS_LABELS = {
    "uz": {
        OrderStatus.PENDING: "⏳ KUTILMOQDA",
        OrderStatus.READY: "✅ TAYYOR",
        OrderStatus.CANCELLED: "❌ BEKOR QILINGAN",
    },
    "ru": {
        OrderStatus.PENDING: "⏳ В ОЖИДАНИИ",
        OrderStatus.READY: "✅ ГОТОВ",
        OrderStatus.CANCELLED: "❌ ОТМЕНЁН",
    },
}

CARD_LABELS = {
    "uz": {
        "title": "📋 <b>BUYURTMA #{n}</b>",
        "status": "Holati",
        "customer": "👤 Mijoz",
        "phone": "📞 Telefon",
        "task": "🔧 Vazifa",
        "created_by": "👨‍🔧 Qabul qilgan usta",
        "completed_by": "👨‍🔧 Tayyorlagan usta",
        "work": "🔧 <b>Bajarilgan ishlar:</b>",
        "price": "💰 Xizmat haqqi",
        "created": "📅 Qabul qilingan",
        "completed": "📅 Tayyorlangan",
    },
    "ru": {
        "title": "📋 <b>ЗАКАЗ #{n}</b>",
        "status": "Статус",
        "customer": "👤 Клиент",
        "phone": "📞 Телефон",
        "task": "🔧 Задача",
        "created_by": "👨‍🔧 Принял мастер",
        "completed_by": "👨‍🔧 Выполнил мастер",
        "work": "🔧 <b>Выполненные работы:</b>",
        "price": "💰 Стоимость",
        "created": "📅 Принят",
        "completed": "📅 Готов",
    },
}


def pending_group_text(order: Order) -> str:
    """«Kutayotgan buyurtmalar» topic'iga yuboriladigan xabar (3 tilda).

    Mazmuni: buyurtma qabul qilindi + tayyor bo'lganda «TAYYOR BUYURTMALAR»
    bo'limida e'lon qilinishini bildiradi.
    """
    master = escape(order.creator.full_name)
    n = order.order_number
    return (
        "📥 <b>BUYURTMA QABUL QILINDI</b>\n"
        f"🔢 Buyurtma raqami: <b>#{n}</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🇺🇿 Assalomu alaykum, hurmatli mijoz!\n"
        f"Sizning <b>#{n}</b> raqamli buyurtmangiz muvaffaqiyatli qabul qilindi, "
        "ustalarimiz ishni boshladi. 🔧\n"
        "⏳ Buyurtmangiz tayyor bo'lishi bilan "
        "«✅ TAYYOR BUYURTMALAR» bo'limida e'lon qilamiz.\n"
        "Bizni tanlaganingizdan xursandmiz! ❤️\n\n"
        "🇷🇺 Здравствуйте, уважаемый клиент!\n"
        f"Ваш заказ <b>#{n}</b> успешно принят, наши мастера уже приступили к работе. 🔧\n"
        "⏳ Как только заказ будет готов, мы сообщим об этом "
        "в разделе «✅ TAYYOR BUYURTMALAR».\n"
        "Спасибо, что выбрали нас! ❤️\n\n"
        "🇬🇧 Hello, dear customer!\n"
        f"Your order <b>#{n}</b> has been received and our technicians have started "
        "working on it. 🔧\n"
        "⏳ As soon as it is ready, we will announce it "
        "in the «✅ TAYYOR BUYURTMALAR» topic.\n"
        "Thank you for choosing us! ❤️\n\n"
        "━━━━━━━━━━━━━━━━━━\n"
        f"👨‍🔧 Mas'ul usta / Мастер / Technician: <b>{master}</b>\n"
        f"🕐 Qabul qilindi / Принят / Received: {fmt_dt(order.created_at)}"
    )


def ready_group_text(order: Order) -> str:
    """«Tayyor buyurtmalar» topic'iga yuboriladigan xabar (3 tilda)."""
    master = escape(
        order.completer.full_name if order.completer else order.creator.full_name
    )
    return (
        "━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>#{order.order_number} — TAYYOR / ГОТОВ / READY</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🇺🇿 🎉 Buyurtmangiz tayyor! Olib ketishingiz mumkin.\n"
        "🇷🇺 🎉 Ваш заказ готов! Можете забирать.\n"
        "🇬🇧 🎉 Your order is ready for pickup!\n\n"
        "🔧 <b>Bajarilgan ishlar / Выполненные работы / Work done:</b>\n"
        f"{fmt_work_done(order.work_done or '')}\n\n"
        "💰 <b>Xizmat haqqi / Стоимость / Price:</b>\n"
        f"{fmt_price(order.price)}\n\n"
        f"👨‍🔧 Usta / Мастер / Technician: <b>{master}</b>\n"
        f"🕐 {fmt_dt(order.completed_at)}\n\n"
        "Bizni tanlaganingiz uchun tashakkur! ❤️\n"
        "Спасибо, что выбрали нас! ❤️\n"
        "Thank you for choosing us! ❤️\n"
        "━━━━━━━━━━━━━━━━━━"
    )


def pending_done_note(order: Order) -> str:
    """Buyurtma tayyor bo'lganda eski «kutayotgan» xabarga yangilangan matn."""
    return (
        f"✅ <b>#{order.order_number} — TAYYOR / ГОТОВ / READY</b>\n\n"
        "🇺🇿 Buyurtma yakunlandi — batafsil «✅ TAYYOR BUYURTMALAR» bo'limida.\n"
        "🇷🇺 Заказ завершён — подробности в разделе «✅ TAYYOR BUYURTMALAR».\n"
        "🇬🇧 Order completed — see the «✅ TAYYOR BUYURTMALAR» topic.\n\n"
        f"🕐 {fmt_dt(order.completed_at)}"
    )


def order_card(order: Order, lang: str = "uz") -> str:
    """Usta uchun buyurtma kartochkasi (qidiruv/ro'yxat)."""
    lbl = CARD_LABELS.get(lang, CARD_LABELS["uz"])
    status = STATUS_LABELS.get(lang, STATUS_LABELS["uz"]).get(
        order.status, order.status
    )
    lines = [
        lbl["title"].format(n=order.order_number),
        "",
        f"{lbl['status']}: <b>{status}</b>",
        "",
    ]
    if order.customer_name:
        lines.append(f"{lbl['customer']}: <b>{escape(order.customer_name)}</b>")
    if order.customer_phone:
        lines.append(f"{lbl['phone']}: <code>{escape(order.customer_phone)}</code>")
    if order.description:
        lines.append(f"{lbl['task']}: {escape(order.description)}")
    if order.customer_name or order.customer_phone or order.description:
        lines.append("")
    lines.append(f"{lbl['created_by']}: {escape(order.creator.full_name)}")
    if order.completer:
        lines.append(f"{lbl['completed_by']}: {escape(order.completer.full_name)}")
    if order.work_done:
        lines += ["", lbl["work"], fmt_work_done(order.work_done)]
    if order.price:
        lines += ["", f"{lbl['price']}: <b>{fmt_price(order.price)}</b>"]
    lines += ["", f"{lbl['created']}: {fmt_dt(order.created_at)}"]
    if order.completed_at:
        lines.append(f"{lbl['completed']}: {fmt_dt(order.completed_at)}")
    return "\n".join(lines)


def about_text() -> str:
    """«Biz haqimizda» bo'limi matni — .env dagi ma'lumotlardan."""
    parts = [
        f"🖥 <b>{escape(settings.workshop_name)}</b>",
        "",
        "Sizning texnikangiz — bizning mas'uliyatimiz!",
        "",
    ]
    if settings.workshop_phone:
        parts.append("📞 <b>Telefon:</b>")
        # Vergul bilan ajratilgan bir nechta raqam — har biri alohida qatorda
        for phone in settings.workshop_phone.split(","):
            if phone.strip():
                parts.append(escape(phone.strip()))
        parts.append("")
    if settings.workshop_address:
        parts += ["📍 <b>Manzil:</b>", escape(settings.workshop_address), ""]
    if settings.workshop_working_hours:
        parts += ["🕐 <b>Ish vaqti:</b>", escape(settings.workshop_working_hours), ""]
    parts.append("Bizni tanlaganingiz uchun rahmat!")
    return "\n".join(parts)
