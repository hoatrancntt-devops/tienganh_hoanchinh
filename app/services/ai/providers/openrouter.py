import time

import httpx

from app.services.ai.base import (
    LLMError,
    LLMRequest,
    LLMResponse,
    ProviderConfig,
    estimate_tokens,
)

API = "https://openrouter.ai/api/v1/chat/completions"


class OpenRouterProvider:
    name = "openrouter"

    def __init__(self, cfg: ProviderConfig):
        self.cfg = cfg
        self.base = cfg.base_url or API

    async def complete(self, req: LLMRequest, model: str) -> LLMResponse:
        if not self.cfg.api_key:
            raise LLMError("thiếu API key", "no_key", retryable=False)
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": req.system}, *req.messages],
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
        }
        started = time.monotonic()
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                self.base,
                headers={
                    "Authorization": f"Bearer {self.cfg.api_key}",
                    "X-Title": "English for Work",
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
        text = data["choices"][0]["message"]["content"]
        usage = data.get("usage") or {}
        # Một số route của OpenRouter không trả usage -> ước lượng, đánh dấu rõ.
        estimated = not usage
        return LLMResponse(
            text=text, provider=self.name, model=data.get("model", model),
            input_tokens=usage.get("prompt_tokens")
            or estimate_tokens(req.system + str(req.messages)),
            output_tokens=usage.get("completion_tokens") or estimate_tokens(text),
            usage_estimated=estimated,
            latency_ms=int((time.monotonic() - started) * 1000),
        )

    async def health(self) -> bool:
        return bool(self.cfg.api_key)
