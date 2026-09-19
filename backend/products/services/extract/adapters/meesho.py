"""Meesho adapter."""

from __future__ import annotations

from ..base import BaseProductExtractor, ExtractedProduct
from ._common import run_standard

_CONFIG = {
    "selectors": {
        "title": ["h1", "div[class*='ProductName']"],
        "price": ["span[class*='Price']", "div[class*='Price']"],
        "rating": ["span[class*='Rating']"],
        "image": ["img[class*='Product']"],
    },
    "id_patterns": [r"/(\d{5,})(?:\?|/|$)"],
    "wait_selector": "h1",
}


class MeeshoExtractor(BaseProductExtractor):
    name = "Meesho"
    domains = ("meesho.com",)
    # No public affiliate/product API (as of Sept 2026) — inherits the
    # no-op official_api(); pipeline proceeds to HTTP extraction.

    def extract(self, url: str) -> ExtractedProduct:
        return run_standard(platform=self.name, url=url, cfg=dict(_CONFIG))
