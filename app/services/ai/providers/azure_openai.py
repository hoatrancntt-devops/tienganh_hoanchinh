import time

import httpx

from app.services.ai.base import LLMError, LLMRequest, LLMResponse, ProviderConfig

API_VERSION = "2024-10-21"


class AzureOpenAIProvider:
    """Cùng payload với OpenAI nhưng khác cách dựng endpoint: model = tên deployment.

    base_url: https://<resource>.openai.azure.com
    """

    name = "azure_openai"

    def __init__(self, cfg: ProviderConfig):
        self.cfg = cfg
        self.base = (cfg.base_url or "").rstrip("/")
        self.api_version = cfg.extra.get("api_version", API_VERSION)

    async def complete(self, req: LLMRequest, model: str) -> LLMResponse:
        if not self.cfg.api_key or not self.base:
            raise LLMError("thiếu API key hoặc endpoint", "no_key", retryable=False)
        url = f"{self.base}/openai/deployments/{model}/chat/completions"
        payload = {
            "messages": [{"role": "system", "content": req.system}, *req.messages],
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
        }
        started = time.monotonic()
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                url, params={"api-version": self.api_version},
                headers={"api-key": self.cfg.api_key}, json=payload,
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
            provider=self.name, model=model,
            input_tokens=usage.get("prompt_tokens", 0),
            output_tokens=usage.get("completion_tokens", 0),
            latency_ms=int((time.monotonic() - started) * 1000),
        )

    async def health(self) -> bool:
        return bool(self.cfg.api_key and self.base)
