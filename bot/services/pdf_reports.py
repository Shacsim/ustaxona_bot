"""PDF hisobotlar (fpdf2 + DejaVu shrifti — lotin, kirill, o'zbekcha belgilar).

PDF'da emoji ishlatilmaydi (shriftda yo'q). Barcha funksiyalar tayyor
PDF baytlarini qaytaradi — handler ularni BufferedInputFile qilib yuboradi.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from fpdf import FPDF
from fpdf.fonts import FontFace

from bot.utils.formatters import fmt_dt, now_local, to_local, wait_days
from config import settings
from database.models import Order, Product, StockMove

FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"

INK = (31, 41, 55)
MUTED = (107, 114, 128)
ACCENT = (37, 99, 235)
HEAD_FILL = (229, 236, 251)
ZEBRA = (247, 248, 250)

L = {
    "uz": {
        "generated": "Tuzilgan",
        "page": "Sahifa",
        "currency": "so'm",
        "pending_title": "Kutayotgan buyurtmalar",
        "ready_title": "Tayyor buyurtmalar",
        "master_title": "Usta hisoboti",
        "daily_title": "Kunlik hisobot",
        "period": "Davr",
        "master": "Usta",
        "count": "Soni",
        "total": "Jami",
        "no": "No",
        "date": "Sana",
        "waiting": "Kutmoqda",
        "days": "kun",
        "customer": "Mijoz",
        "phone": "Telefon",
        "task": "Nima qilish kerak",
        "work": "Bajarilgan ishlar",
        "amount": "Summa",
        "accepted_by": "Qabul qilgan",
        "completed_by": "Tayyorlagan",
        "ready_at": "Tayyor bo'lgan",
        "s_summary": "Qisqacha",
        "s_orders": "Tayyorlangan buyurtmalar",
        "s_sales": "Ombordan sotilganlar",
        "s_buys": "Sotib olinganlar (kirim)",
        "s_stock": "Ombordagi qoldiq (hozir)",
        "product": "Mahsulot",
        "qty": "Soni",
        "price": "Narxi",
        "cost": "Tannarx",
        "value": "Qiymati",
        "profit": "Foyda",
        "datetime": "Sana va vaqt",
        "none": "Yozuvlar yo'q",
        "income_orders": "Buyurtmalardan daromad",
        "sales_sum": "Ombordan sotuv",
        "sales_profit": "Sotuvdan foyda",
        "buys_sum": "Sotib olingan mahsulotlar",
        "stock_value": "Ombor qiymati",
        "pending_now": "Hozir kutayotgan buyurtmalari",
        "pcs": "dona",
    },
    "ru": {
        "generated": "Сформирован",
        "page": "Стр.",
        "currency": "сум",
        "pending_title": "Заказы в ожидании",
        "ready_title": "Готовые заказы",
        "master_title": "Отчёт мастера",
        "daily_title": "Ежедневный отчёт",
        "period": "Период",
        "master": "Мастер",
        "count": "Кол-во",
        "total": "Итого",
        "no": "№",
        "date": "Дата",
        "waiting": "Ждёт",
        "days": "дн.",
        "customer": "Клиент",
        "phone": "Телефон",
        "task": "Что сделать",
        "work": "Выполненные работы",
        "amount": "Сумма",
        "accepted_by": "Принял",
        "completed_by": "Выполнил",
        "ready_at": "Готов",
        "s_summary": "Кратко",
        "s_orders": "Выполненные заказы",
        "s_sales": "Продажи со склада",
        "s_buys": "Покупки (приход)",
        "s_stock": "Остатки на складе (сейчас)",
        "product": "Товар",
        "qty": "Кол-во",
        "price": "Цена",
        "cost": "Себест.",
        "value": "Стоимость",
        "profit": "Прибыль",
        "datetime": "Дата и время",
        "none": "Записей нет",
        "income_orders": "Доход по заказам",
        "sales_sum": "Продажи со склада",
        "sales_profit": "Прибыль от продаж",
        "buys_sum": "Куплено товаров",
        "stock_value": "Стоимость склада",
        "pending_now": "Заказов в ожидании сейчас",
        "pcs": "шт.",
    },
    "en": {
        "generated": "Generated",
        "page": "Page",
        "currency": "UZS",
        "pending_title": "Pending orders",
        "ready_title": "Ready orders",
        "master_title": "Technician report",
        "daily_title": "Daily report",
        "period": "Period",
        "master": "Technician",
        "count": "Count",
        "total": "Total",
        "no": "No",
        "date": "Date",
        "waiting": "Waiting",
        "days": "d",
        "customer": "Customer",
        "phone": "Phone",
        "task": "What to do",
        "work": "Work done",
        "amount": "Amount",
        "accepted_by": "Accepted by",
        "completed_by": "Completed by",
        "ready_at": "Ready at",
        "s_summary": "Summary",
        "s_orders": "Completed orders",
        "s_sales": "Stock sales",
        "s_buys": "Purchases (stock in)",
        "s_stock": "Current stock",
        "product": "Product",
        "qty": "Qty",
        "price": "Price",
        "cost": "Cost",
        "value": "Value",
        "profit": "Profit",
        "datetime": "Date & time",
        "none": "No entries",
        "income_orders": "Income from orders",
        "sales_sum": "Stock sales",
        "sales_profit": "Profit from sales",
        "buys_sum": "Products bought",
        "stock_value": "Stock value",
        "pending_now": "Pending orders right now",
        "pcs": "pcs",
    },
}


def _lbl(lang: str) -> dict[str, str]:
    return L.get(lang, L["uz"])


def money(value: int | None) -> str:
    if value is None:
        return "—"
    return f"{value:,}".replace(",", " ")


def _clean(text: str | None) -> str:
    """PDF uchun: emoji va boshqa shriftda yo'q belgilarni olib tashlaydi."""
    if not text:
        return "—"
    out = []
    for ch in text:
        cp = ord(ch)
        if cp >= 0x1F000 or 0x2600 <= cp <= 0x27BF or cp in (0xFE0F, 0x200D):
            continue
        out.append(ch)
    return "".join(out).strip() or "—"


