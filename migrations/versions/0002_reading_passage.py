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

TABLE = "lessons"
COLUMN = "reading_passage"


def _co_cot(bind) -> bool:
    return COLUMN in {c["name"] for c in sa.inspect(bind).get_columns(TABLE)}


def upgrade() -> None:
    # 0001 dung `Base.metadata.create_all`, tuc la no luon dung metadata MOI NHAT. Tren mot
    # database trong, 0001 da tao san cot nay roi; tren database co san tu truoc thi chua.
    # Kiem tra truoc khi them de ca hai duong deu chay duoc.
    bind = op.get_bind()
    if _co_cot(bind):
        return
    op.add_column(
        TABLE, sa.Column(COLUMN, sa.JSON(), nullable=False, server_default="{}")
    )


def downgrade() -> None:
    bind = op.get_bind()
    if _co_cot(bind):
        op.drop_column(TABLE, COLUMN)
