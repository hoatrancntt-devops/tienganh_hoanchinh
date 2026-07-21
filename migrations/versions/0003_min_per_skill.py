"""them cot lessons.min_per_skill

Nguong toi thieu tung ky nang o checkpoint. Diem tong co the che mot ky nang yeu:
doc 90 keo noi 40 len van qua nguong chung.

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-21
"""
import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None

TABLE = "lessons"
COLUMN = "min_per_skill"


def _co_cot(bind) -> bool:
    return COLUMN in {c["name"] for c in sa.inspect(bind).get_columns(TABLE)}


def upgrade() -> None:
    # 0001 dung create_all tu metadata moi nhat nen tren database trong da co san cot nay.
    if _co_cot(op.get_bind()):
        return
    op.add_column(TABLE, sa.Column(COLUMN, sa.JSON(), nullable=False, server_default="{}"))


def downgrade() -> None:
    if _co_cot(op.get_bind()):
        op.drop_column(TABLE, COLUMN)