class _Doc(FPDF):
    def __init__(self, title: str, subtitle: str, lang: str, landscape: bool = False) -> None:
        super().__init__(orientation="L" if landscape else "P", unit="mm", format="A4")
        self.lang = lang
        self.doc_title = title
        self.doc_subtitle = subtitle
        self.add_font("DejaVu", "", str(FONT_DIR / "DejaVuSans.ttf"))
        self.add_font("DejaVu", "B", str(FONT_DIR / "DejaVuSans-Bold.ttf"))
        self.set_margins(10, 12, 10)
        self.set_auto_page_break(True, margin=14)
        self.set_title(title)
        self.set_author(settings.workshop_name)
        self.set_creator("Ustaxona bot")
        self.add_page()

    def header(self) -> None:
        lb = _lbl(self.lang)
        self.set_fill_color(*INK)
        self.rect(0, 0, self.w, 24, style="F")
        self.set_xy(10, 5)
        self.set_text_color(255, 255, 255)
        self.set_font("DejaVu", "B", 15)
        self.cell(0, 7, _clean(self.doc_title))
        self.set_xy(10, 13)
        self.set_font("DejaVu", "", 9)
        self.cell(0, 5, _clean(self.doc_subtitle))
        self.set_xy(10, 5)
        self.set_font("DejaVu", "B", 9)
        self.cell(0, 6, _clean(settings.workshop_name), align="R")
        self.set_xy(10, 13)
        self.set_font("DejaVu", "", 8)
        self.cell(0, 5, f"{lb['generated']}: {now_local().strftime('%d.%m.%Y %H:%M')}", align="R")
        self.set_text_color(*INK)
        self.set_y(30)

    def footer(self) -> None:
        lb = _lbl(self.lang)
        self.set_y(-10)
        self.set_font("DejaVu", "", 7)
        self.set_text_color(*MUTED)
        self.cell(0, 5, f"{lb['page']} {self.page_no()}/{{nb}}", align="C")
        self.set_text_color(*INK)

    # ---- bloklar ----

    def section(self, title: str) -> None:
        if self.get_y() > self.h - 40:
            self.add_page()
        self.ln(3)
        self.set_font("DejaVu", "B", 11)
        self.set_text_color(*ACCENT)
        self.cell(0, 7, _clean(title), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*ACCENT)
        self.set_line_width(0.4)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)
        self.set_text_color(*INK)

    def kv_rows(self, rows: list[tuple[str, str]]) -> None:
        self.set_font("DejaVu", "", 9.5)
        for k, v in rows:
            self.set_text_color(*MUTED)
            self.cell(80, 6.2, _clean(k))
            self.set_text_color(*INK)
            self.set_font("DejaVu", "B", 9.5)
            self.cell(0, 6.2, _clean(v), new_x="LMARGIN", new_y="NEXT")
            self.set_font("DejaVu", "", 9.5)

    def empty(self, text: str) -> None:
        self.set_font("DejaVu", "", 9)
        self.set_text_color(*MUTED)
        self.cell(0, 6, _clean(text), new_x="LMARGIN", new_y="NEXT")
        self.set_text_color(*INK)

    def grid(
        self,
        headers: list[str],
        rows: list[list[str]],
        widths: tuple[float, ...],
        align: tuple[str, ...],
        total: list[str] | None = None,
    ) -> None:
        self.set_font("DejaVu", "", 8.5)
        self.set_draw_color(220, 223, 228)
        self.set_line_width(0.2)
        head_style = FontFace(emphasis="BOLD", fill_color=HEAD_FILL, color=INK)
        with self.table(
            col_widths=widths,
            text_align=align,
            headings_style=head_style,
            line_height=5,
            cell_fill_color=ZEBRA,
            cell_fill_mode="ROWS",
            padding=1.4,
            first_row_as_headings=True,
            width=self.w - self.l_margin - self.r_margin,
        ) as table:
            r = table.row()
            for h in headers:
                r.cell(_clean(h))
            for row in rows:
                r = table.row()
                for value in row:
                    r.cell(_clean(value))
            if total:
                r = table.row(style=FontFace(emphasis="BOLD", fill_color=HEAD_FILL))
                for value in total:
                    r.cell(_clean(value) if value else "")

    def output_bytes(self) -> bytes:
        self.alias_nb_pages()
        return bytes(self.output())


