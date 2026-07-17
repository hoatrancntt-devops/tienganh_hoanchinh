# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder

WORKDIR /build
RUN pip install --no-cache-dir --upgrade pip
# Cài vào prefix riêng để stage sau chỉ copy artefact, không kéo theo toolchain.
RUN pip install --no-cache-dir --prefix=/install \
    "fastapi==0.115.6" "uvicorn[standard]==0.34.0" "sqlalchemy[asyncio]==2.0.36" \
    "alembic==1.14.0" "asyncpg==0.30.0" "aiosqlite==0.20.0" "pydantic==2.10.4" \
    "pydantic-settings==2.7.0" "argon2-cffi==23.1.0" "cryptography==44.0.0" \
    "itsdangerous==2.2.0" "httpx==0.28.1" "jinja2==3.1.5" "python-multipart==0.0.20" \
    "apscheduler==3.11.0" "email-validator==2.2.0" "greenlet==3.1.1" "pyyaml==6.0.2"


FROM python:3.11-slim

# ffmpeg: chuẩn hoá audio từ trình duyệt về WAV 16k mono. curl: healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

RUN useradd --create-home --uid 1000 app
WORKDIR /app

COPY --chown=app:app app ./app
COPY --chown=app:app scripts ./scripts
COPY --chown=app:app migrations ./migrations
COPY --chown=app:app seeds ./seeds
COPY --chown=app:app config ./config
COPY --chown=app:app alembic.ini pyproject.toml ./

RUN mkdir -p /app/media /app/data && chown -R app:app /app/media /app/data

USER app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PATH="/usr/local/bin:$PATH"
EXPOSE 9999

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
    CMD curl -fsS http://localhost:9999/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9999", "--workers", "1"]
