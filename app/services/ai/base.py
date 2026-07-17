"""Hợp đồng provider. Router không biết provider nào tồn tại."""
from dataclasses import dataclass, field
from typing import Protocol


@dataclass
class LLMRequest:
    system: str
    messages: list[dict]           # [{"role": "user"|"assistant", "content": str}]
    max_tokens: int = 350
    temperature: float = 0.3
    json_schema: dict | None = None


@dataclass
class LLMResponse:
    text: str
    provider: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    usage_estimated: bool = False   # provider không trả usage -> adapter tự ước lượng
    latency_ms: int = 0
    parsed: dict | None = None
    from_cache: bool = False


@dataclass
class ProviderConfig:
    api_key: str = ""
    base_url: str = ""
    extra: dict = field(default_factory=dict)


class LLMError(Exception):
    def __init__(self, msg: str, code: str = "provider_error", retryable: bool = True):
        super().__init__(msg)
        self.code = code
        self.retryable = retryable


class LLMProvider(Protocol):
    name: str

    async def complete(self, req: LLMRequest, model: str) -> LLMResponse: ...
    async def health(self) -> bool: ...


def estimate_tokens(text: str) -> int:
    """Ước lượng thô khi provider không trả usage. Mất số liệu token = mất kiểm soát chi phí."""
    return max(1, len(text) // 4)
