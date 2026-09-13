import os
import logging

from .base import AIProvider

logger = logging.getLogger(__name__)


class ClaudeProvider(AIProvider):
    name = "claude"
    model = "claude-3-5-haiku-20241022"

    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        if not self.api_key:
            self._available = False
            return False
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
            self._available = True
        except ImportError:
            logger.info("anthropic package not installed. Run: pip install anthropic")
            self._available = False
        except Exception as e:
            logger.warning("Claude init failed: %s", str(e)[:100])
            self._available = False
        return self._available

    def _call_api(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> str:
        response = self._client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return response.content[0].text.strip()
