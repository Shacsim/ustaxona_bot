"""Usta ombori (products, stock_moves) va bot_state jadvallari.

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-20

"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("name_key", sa.String(length=100), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_cost", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("owner_id", "name_key", name="uq_products_owner_name"),
    )
    op.create_index("ix_products_owner_id", "products", ["owner_id"])

    op.create_table(
        "stock_moves",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "owner_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.Integer(),
            sa.ForeignKey("products.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("kind", sa.String(length=8), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.BigInteger(), nullable=False),
        sa.Column("unit_cost", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_stock_moves_owner_id", "stock_moves", ["owner_id"])
    op.create_index("ix_stock_moves_product_id", "stock_moves", ["product_id"])
    op.create_index("ix_stock_moves_created_at", "stock_moves", ["created_at"])

    op.create_table(
        "bot_state",
        sa.Column("key", sa.String(length=64), primary_key=True),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("bot_state")
    op.drop_index("ix_stock_moves_created_at", table_name="stock_moves")
    op.drop_index("ix_stock_moves_product_id", table_name="stock_moves")
    op.drop_index("ix_stock_moves_owner_id", table_name="stock_moves")
    op.drop_table("stock_moves")
    op.drop_index("ix_products_owner_id", table_name="products")
    op.drop_table("products")
