import time

import httpx

from app.services.ai.base import LLMError, LLMRequest, LLMResponse, ProviderConfig

API = "https://api.anthropic.com/v1/messages"


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, cfg: ProviderConfig):
        self.cfg = cfg
        self.base = cfg.base_url or API

    async def complete(self, req: LLMRequest, model: str) -> LLMResponse:
        if not self.cfg.api_key:
            raise LLMError("thiếu API key", "no_key", retryable=False)
        payload = {
            "model": model,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
            "system": req.system,
            "messages": req.messages,
        }
        started = time.monotonic()
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                self.base,
                headers={
                    "x-api-key": self.cfg.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json=payload,
            )
        if resp.status_code == 401:
            raise LLMError("API key không hợp lệ", "auth", retryable=False)
        if resp.status_code == 429:
            raise LLMError("rate limited", "rate_limit")
        if resp.status_code >= 400:
            raise LLMError(f"{resp.status_code}: {resp.text[:180]}", "http_error")
        data = resp.json()
        text = "".join(b.get("text", "") for b in data.get("content", []))
        usage = data.get("usage", {})
        return LLMResponse(
            text=text, provider=self.name, model=data.get("model", model),
            input_tokens=usage.get("input_tokens", 0),
            output_tokens=usage.get("output_tokens", 0),
            latency_ms=int((time.monotonic() - started) * 1000),
        )

    async def health(self) -> bool:
        return bool(self.cfg.api_key)