# ---------- Buyurtmalar ----------


def pending_pdf(orders: list[Order], lang: str) -> bytes:
    lb = _lbl(lang)
    doc = _Doc(lb["pending_title"], f"{lb['count']}: {len(orders)}", lang, landscape=True)
    if not orders:
        doc.empty(lb["none"])
        return doc.output_bytes()
    rows = [
        [
            f"#{o.order_number}",
            fmt_dt(o.created_at),
            f"{wait_days(o.created_at)} {lb['days']}",
            o.customer_name or "—",
            o.customer_phone or "—",
            o.description or "—",
            o.creator.full_name if o.creator else "—",
        ]
        for o in orders
    ]
    doc.grid(
        [lb["no"], lb["date"], lb["waiting"], lb["customer"], lb["phone"], lb["task"], lb["accepted_by"]],
        rows,
        widths=(14, 30, 20, 42, 34, 99, 38),
        align=("CENTER", "LEFT", "CENTER", "LEFT", "LEFT", "LEFT", "LEFT"),
    )
    return doc.output_bytes()


def ready_pdf(orders: list[Order], period_label: str, lang: str) -> bytes:
    lb = _lbl(lang)
    total = sum(o.price or 0 for o in orders)
    subtitle = (
        f"{lb['period']}: {period_label}  ·  {lb['count']}: {len(orders)}  ·  "
        f"{lb['total']}: {money(total)} {lb['currency']}"
    )
    doc = _Doc(lb["ready_title"], subtitle, lang, landscape=True)
    if not orders:
        doc.empty(lb["none"])
        return doc.output_bytes()
    rows = []
    for o in orders:
        master = o.completer or o.creator
        rows.append(
            [
                f"#{o.order_number}",
                fmt_dt(o.completed_at),
                o.customer_name or "—",
                o.customer_phone or "—",
                (o.work_done or "—").replace("\n", "; "),
                master.full_name if master else "—",
                money(o.price),
            ]
        )
    doc.grid(
        [lb["no"], lb["ready_at"], lb["customer"], lb["phone"], lb["work"], lb["completed_by"],
         f"{lb['amount']}, {lb['currency']}"],
        rows,
        widths=(14, 30, 38, 32, 98, 34, 31),
        align=("CENTER", "LEFT", "LEFT", "LEFT", "LEFT", "LEFT", "RIGHT"),
        total=["", "", "", "", "", lb["total"], money(total)],
    )
    return doc.output_bytes()


# ---------- Usta hisoboti (kunlik / ombor) ----------


@dataclass
class MasterReport:
    master_name: str
    period_label: str
    orders_done: list[Order] = field(default_factory=list)
    sales: list[StockMove] = field(default_factory=list)
    purchases: list[StockMove] = field(default_factory=list)
    stock: list[Product] = field(default_factory=list)
    pending_count: int = 0
    daily: bool = False


