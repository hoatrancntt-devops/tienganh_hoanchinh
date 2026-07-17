import time

import httpx

from app.services.ai.base import LLMError, LLMRequest, LLMResponse, ProviderConfig

API = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider:
    name = "openai"

    def __init__(self, cfg: ProviderConfig):
        self.cfg = cfg
        self.base = cfg.base_url or API

    def _messages(self, req: LLMRequest) -> list[dict]:
        return [{"role": "system", "content": req.system}, *req.messages]

    async def complete(self, req: LLMRequest, model: str) -> LLMResponse:
        if not self.cfg.api_key:
            raise LLMError("thiếu API key", "no_key", retryable=False)
        payload = {
            "model": model,
            "messages": self._messages(req),
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
        }
        if req.json_schema:
            payload["response_format"] = {"type": "json_object"}
        started = time.monotonic()
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                self.base,
                headers={"Authorization": f"Bearer {self.cfg.api_key}"},
                json=payload,
            )
        if resp.status_code == 401:
            raise LLMError("API key không hợp lệ", "auth", retryable=False)
        if resp.status_code == 429:
            raise LLMError("rate limited", "rate_limit")
        if resp.status_code >= 400:
            raise LLMError(f"{resp.status_code}: {resp.text[:180]}", "http_error")
        data = resp.json()
        usage = data.get("usage", {})
        return LLMResponse(
            text=data["choices"][0]["message"]["content"],
            provider=self.name, model=data.get("model", model),
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            latency_ms=int((time.monotonic() - started) * 1000),
        )

    async def health(self) -> bool:
        return bool(self.cfg.api_key)
