"""Gửi mail: Microsoft 365 OAuth 2.0 (client credentials) hoặc SMTP. Cấu hình trên web.

M365 setup phía Azure: App registration -> Application permission `Mail.Send` -> Grant admin
consent. Sender phải là mailbox thật trong tenant.
"""
import logging
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import settings_service as cfg

log = logging.getLogger(__name__)

GRAPH_TOKEN_URL = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"
GRAPH_SEND_URL = "https://graph.microsoft.com/v1.0/users/{sender}/sendMail"

_token_cache: dict[str, tuple[str, float]] = {}  # tenant -> (token, expires_at monotonic)


class MailError(Exception):
    pass


async def _m365_token(tenant: str, client_id: str, client_secret: str) -> str:
    cached = _token_cache.get(tenant)
    if cached and cached[1] > time.monotonic() + 60:
        return cached[0]
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(
            GRAPH_TOKEN_URL.format(tenant=tenant),
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": "https://graph.microsoft.com/.default",
                "grant_type": "client_credentials",
            },
        )
    if resp.status_code != 200:
        raise MailError(f"M365 token thất bại ({resp.status_code}): {resp.text[:200]}")
    data = resp.json()
    token = data["access_token"]
    _token_cache[tenant] = (token, time.monotonic() + int(data.get("expires_in", 3600)))
    return token


async def _send_m365(db: AsyncSession, to_email: str, subject: str, body_html: str) -> None:
    tenant = await cfg.get(db, "mail.m365.tenant_id")
    client_id = await cfg.get(db, "mail.m365.client_id")
    client_secret = await cfg.get(db, "mail.m365.client_secret")
    sender = await cfg.get(db, "mail.sender")
    if not all([tenant, client_id, client_secret, sender]):
        raise MailError("Cấu hình Microsoft 365 chưa đầy đủ.")

    token = await _m365_token(tenant, client_id, client_secret)
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body_html},
            "toRecipients": [{"emailAddress": {"address": to_email}}],
        },
        "saveToSentItems": False,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            GRAPH_SEND_URL.format(sender=sender),
            headers={"Authorization": f"Bearer {token}"},
            json=payload,
        )
    if resp.status_code == 401:
        _token_cache.pop(tenant, None)  # token hỏng -> buộc lấy lại lần sau
    if resp.status_code not in (202, 200):
        raise MailError(f"Graph sendMail lỗi ({resp.status_code}): {resp.text[:200]}")


async def _send_smtp(db: AsyncSession, to_email: str, subject: str, body_html: str) -> None:
    host = await cfg.get(db, "mail.smtp.host")
    port = await cfg.get_int(db, "mail.smtp.port", 587)
    username = await cfg.get(db, "mail.smtp.username")
    password = await cfg.get(db, "mail.smtp.password")
    use_tls = await cfg.get_bool(db, "mail.smtp.use_tls", True)
    sender = await cfg.get(db, "mail.sender") or username
    if not host or not sender:
        raise MailError("Cấu hình SMTP chưa đầy đủ.")

    msg = MIMEMultipart("alternative")
    msg["Subject"], msg["From"], msg["To"] = subject, sender, to_email
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    # smtplib đồng bộ; chấp nhận vì chỉ chạy trong job outbox, không nằm trên đường request.
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        if use_tls:
            smtp.starttls()
        if username and password:
            smtp.login(username, password)
        smtp.send_message(msg)


async def send(db: AsyncSession, to_email: str, subject: str, body_html: str) -> None:
    provider = await cfg.get(db, "mail.provider", "none")
    if provider == "none":
        raise MailError("Chưa cấu hình gửi mail.")
    if provider == "m365":
        await _send_m365(db, to_email, subject, body_html)
    elif provider == "smtp":
        await _send_smtp(db, to_email, subject, body_html)
    else:
        raise MailError(f"Provider mail không hỗ trợ: {provider}")


async def is_configured(db: AsyncSession) -> bool:
    provider = await cfg.get(db, "mail.provider", "none")
    if provider == "m365":
        return all([
            await cfg.get(db, "mail.m365.tenant_id"),
            await cfg.get(db, "mail.m365.client_id"),
            await cfg.get(db, "mail.m365.client_secret"),
            await cfg.get(db, "mail.sender"),
        ])
    if provider == "smtp":
        return bool(await cfg.get(db, "mail.smtp.host") and await cfg.get(db, "mail.sender"))
    return False


async def send_test(db: AsyncSession, to_email: str) -> None:
    await send(
        db, to_email, "[English for Work] Kiểm tra cấu hình email",
        "<p>Nếu bạn đọc được thư này, cấu hình gửi mail đã hoạt động.</p>",
    )
