import os
import logging

from .base import AIProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(AIProvider):
    name = "openai"
    model = "gpt-4o-mini"

    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get("OPENAI_API_KEY", "")

    def is_available(self) -> bool:
        if self._available is not None:
            return self._available
        if not self.api_key:
            self._available = False
            return False
        try:
            import openai
            self._client = openai.OpenAI(api_key=self.api_key)
            self._available = True
        except ImportError:
            logger.info("openai package not installed. Run: pip install openai")
            self._available = False
        except Exception as e:
            logger.warning("OpenAI init failed: %s", str(e)[:100])
            self._available = False
        return self._available

    def _call_api(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
