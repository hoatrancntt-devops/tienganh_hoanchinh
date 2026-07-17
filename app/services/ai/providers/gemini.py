import time

import httpx

from app.services.ai.base import LLMError, LLMRequest, LLMResponse, ProviderConfig

API = "https://generativelanguage.googleapis.com/v1beta/models"


class GeminiProvider:
    name = "gemini"

    def __init__(self, cfg: ProviderConfig):
        self.cfg = cfg
        self.base = cfg.base_url or API

    async def complete(self, req: LLMRequest, model: str) -> LLMResponse:
        if not self.cfg.api_key:
            raise LLMError("thiếu API key", "no_key", retryable=False)
        contents = [
            {"role": "model" if m["role"] == "assistant" else "user",
             "parts": [{"text": m["content"]}]}
            for m in req.messages
        ]
        payload = {
            "contents": contents,
            "systemInstruction": {"parts": [{"text": req.system}]},
            "generationConfig": {
                "maxOutputTokens": req.max_tokens,
                "temperature": req.temperature,
            },
        }
        started = time.monotonic()
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                f"{self.base}/{model}:generateContent",
                params={"key": self.cfg.api_key},
                json=payload,
            )
        if resp.status_code in (401, 403):
            raise LLMError("API key không hợp lệ", "auth", retryable=False)
        if resp.status_code == 429:
            raise LLMError("rate limited", "rate_limit")
        if resp.status_code >= 400:
            raise LLMError(f"{resp.status_code}: {resp.text[:180]}", "http_error")
        data = resp.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise LLMError("phản hồi rỗng", "empty_response") from None
        usage = data.get("usageMetadata", {})
        return LLMResponse(
            text=text, provider=self.name, model=model,
            input_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            latency_ms=int((time.monotonic() - started) * 1000),
        )

    async def health(self) -> bool:
        return bool(self.cfg.api_key)