def master_pdf(rep: MasterReport, lang: str) -> bytes:
    lb = _lbl(lang)
    cur = lb["currency"]
    title = lb["daily_title"] if rep.daily else lb["master_title"]
    doc = _Doc(title, f"{lb['master']}: {rep.master_name}  ·  {lb['period']}: {rep.period_label}", lang)

    income = sum(o.price or 0 for o in rep.orders_done)
    sales_sum = sum(m.total for m in rep.sales)
    profit = sum(m.profit for m in rep.sales)
    buys_sum = sum(m.total for m in rep.purchases)
    stock_units = sum(p.quantity for p in rep.stock)
    stock_value = sum(p.quantity * p.avg_cost for p in rep.stock)

    doc.section(lb["s_summary"])
    doc.kv_rows(
        [
            (lb["income_orders"], f"{money(income)} {cur}  ({len(rep.orders_done)})"),
            (lb["sales_sum"], f"{money(sales_sum)} {cur}  ({sum(m.quantity for m in rep.sales)} {lb['pcs']})"),
            (lb["sales_profit"], f"{money(profit)} {cur}"),
            (lb["buys_sum"], f"{money(buys_sum)} {cur}  ({sum(m.quantity for m in rep.purchases)} {lb['pcs']})"),
            (lb["stock_value"], f"{money(stock_value)} {cur}  ({stock_units} {lb['pcs']})"),
            (lb["pending_now"], str(rep.pending_count)),
        ]
    )

    doc.section(lb["s_orders"])
    if rep.orders_done:
        doc.grid(
            [lb["no"], lb["ready_at"], lb["customer"], lb["work"], f"{lb['amount']}, {cur}"],
            [
                [
                    f"#{o.order_number}",
                    fmt_dt(o.completed_at),
                    o.customer_name or "—",
                    (o.work_done or "—").replace("\n", "; "),
                    money(o.price),
                ]
                for o in rep.orders_done
            ],
            widths=(14, 28, 36, 82, 30),
            align=("CENTER", "LEFT", "LEFT", "LEFT", "RIGHT"),
            total=["", "", "", lb["total"], money(income)],
        )
    else:
        doc.empty(lb["none"])

    doc.section(lb["s_sales"])
    if rep.sales:
        doc.grid(
            [lb["datetime"], lb["product"], lb["qty"], lb["price"], lb["total"], lb["profit"]],
            [
                [
                    to_local(m.created_at).strftime("%d.%m.%Y %H:%M"),
                    m.product.name,
                    str(m.quantity),
                    money(m.unit_price),
                    money(m.total),
                    money(m.profit),
                ]
                for m in sorted(rep.sales, key=lambda m: m.created_at)
            ],
            widths=(32, 62, 16, 26, 28, 26),
            align=("LEFT", "LEFT", "CENTER", "RIGHT", "RIGHT", "RIGHT"),
            total=["", lb["total"], str(sum(m.quantity for m in rep.sales)), "", money(sales_sum), money(profit)],
        )
    else:
        doc.empty(lb["none"])

    doc.section(lb["s_buys"])
    if rep.purchases:
        doc.grid(
            [lb["datetime"], lb["product"], lb["qty"], lb["price"], lb["total"]],
            [
                [
                    to_local(m.created_at).strftime("%d.%m.%Y %H:%M"),
                    m.product.name,
                    str(m.quantity),
                    money(m.unit_price),
                    money(m.total),
                ]
                for m in sorted(rep.purchases, key=lambda m: m.created_at)
            ],
            widths=(32, 76, 18, 32, 32),
            align=("LEFT", "LEFT", "CENTER", "RIGHT", "RIGHT"),
            total=["", lb["total"], str(sum(m.quantity for m in rep.purchases)), "", money(buys_sum)],
        )
    else:
        doc.empty(lb["none"])

    doc.section(lb["s_stock"])
    if rep.stock:
        doc.grid(
            [lb["product"], lb["qty"], lb["cost"], lb["value"]],
            [
                [p.name, str(p.quantity), money(p.avg_cost), money(p.quantity * p.avg_cost)]
                for p in rep.stock
            ],
            widths=(96, 22, 36, 36),
            align=("LEFT", "CENTER", "RIGHT", "RIGHT"),
            total=[lb["total"], str(stock_units), "", money(stock_value)],
        )
    else:
        doc.empty(lb["none"])

    return doc.output_bytes()
