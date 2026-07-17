"""schema khởi tạo

Sinh từ metadata thay vì viết tay: create_all trên connection của Alembic cho kết quả
giống hệt models và không thể lệch. Migration sau này dùng --autogenerate bình thường.

Revision ID: 0001
Revises:
Create Date: 2026-07-17
"""
from alembic import op

import app.models  # noqa: F401
from app.db.base import Base

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    Base.metadata.create_all(bind=op.get_bind())


def downgrade() -> None:
    Base.metadata.drop_all(bind=op.get_bind())
