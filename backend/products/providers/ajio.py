import logging
from typing import Dict, List, Optional
from decimal import Decimal
from .base import BaseProvider, ProductData

logger = logging.getLogger(__name__)


class AJIOProvider(BaseProvider):
    """AJIO provider — uses ProductExtractor for extraction."""

    def __init__(self):
        super().__init__()
        self.platform_name = "AJIO"
        self.base_url = "https://www.ajio.com"

    def search_products(self, query: str, category: str = None) -> List[ProductData]:
        return []

    def get_product_details(self, product_url: str) -> Optional[ProductData]:
        try:
            from products.services.product_extractor import ProductExtractor
            extractor = ProductExtractor()
            raw = extractor.extract(product_url, "AJIO")
            price = Decimal(str(raw.get("price", 0)))
            return ProductData(
                name=raw.get("title", ""),
                brand=raw.get("brand", ""),
                category=raw.get("category", "Fashion"),
                price=price,
                original_price=Decimal(str(raw.get("mrp", 0))) if raw.get("mrp", 0) > 0 else None,
                rating=raw.get("rating"),
                reviews_count=raw.get("review_count", 0),
                product_url=product_url,
                image_url=raw.get("image_url", ""),
            )
        except Exception as e:
            logger.warning("AJIO extraction failed for %s: %s", product_url, e)
            return None

    def get_price_history(self, product_url: str) -> List[Dict]:
        return []

    def is_available(self) -> bool:
        return True
