import os
import json
import logging

logger = logging.getLogger(__name__)


class GeminiService:
    """Google Gemini AI service for product reviews and chatbot."""

    def __init__(self):
        from dotenv import load_dotenv
        load_dotenv()
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.model = None

    def _get_client(self):
        if self.model:
            return self.model
        if not self.api_key:
            return None
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            self.model = client
            return self.model
        except Exception as e:
            logger.warning("Gemini client init failed: %s", e)
            return None

    def generate_review(self, product_data, comparison_data):
        """Generate AI review using Gemini. Falls back to local rules if no API key."""
        client = self._get_client()
        if not client:
            return None

        listings = comparison_data.get("listings", [])
        platforms = [l.get("platform", "") for l in listings]
        prices = [l.get("price", 0) for l in listings if l.get("price", 0) > 0]
        min_price = min(prices) if prices else 0
        max_price = max(prices) if prices else 0
        best = listings[0] if listings else {}

        prompt = f"""You are ShopSmart AI, an expert product advisor for Indian e-commerce.

Product: {product_data.get('title', 'Unknown')}
Brand: {product_data.get('brand', 'Unknown')}
Category: {product_data.get('category', 'Unknown')}
Current Price: Rs.{product_data.get('price', 0):,.0f}
MRP: Rs.{product_data.get('mrp', 0):,.0f}
Platform: {product_data.get('platform', 'Unknown')}

Price comparison across platforms:
{json.dumps([{{'platform': l.get('platform'), 'price': l.get('price'), 'rating': l.get('rating')}} for l in listings[:6]], indent=2)}

Price range: Rs.{min_price:,.0f} - Rs.{max_price:,.0f}
Best price: Rs.{best.get('price', 0):,.0f} on {best.get('platform', 'N/A')}

Generate a review in this EXACT JSON format (no markdown, just raw JSON):
{{
  "summary": "2-3 sentence product summary",
  "pros": ["pro 1", "pro 2", "pro 3"],
  "cons": ["con 1", "con 2"],
  "verdict": "One line deal assessment",
  "best_platform": {{"name": "platform name", "price": price_number, "savings": savings_vs_mrp}},
  "savings_tip": "One actionable savings tip",
  "recommendation": "Buy/Wait/Hold recommendation with reason"
}}"""

        try:
            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                input=prompt,
            )
            text = interaction.output_text.strip()
            # Clean up markdown code blocks if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
            if text.endswith("```"):
                text = text.rsplit("```", 1)[0]
            text = text.strip()
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Gemini returned invalid JSON, using fallback")
            return None
        except Exception as e:
            logger.warning("Gemini review failed: %s", e)
            return None

    def chat(self, message, context=None):
        """Chatbot endpoint using Gemini."""
        client = self._get_client()
        if not client:
            return "Gemini API key not configured. Please add GEMINI_API_KEY to backend/.env file."

        system_prompt = """You are ShopSmart AI, an intelligent shopping assistant for Indian e-commerce platforms.

You help users:
- Compare prices across Amazon, Flipkart, Myntra, AJIO, Meesho, Croma, Reliance Digital, Tata CLiQ
- Find the best deals and coupons
- Get product recommendations
- Understand product specifications
- Make informed purchase decisions

Rules:
- Always mention prices in INR (Rs.)
- Be concise and helpful
- If asked about a specific product, suggest comparing on ShopSmart
- You know about products available in the ShopSmart database
- Keep responses under 200 words unless asked for detail"""

        ctx_text = ""
        if context:
            ctx_text = f"\n\nContext: The user is viewing: {json.dumps(context, default=str)[:500]}"

        try:
            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                input=f"{system_prompt}{ctx_text}\n\nUser: {message}",
            )
            return interaction.output_text.strip()
        except Exception as e:
            logger.warning("Gemini chat failed: %s", e)
            return f"Sorry, AI is temporarily unavailable. Error: {str(e)[:100]}"
