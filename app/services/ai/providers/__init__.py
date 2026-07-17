from app.services.ai.providers.anthropic import AnthropicProvider
from app.services.ai.providers.azure_openai import AzureOpenAIProvider
from app.services.ai.providers.gemini import GeminiProvider
from app.services.ai.providers.ollama import OllamaProvider
from app.services.ai.providers.openai import OpenAIProvider
from app.services.ai.providers.openrouter import OpenRouterProvider

REGISTRY = {
    "anthropic": AnthropicProvider,
    "openai": OpenAIProvider,
    "gemini": GeminiProvider,
    "openrouter": OpenRouterProvider,
    "ollama": OllamaProvider,
    "azure_openai": AzureOpenAIProvider,
}

__all__ = ["REGISTRY"]
