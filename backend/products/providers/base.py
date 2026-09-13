from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ProductData:
    """Standardized product data structure for all providers."""
    name: str
    brand: str
    category: str
    price: Decimal
    original_price: Optional[Decimal] = None
    rating: Optional[float] = None
    reviews_count: int = 0
    in_stock: bool = True
    delivery_days: int = 3
    product_url: str = ""
    image_url: str = ""


class BaseProvider(ABC):
    """Abstract base class for all platform providers."""

    def __init__(self):
        self.platform_name = ""
        self.base_url = ""

    @abstractmethod
    def search_products(self, query: str, category: str = None) -> List[ProductData]:
        """
        Search for products on the platform.
        
        Args:
            query: Search query string
            category: Optional category filter
            
        Returns:
            List of ProductData objects
        """
        pass

    @abstractmethod
    def get_product_details(self, product_url: str) -> Optional[ProductData]:
        """
        Get detailed product information from a URL.
        
        Args:
            product_url: URL of the product
            
        Returns:
            ProductData object or None if not found
        """
        pass

    @abstractmethod
    def get_price_history(self, product_url: str) -> List[Dict]:
        """
        Get price history for a product.
        
        Args:
            product_url: URL of the product
            
        Returns:
            List of price history entries
        """
        pass

    def is_available(self) -> bool:
        """Check if the provider is available (API key configured, etc.)."""
        return True

    def get_platform_info(self) -> Dict:
        """Get platform information."""
        return {
            'name': self.platform_name,
            'base_url': self.base_url,
            'is_available': self.is_available(),
        }
