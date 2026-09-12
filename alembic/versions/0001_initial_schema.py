"""initial schema: user, poll, polloption, vote

Revision ID: 0001
Revises:
Create Date: 2026-09-12

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_user_username", "user", ["username"], unique=True)
    op.create_index("ix_user_email", "user", ["email"], unique=True)

    op.create_table(
        "poll",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("question", sa.String(length=280), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_poll_created_by_id", "poll", ["created_by_id"])
    op.create_index("ix_poll_created_at", "poll", ["created_at"])

    op.create_table(
        "polloption",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("poll_id", sa.Integer(), sa.ForeignKey("poll.id"), nullable=False),
        sa.Column("text", sa.String(length=120), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_polloption_poll_id", "polloption", ["poll_id"])

    op.create_table(
        "vote",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("poll_id", sa.Integer(), sa.ForeignKey("poll.id"), nullable=False),
        sa.Column("option_id", sa.Integer(), sa.ForeignKey("polloption.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=True),
        sa.Column("guest_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_vote_poll_id", "vote", ["poll_id"])
    op.create_index("ix_vote_option_id", "vote", ["option_id"])

    # Bir kullanıcı (üye ya da misafir) bir ankette yalnızca 1 kez oy kullanabilir.
    # Partial unique index: SQLModel/SQLAlchemy Core seviyesinde ifade edilemediği
    # için burada elle tanımlanıyor (bkz. docs/kararsizim-proje-plani.md, Bölüm 7).
    op.create_index(
        "unique_vote_per_user_per_poll",
        "vote",
        ["poll_id", "user_id"],
        unique=True,
        postgresql_where=sa.text("user_id IS NOT NULL"),
    )
    op.create_index(
        "unique_vote_per_guest_per_poll",
        "vote",
        ["poll_id", "guest_id"],
        unique=True,
        postgresql_where=sa.text("guest_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_table("vote")
    op.drop_table("polloption")
    op.drop_table("poll")
    op.drop_table("user")
