"""Usta ombori bilan ishlash — barcha SQL shu yerda.

Har bir usta faqat o'z omborini ko'radi va o'zgartiradi (owner_id).
Kirim o'rtacha tannarxni yangilaydi; sotuv o'sha paytdagi tannarxni
yozib qo'yadi — foyda shundan hisoblanadi.
"""

from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import MoveKind, Product, StockMove


def name_key(name: str) -> str:
    return " ".join(name.lower().split())


@dataclass
class MoveTotals:
    in_units: int = 0
    in_sum: int = 0
    out_units: int = 0
    out_sum: int = 0
    profit: int = 0


class InventoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ---------- Mahsulotlar ----------

    async def list_products(self, owner_id: int, in_stock_only: bool = False) -> list[Product]:
        q = select(Product).where(Product.owner_id == owner_id)
        if in_stock_only:
            q = q.where(Product.quantity > 0)
        q = q.order_by(Product.quantity.desc(), Product.name)
        return list((await self.session.execute(q)).scalars().all())

    async def get_product(self, owner_id: int, product_id: int) -> Product | None:
        product = await self.session.get(Product, product_id)
        if product is None or product.owner_id != owner_id:
            return None
        return product

    async def find_by_name(self, owner_id: int, name: str) -> Product | None:
        result = await self.session.execute(
            select(Product).where(
                Product.owner_id == owner_id, Product.name_key == name_key(name)
            )
        )
        return result.scalar_one_or_none()

    # ---------- Harakatlar ----------

    async def buy(
        self,
        owner_id: int,
        quantity: int,
        unit_price: int,
        product_id: int | None = None,
        new_name: str | None = None,
    ) -> tuple[Product, StockMove]:
        """Kirim: mavjud mahsulotga yoki yangi nom bilan (bor bo'lsa — o'shanga)."""
        product: Product | None = None
        if product_id is not None:
            product = await self.get_product(owner_id, product_id)
        elif new_name:
            product = await self.find_by_name(owner_id, new_name)
            if product is None:
                product = Product(
                    owner_id=owner_id,
                    name=" ".join(new_name.split()),
                    name_key=name_key(new_name),
                    quantity=0,
                    avg_cost=0,
                )
                self.session.add(product)
                await self.session.flush()
        if product is None:
            raise LookupError("product not found")

        old_qty, old_cost = product.quantity, product.avg_cost
        new_qty = old_qty + quantity
        product.avg_cost = round((old_qty * old_cost + quantity * unit_price) / new_qty)
        product.quantity = new_qty

        move = StockMove(
            owner_id=owner_id,
            product_id=product.id,
            kind=MoveKind.IN,
            quantity=quantity,
            unit_price=unit_price,
        )
        self.session.add(move)
        await self.session.commit()
        await self.session.refresh(product)
        await self.session.refresh(move)
        return product, move

    async def sell(
        self, owner_id: int, product_id: int, quantity: int, unit_price: int
    ) -> tuple[Product, StockMove]:
        """Sotuv. Qoldiq yetmasa ValueError."""
        product = await self.session.get(Product, product_id, with_for_update=True)
        if product is None or product.owner_id != owner_id:
            raise LookupError("product not found")
        if product.quantity < quantity:
            raise ValueError(product.quantity)
        product.quantity -= quantity
        move = StockMove(
            owner_id=owner_id,
            product_id=product.id,
            kind=MoveKind.OUT,
            quantity=quantity,
            unit_price=unit_price,
            unit_cost=product.avg_cost,
        )
        self.session.add(move)
        await self.session.commit()
        await self.session.refresh(product)
        await self.session.refresh(move)
        return product, move

    async def last_move(self, owner_id: int) -> StockMove | None:
        result = await self.session.execute(
            select(StockMove)
            .where(StockMove.owner_id == owner_id)
            .order_by(StockMove.created_at.desc(), StockMove.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def undo_move(self, owner_id: int, move_id: int) -> Product | None:
        """Harakatni bekor qiladi. Kirimni bekor qilish qoldiqni manfiy qilsa ValueError."""
        move = await self.session.get(StockMove, move_id)
        if move is None or move.owner_id != owner_id:
            return None
        product = await self.session.get(Product, move.product_id, with_for_update=True)
        if move.kind == MoveKind.IN:
            if product.quantity < move.quantity:
                raise ValueError("would go negative")
            new_qty = product.quantity - move.quantity
            if new_qty > 0:
                total_cost = product.quantity * product.avg_cost - move.quantity * move.unit_price
                product.avg_cost = max(0, round(total_cost / new_qty))
            product.quantity = new_qty
        else:
            product.quantity += move.quantity
        await self.session.delete(move)
        await self.session.commit()
        await self.session.refresh(product)
        return product

    async def list_moves(
        self,
        owner_id: int,
        kind: MoveKind | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int | None = None,
    ) -> list[StockMove]:
        q = select(StockMove).where(StockMove.owner_id == owner_id)
        if kind is not None:
            q = q.where(StockMove.kind == kind)
        if since is not None:
            q = q.where(StockMove.created_at >= since)
        if until is not None:
            q = q.where(StockMove.created_at < until)
        q = q.order_by(StockMove.created_at.desc(), StockMove.id.desc())
        if limit:
            q = q.limit(limit)
        return list((await self.session.execute(q)).scalars().all())

    async def totals(
        self, owner_id: int, since: datetime | None = None, until: datetime | None = None
    ) -> MoveTotals:
        totals = MoveTotals()
        for m in await self.list_moves(owner_id, since=since, until=until):
            if m.kind == MoveKind.IN:
                totals.in_units += m.quantity
                totals.in_sum += m.total
            else:
                totals.out_units += m.quantity
                totals.out_sum += m.total
                totals.profit += m.profit
        return totals

    async def stock_summary(self, owner_id: int) -> tuple[int, int, int]:
        """(mahsulot turlari, jami dona, tannarxdagi qiymat) — faqat qoldig'i borlar."""
        row = (
            await self.session.execute(
                select(
                    func.count(Product.id),
                    func.coalesce(func.sum(Product.quantity), 0),
                    func.coalesce(func.sum(Product.quantity * Product.avg_cost), 0),
                ).where(Product.owner_id == owner_id, Product.quantity > 0)
            )
        ).one()
        return int(row[0]), int(row[1]), int(row[2])

    async def count_products(self) -> int:
        return int(
            (await self.session.execute(select(func.count()).select_from(Product))).scalar_one()
        )
