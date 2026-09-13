import time
import logging

from .base import AIProvider
from .gemini_provider import GeminiProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider

logger = logging.getLogger(__name__)

DEFAULT_CHAIN = ["gemini", "openai", "claude"]


class AIProviderManager:
    def __init__(self, chain: list[str] | None = None):
        self._providers: dict[str, AIProvider] = {
            "gemini": GeminiProvider(),
            "openai": OpenAIProvider(),
            "claude": ClaudeProvider(),
        }
        self._chain = chain or DEFAULT_CHAIN

    def _get_available(self) -> list[AIProvider]:
        return [self._providers[name] for name in self._chain if name in self._providers and self._providers[name].is_available()]

    def _log_interaction(self, provider_name: str, endpoint: str, status: str,
                         response_time_ms: int = 0, error_message: str = ""):
        try:
            from products.models import AIProviderLog
            AIProviderLog.objects.create(
                provider=provider_name,
                endpoint=endpoint,
                status=status,
                response_time_ms=response_time_ms,
                error_message=error_message,
            )
        except Exception as e:
            logger.debug("Failed to log AI provider interaction: %s", str(e)[:80])

    def generate_review(self, product_data: dict, comparison: dict) -> dict | None:
        available = self._get_available()
        if not available:
            logger.info("No AI providers available, using rule-based fallback")
            return None

        for provider in available:
            try:
                start = time.time()
                result = provider.generate_review(product_data, comparison)
                elapsed_ms = int((time.time() - start) * 1000)

                if result:
                    self._log_interaction(provider.name, "generate_review", "success", elapsed_ms)
                    return result

                self._log_interaction(provider.name, "generate_review", "error", elapsed_ms, "Invalid response")

            except Exception as e:
                elapsed_ms = int((time.time() - start) * 1000)
                self._log_interaction(provider.name, "generate_review", "error", elapsed_ms, str(e)[:200])
                logger.warning("%s failed: %s", provider.name, str(e)[:100])

        return None

    def chat(self, message: str, context: str = "") -> str:
        available = self._get_available()
        if not available:
            return "No AI providers configured. Add GEMINI_API_KEY, OPENAI_API_KEY, or ANTHROPIC_API_KEY to backend/.env."

        for provider in available:
            try:
                start = time.time()
                result = provider.chat(message, context)
                elapsed_ms = int((time.time() - start) * 1000)

                if result and not result.startswith("Sorry, AI is temporarily unavailable"):
                    self._log_interaction(provider.name, "chat", "success", elapsed_ms)
                    return result

                self._log_interaction(provider.name, "chat", "error", elapsed_ms, result[:200])

            except Exception as e:
                elapsed_ms = int((time.time() - start) * 1000)
                self._log_interaction(provider.name, "chat", "error", elapsed_ms, str(e)[:200])
                logger.warning("%s chat failed: %s", provider.name, str(e)[:100])

        return "Sorry, all AI providers are temporarily unavailable. Please try again later."

    def status(self) -> dict:
        return {
            name: {
                "available": provider.is_available(),
                "model": provider.model,
            }
            for name, provider in self._providers.items()
        }


_manager = None


def get_ai_manager() -> AIProviderManager:
    global _manager
    if _manager is None:
        _manager = AIProviderManager()
    return _manager
