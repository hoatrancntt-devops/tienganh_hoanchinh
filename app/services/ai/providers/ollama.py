import time

import httpx

from app.services.ai.base import (
    LLMError,
    LLMRequest,
    LLMResponse,
    ProviderConfig,
    estimate_tokens,
)

DEFAULT_BASE = "http://localhost:11434"


class OllamaProvider:
    """Chạy local, không tốn tiền. Mặc định TẮT: kiến trúc 8GB đã dành RAM cho whisper."""

    name = "ollama"

    def __init__(self, cfg: ProviderConfig):
        self.cfg = cfg
        self.base = (cfg.base_url or DEFAULT_BASE).rstrip("/")

    async def complete(self, req: LLMRequest, model: str) -> LLMResponse:
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": req.system}, *req.messages],
            "stream": False,
            "options": {"temperature": req.temperature, "num_predict": req.max_tokens},
        }
        started = time.monotonic()
        try:
            async with httpx.AsyncClient(timeout=120) as client:
                resp = await client.post(f"{self.base}/api/chat", json=payload)
        except httpx.RequestError as exc:
            raise LLMError(f"không kết nối được Ollama: {exc}", "connection") from exc
        if resp.status_code >= 400:
            raise LLMError(f"{resp.status_code}: {resp.text[:180]}", "http_error")
        data = resp.json()
        text = data.get("message", {}).get("content", "")
        return LLMResponse(
            text=text, provider=self.name, model=model,
            input_tokens=data.get("prompt_eval_count") or estimate_tokens(req.system),
            output_tokens=data.get("eval_count") or estimate_tokens(text),
            usage_estimated="eval_count" not in data,
            latency_ms=int((time.monotonic() - started) * 1000),
        )

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                return (await client.get(f"{self.base}/api/tags")).status_code == 200
        except httpx.RequestError:
            return False
