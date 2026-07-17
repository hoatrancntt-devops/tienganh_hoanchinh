"""Mã hoá secret do admin nhập trên web (API key, client secret) trước khi vào DB.

Khoá dẫn xuất từ SECRET_KEY -> đổi SECRET_KEY sẽ làm mọi secret trong DB không giải mã được.
"""
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import get_settings

_PREFIX = "enc:v1:"


def _fernet() -> Fernet:
    digest = hashlib.sha256(get_settings().SECRET_KEY.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt(plain: str) -> str:
    return _PREFIX + _fernet().encrypt(plain.encode()).decode()


def decrypt(value: str) -> str:
    if not value.startswith(_PREFIX):
        return value  # giá trị cũ chưa mã hoá
    try:
        return _fernet().decrypt(value[len(_PREFIX):].encode()).decode()
    except InvalidToken:
        return ""  # SECRET_KEY đã đổi; coi như chưa cấu hình


def mask(plain: str) -> str:
    """Hiển thị lên UI mà không lộ giá trị."""
    if not plain:
        return ""
    return plain[:3] + "•" * 8 + plain[-3:] if len(plain) > 8 else "•" * len(plain)
