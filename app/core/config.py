"""Config từ env. Không có secret nào hardcode ở đây."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "English for Work"
    APP_ENV: str = "dev"  # dev | prod
    APP_PORT: int = 9999
    DEBUG: bool = False

    # Bắt buộc. Dùng cho ký session cookie VÀ dẫn xuất khoá mã hoá secret trong DB.
    SECRET_KEY: str = Field(min_length=32)

    # dev: sqlite+aiosqlite:///./data/dev.db | prod: postgresql+asyncpg://...
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/dev.db"
    DB_ECHO: bool = False

    SESSION_COOKIE: str = "efw_session"
    SESSION_TTL_HOURS: int = 24 * 14

    MEDIA_DIR: str = "./media"
    SPEECH_SERVICE_URL: str = "http://speech:8080"
    SPEECH_ENABLED: bool = True

    # Admin bootstrap. Seed đọc từ đây, không lưu vào code.
    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None

    DEFAULT_TZ: str = "Asia/Ho_Chi_Minh"

    # AI: route mặc định khi DB chưa cấu hình. Format "provider:model,provider:model"
    LLM_ROUTE_T1: str = ""
    LLM_ROUTE_T2: str = ""
    LLM_PRICES_PATH: str = "./config/llm_prices.json"
    AI_USER_DAILY_CALLS: int = 20
    AI_USER_DAILY_TOKENS: int = 30_000
    AI_GLOBAL_MONTHLY_USD: float = 20.0

    SCHEDULER_ENABLED: bool = True

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    return Settings()
