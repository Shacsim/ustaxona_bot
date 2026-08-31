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
    OrderStatus.PENDING: "⏳ KUTILMOQDA",
    OrderStatus.READY: "✅ TAYYOR",
    OrderStatus.CANCELLED: "❌ BEKOR QILINGAN",
}


def pending_group_text(order: Order) -> str:
    """«Kutayotgan buyurtmalar» topic'iga yuboriladigan xabar."""
    master = escape(order.creator.full_name)
    return (
        "📥 <b>BUYURTMA QABUL QILINDI</b>\n\n"
        f"🔢 Buyurtma raqami: <b>#{order.order_number}</b>\n\n"
        "Assalomu alaykum!\n\n"
        "Buyurtmangiz ustalarimiz tomonidan qabul qilindi.\n\n"
        "🔧 Hozirda qurilmangiz diagnostika va ta'mirlash jarayonida.\n\n"
        "⏳ Iltimos, biroz sabr qiling.\n\n"
        "Sizning ishonchingiz biz uchun juda muhim.\n"
        "Bizni tanlaganingizdan xursandmiz! ❤️\n\n"
        f"👨‍🔧 Mas'ul usta: <b>{master}</b>\n"
        f"🕐 Qabul qilingan vaqt: {fmt_dt(order.created_at)}"
    )


def ready_group_text(order: Order) -> str:
    """«Tayyor buyurtmalar» topic'iga yuboriladigan xabar."""
    master = escape(
        order.completer.full_name if order.completer else order.creator.full_name
    )
    return (
        "━━━━━━━━━━━━━━━━━━\n"
        "✅ <b>BUYURTMA TAYYOR</b>\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        f"🔢 Buyurtma raqami: <b>#{order.order_number}</b>\n\n"
        "🎉 Buyurtmangiz tayyor!\n\n"
        "🔧 <b>Bajarilgan ishlar:</b>\n\n"
        f"{fmt_work_done(order.work_done or '')}\n\n"
        f"💰 <b>Xizmat haqqi:</b>\n{fmt_price(order.price)}\n\n"
        f"👨‍🔧 <b>Mas'ul usta:</b>\n{master}\n\n"
        f"🕐 <b>Tayyor bo'lgan vaqt:</b>\n{fmt_dt(order.completed_at)}\n\n"
        "📌 Buyurtmangizni olib ketishingiz mumkin.\n\n"
        "Bizni tanlaganingiz uchun tashakkur!\n"
        "Sizning ishonchingiz biz uchun juda muhim. ❤️\n"
        "━━━━━━━━━━━━━━━━━━"
    )


def pending_done_note(order: Order) -> str:
    """Buyurtma tayyor bo'lganda eski «kutayotgan» xabarga yangilangan matn."""
    return (
        f"✅ <b>BUYURTMA #{order.order_number} TAYYOR BO'LDI</b>\n\n"
        "Ushbu buyurtma yakunlandi.\n"
        "Batafsil ma'lumot «✅ TAYYOR BUYURTMALAR» bo'limida.\n\n"
        f"🕐 {fmt_dt(order.completed_at)}"
    )


def order_card(order: Order) -> str:
    """Usta uchun buyurtma kartochkasi (qidiruv/ro'yxat)."""
    lines = [
        f"📋 <b>BUYURTMA #{order.order_number}</b>",
        "",
        f"Holati: <b>{STATUS_LABELS.get(order.status, order.status)}</b>",
        "",
        f"👨‍🔧 Qabul qilgan usta: {escape(order.creator.full_name)}",
    ]
    if order.completer:
        lines.append(f"👨‍🔧 Tayyorlagan usta: {escape(order.completer.full_name)}")
    if order.work_done:
        lines += ["", "🔧 <b>Bajarilgan ishlar:</b>", fmt_work_done(order.work_done)]
    if order.price:
        lines += ["", f"💰 Xizmat haqqi: <b>{fmt_price(order.price)}</b>"]
    lines += ["", f"📅 Qabul qilingan: {fmt_dt(order.created_at)}"]
    if order.completed_at:
        lines.append(f"📅 Tayyorlangan: {fmt_dt(order.completed_at)}")
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
