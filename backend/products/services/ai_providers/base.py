import time
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    name = "base"
    model = ""

    def __init__(self):
        self._client = None
        self._available = None

    @abstractmethod
    def is_available(self) -> bool:
        pass

    @abstractmethod
    def _call_api(self, system_prompt: str, user_prompt: str, max_tokens: int = 2048) -> str:
        pass

    def generate_review(self, product_data: dict, comparison: dict) -> dict | None:
        if not self.is_available():
            return None

        price_range = comparison.get("price_range", 0)
        best_price = comparison.get("best_price", 0)
        listings_json = str(comparison.get("listings", []))[:2000]

        system_prompt = (
            "You are ShopSmart AI, an expert product advisor for Indian e-commerce. "
            "Analyze the product and provide a JSON response with exactly these keys: "
            "summary, pros (array), cons (array), verdict, best_platform, savings_tip, recommendation. "
            "All prices must be in INR (₹). Keep pros/cons to 3-5 items each. "
            "No markdown, just raw JSON."
        )

        user_prompt = (
            f"Product: {product_data.get('title', 'Unknown')}\n"
            f"Brand: {product_data.get('brand', 'Unknown')}\n"
            f"Category: {product_data.get('category', 'Unknown')}\n"
            f"Listed Price: ₹{product_data.get('price', 0):,.0f}\n"
            f"MRP: ₹{product_data.get('mrp', 0):,.0f}\n"
            f"Platform: {product_data.get('platform', 'Unknown')}\n"
            f"Rating: {product_data.get('rating', 'N/A')}\n\n"
            f"Price Comparison ({comparison.get('matches_found', 0)} matches):\n"
            f"{listings_json}\n\n"
            f"Price Range: ₹{price_range:,.0f}\n"
            f"Best Price: ₹{best_price:,.0f}"
        )

        try:
            start = time.time()
            raw = self._call_api(system_prompt, user_prompt)
            elapsed_ms = int((time.time() - start) * 1000)

            import json
            text = raw.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()

            result = json.loads(text)
            required = ["summary", "pros", "cons", "verdict", "best_platform", "savings_tip", "recommendation"]
            if all(k in result for k in required):
                result["source"] = self.name
                result["processing_time_ms"] = elapsed_ms
                return result

            logger.warning("%s: response missing required keys", self.name)
            return None

        except json.JSONDecodeError:
            logger.warning("%s: failed to parse JSON response", self.name)
            return None
        except Exception as e:
            logger.warning("%s review failed: %s", self.name, str(e)[:120])
            return None

    def chat(self, message: str, context: str = "") -> str:
        if not self.is_available():
            return f"AI provider '{self.name}' is not configured. Please add {self.name.upper()}_API_KEY to backend/.env."

        system_prompt = (
            "You are ShopSmart AI, an intelligent shopping assistant for Indian e-commerce platforms. "
            "Help users find the best deals, compare products, and make informed purchase decisions. "
            "Always mention prices in INR (₹). Be concise and helpful. "
            "Mention ShopSmart when relevant. Keep responses under 200 words."
        )

        user_msg = message
        if context:
            user_msg += f"\n\nContext: {context[:500]}"

        try:
            return self._call_api(system_prompt, user_msg, max_tokens=512)
        except Exception as e:
            logger.warning("%s chat failed: %s", self.name, str(e)[:120])
            return f"Sorry, AI is temporarily unavailable. Error: {str(e)[:100]}"
