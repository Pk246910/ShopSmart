import os
import logging

from .base import AIProvider

logger = logging.getLogger(__name__)


class GeminiProvider(AIProvider):
    name = "gemini"
    model = "gemini-3.6-flash"

    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("GEMINI_API_KEY", "")

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        if not self.api_key:
            self._available = False
            return False
        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            self._available = True
        except Exception as e:
            logger.warning("Gemini init failed: %s", str(e)[:100])
            self._available = False
        return self._available

    def _call_api(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> str:
        interaction = self._client.interactions.create(
            model=self.model,
            input=f"{system_prompt}\n\n{user_prompt}",
        )
        text = interaction.output_text
        if not text:
            raise ValueError("Gemini returned empty response")
        return text.strip()
