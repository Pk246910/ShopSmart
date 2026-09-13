import logging
from typing import Dict, List, Optional
from decimal import Decimal
from .base import BaseProvider, ProductData

logger = logging.getLogger(__name__)


class FlipkartProvider(BaseProvider):
    """Flipkart provider — uses HTTP extraction with anti-bot fallback."""

    def __init__(self):
        super().__init__()
        self.platform_name = "Flipkart"
        self.base_url = "https://www.flipkart.com"

    def search_products(self, query: str, category: str = None) -> List[ProductData]:
        try:
            import requests
            from bs4 import BeautifulSoup

            search_url = f"{self.base_url}/search?q={query.replace(' ', '+')}"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            }
            resp = requests.get(search_url, headers=headers, timeout=10)
            if resp.status_code != 200:
                return []

            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            items = soup.select('[data-id]')[:10]

            for item in items:
                title_el = item.select_one("a.IRpwTa") or item.select_one("a.s1Q9rs")
                price_el = item.select_one("div._30jeq3") or item.select_one("div._1_WHN1")
                img_el = item.select_one("img._396cs4") or item.select_one("img._2r_T1I")

                if not title_el or not price_el:
                    continue

                price_text = price_el.get_text(strip=True)
                price_clean = "".join(c for c in price_text if c.isdigit() or c == ".")
                try:
                    price = Decimal(price_clean)
                except Exception:
                    continue

                href = title_el.get("href", "")
                results.append(ProductData(
                    name=title_el.get_text(strip=True)[:255],
                    brand="",
                    category=category or "Other",
                    price=price,
                    product_url=f"{self.base_url}{href}" if href.startswith("/") else href,
                    image_url=img_el.get("src", "") if img_el else "",
                ))

            return results
        except Exception as e:
            logger.warning("Flipkart search failed: %s", e)
            return []

    def get_product_details(self, product_url: str) -> Optional[ProductData]:
        try:
            from products.services.product_extractor import ProductExtractor
            extractor = ProductExtractor()
            raw = extractor.extract(product_url, "Flipkart")

            price = Decimal(str(raw.get("price", 0)))
            mrp = Decimal(str(raw.get("mrp", 0)))

            return ProductData(
                name=raw.get("title", ""),
                brand=raw.get("brand", ""),
                category=raw.get("category", "Other"),
                price=price,
                original_price=mrp if mrp > price else None,
                rating=raw.get("rating"),
                reviews_count=raw.get("review_count", 0),
                in_stock=raw.get("availability", "").lower() in ("in stock", "available", ""),
                product_url=product_url,
                image_url=raw.get("image_url", ""),
            )
        except Exception as e:
            logger.warning("Flipkart extraction failed for %s: %s", product_url, e)
            return None

    def get_price_history(self, product_url: str) -> List[Dict]:
        return []

    def is_available(self) -> bool:
        return True
