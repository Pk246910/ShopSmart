"""AJIO adapter."""

from __future__ import annotations

from ..base import BaseProductExtractor, ExtractedProduct
from ._common import run_standard

_CONFIG = {
    "selectors": {
        "title": ["div.item-name", "h1"],
        "price": ["div.price strong", "span.price"],
        "mrp": ["span.mrp"],
        "rating": ["div.rating"],
        "image": ["img.rilrtl-products-img__img"],
        "brand": ["div.brand"],
    },
    "id_patterns": [r"/(\d{6,})(?:\?|/|$)"],
    "wait_selector": "div.item-name",
}


class AjioExtractor(BaseProductExtractor):
    name = "AJIO"
    domains = ("ajio.com",)
    # No public affiliate/product API (as of Sept 2026) — inherits the
    # no-op official_api(); pipeline proceeds to HTTP extraction.

    def extract(self, url: str) -> ExtractedProduct:
        return run_standard(platform=self.name, url=url, cfg=dict(_CONFIG))
