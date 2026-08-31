"""Anonim savollar jadvali.

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-01

"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asker_id", sa.BigInteger(), nullable=False),
        sa.Column("language", sa.String(length=2), nullable=False, server_default="uz"),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("group_message_id", sa.BigInteger(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_questions_group_message_id", "questions", ["group_message_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_questions_group_message_id", table_name="questions")
    op.drop_table("questions")
