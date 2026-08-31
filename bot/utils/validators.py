"""Foydalanuvchi kiritgan ma'lumotlarni tekshirish."""

import re


def parse_order_number(text: str) -> int | None:
    """'#27', '27', ' 27 ' ko'rinishlarini qabul qiladi; noto'g'ri bo'lsa None."""
    cleaned = text.strip().lstrip("#").strip()
    if not cleaned.isdigit():
        return None
    number = int(cleaned)
    if number <= 0 or number > 10_000_000:
        return None
    return number


def parse_price(text: str) -> int | None:
    """'250000', '250 000', '250.000' ko'rinishlarini qabul qiladi."""
    cleaned = re.sub(r"[ .,' ]", "", text.strip())
    if not cleaned.isdigit():
        return None
    price = int(cleaned)
    if price <= 0 or price > 1_000_000_000:
        return None
    return price


def parse_phone(text: str) -> str | None:
    """'+998 90 123-45-67' → '+998901234567'; noto'g'ri bo'lsa None."""
    cleaned = re.sub(r"[ \-()]", "", text.strip())
    if re.fullmatch(r"\+?\d{7,15}", cleaned):
        return cleaned
    return None


def valid_description(text: str) -> str | None:
    """Vazifa tavsifi: 3–500 belgi."""
    desc = text.strip()
    if 3 <= len(desc) <= 500:
        return desc
    return None


def valid_name(text: str) -> str | None:
    """Ism: 2–50 belgi, bo'sh emas."""
    name = " ".join(text.split())
    if 2 <= len(name) <= 50:
        return name
    return None
