from pydantic import BaseModel, EmailStr, Field


class MailSettingsIn(BaseModel):
    """Admin cấu hình trên web. Secret để trống = giữ giá trị cũ."""

    provider: str = Field(pattern="^(m365|smtp|none)$")
    sender: EmailStr | None = None
    # Microsoft 365 OAuth 2.0 (client credentials)
    m365_tenant_id: str = ""
    m365_client_id: str = ""
    m365_client_secret: str = ""  # trống = không đổi
    # SMTP
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""      # trống = không đổi
    smtp_use_tls: bool = True


class MailSettingsOut(BaseModel):
    provider: str
    sender: str
    m365_tenant_id: str
    m365_client_id: str
    m365_client_secret_masked: str
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password_masked: str
    smtp_use_tls: bool
    configured: bool


class ProviderKeyIn(BaseModel):
    provider: str = Field(pattern="^(anthropic|openai|gemini|openrouter|ollama|azure_openai)$")
    api_key: str = ""        # trống = không đổi
    base_url: str = ""
    enabled: bool = True


class AISettingsIn(BaseModel):
    ai_enabled: bool = True
    route_t1: str = ""       # "anthropic:claude-haiku-4-5,gemini:gemini-2.0-flash"
    route_t2: str = ""
    user_daily_calls: int = Field(default=20, ge=0, le=1000)
    global_monthly_usd: float = Field(default=20.0, ge=0)
    providers: list[ProviderKeyIn] = []


class ProviderKeyOut(BaseModel):
    provider: str
    api_key_masked: str
    base_url: str
    enabled: bool
    has_key: bool


class AISettingsOut(BaseModel):
    ai_enabled: bool
    route_t1: str
    route_t2: str
    user_daily_calls: int
    global_monthly_usd: float
    spent_this_month_usd: float
    providers: list[ProviderKeyOut]


class TestMailIn(BaseModel):
    to_email: EmailStr
