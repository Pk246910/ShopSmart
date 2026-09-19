"""Layered real-product-data extraction pipeline.

Levels (first success with usable data wins):
  L1 official API / authorized feed (env-configured only)
  L2 normal HTTP request (requests, headers, timeout, redirects)
  L3 structured page data (JSON-LD, product schema, OG/meta tags)
  L4 rendered browser (Playwright, with anti-bot STOP rules)
  L5 embedded application data exposed by the rendered page
  L6 graceful failure (structured result, nothing fabricated)

Never invents prices, ratings, reviews, specs, availability, delivery
info, offers or URLs. Unverifiable fields are None.
"""

from .base import (
    CONFIDENCE_FAILED,
    CONFIDENCE_HIGH,
    CONFIDENCE_LOW,
    CONFIDENCE_MEDIUM,
    METHOD_BROWSER,
    METHOD_CSS_SELECTOR,
    METHOD_JSON_LD,
    METHOD_METADATA,
    METHOD_NONE,
    METHOD_OFFICIAL_API,
    SOURCE_DATABASE,
    SOURCE_LIVE_EXTRACTION,
    SOURCE_OFFICIAL_API,
    SOURCE_UNAVAILABLE,
    SOURCE_USER_URL,
    BaseProductExtractor,
    ExtractedProduct,
)
from .pipeline import extract_product
from .registry import detect_platform, get_adapter, supported_platforms

__all__ = [
    "CONFIDENCE_FAILED",
    "CONFIDENCE_HIGH",
    "CONFIDENCE_LOW",
    "CONFIDENCE_MEDIUM",
    "METHOD_BROWSER",
    "METHOD_CSS_SELECTOR",
    "METHOD_JSON_LD",
    "METHOD_METADATA",
    "METHOD_NONE",
    "METHOD_OFFICIAL_API",
    "SOURCE_DATABASE",
    "SOURCE_LIVE_EXTRACTION",
    "SOURCE_OFFICIAL_API",
    "SOURCE_UNAVAILABLE",
    "SOURCE_USER_URL",
    "BaseProductExtractor",
    "ExtractedProduct",
    "detect_platform",
    "extract_product",
    "get_adapter",
    "supported_platforms",
]
