"""Tata CLiQ adapter."""

from __future__ import annotations

from ..base import BaseProductExtractor, ExtractedProduct
from ._common import run_standard

_CONFIG = {
    "selectors": {
        "title": ["h1.ProductName", "h1"],
        "price": ["span.ProductPrice", "span.amount"],
        "mrp": ["span.mrp"],
        "rating": ["span.rating"],
        "image": ["img.product-hero-img"],
    },
    "id_patterns": [r"[?&]pid=(\d+)", r"/(\d{5,})(?:\?|/|$)"],
    "wait_selector": "h1.ProductName",
}


class TataCliqExtractor(BaseProductExtractor):
    name = "Tata CLiQ"
    domains = ("tatacliq.com", "tatcliq.com")
    # No public affiliate/product API (as of Sept 2026) — inherits the
    # no-op official_api(); pipeline proceeds to HTTP extraction.

    def extract(self, url: str) -> ExtractedProduct:
        return run_standard(platform=self.name, url=url, cfg=dict(_CONFIG))
