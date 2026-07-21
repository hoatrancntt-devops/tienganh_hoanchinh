"""them cot lessons.reading_passage

Van ban de DOC, tach khoi `dialogue`. Co y khong co truong audio: bai doc phat duoc tieng
thi hoc vien se nghe thay vi doc.

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-21
"""
import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "lessons",
        sa.Column("reading_passage", sa.JSON(), nullable=False, server_default="{}"),
    )


def downgrade() -> None:
    op.drop_column("lessons", "reading_passage")
