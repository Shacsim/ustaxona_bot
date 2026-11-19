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


def parse_amount(text: str, allow_zero: bool = False) -> int | None:
    """Pul summasi (so'm): '250000', '250 000'; allow_zero bo'lsa 0 ham mumkin."""
    cleaned = re.sub(r"[ .,' ]", "", text.strip())
    if not cleaned.isdigit():
        return None
    value = int(cleaned)
    if value > 1_000_000_000 or (value == 0 and not allow_zero):
        return None
    return value


def parse_qty(text: str) -> int | None:
    """Mahsulot soni: 1–100000 butun son."""
    cleaned = text.strip().replace(" ", "")
    if not cleaned.isdigit():
        return None
    qty = int(cleaned)
    if 1 <= qty <= 100_000:
        return qty
    return None


def valid_product_name(text: str) -> str | None:
    name = " ".join(text.split())
    if 2 <= len(name) <= 100:
        return name
    return None


def parse_phone(text: str) -> str | None:
    """Telefonni yagona ko'rinishga keltiradi; noto'g'ri bo'lsa None.

    '+998 90 123-45-67' → '+998901234567'
    '90 123 45 67' / '901234567' (O'zbekiston, 9 raqam) → '+998901234567'
    '998901234567' → '+998901234567'
    Boshqa xalqaro raqamlar: 7–15 raqam, boshida + qo'yiladi.
    """
    cleaned = re.sub(r"[\s\-().]", "", text.strip())
    if not re.fullmatch(r"\+?\d{7,15}", cleaned):
        return None
    digits = cleaned.lstrip("+")
    if len(digits) == 9 and not cleaned.startswith("+"):
        return "+998" + digits
    return "+" + digits


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
