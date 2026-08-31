"""users jadvaliga language ustuni (uz/ru).

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-01

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("language", sa.String(length=2), nullable=False, server_default="uz"),
    )


def downgrade() -> None:
    op.drop_column("users", "language")
