"""Central platform detector + adapter registry.

Detection reuses the existing URLAnalyzer domain map (single source of
truth); this module only reshapes the result and resolves adapters.
Adding a platform = new adapter class + domains entry, nothing else.
"""

from products.services.url_analyzer import PLATFORM_DOMAINS, URLAnalyzer


def detect_platform(url: str) -> dict:
    """Return {platform, valid} — never guess from product names."""
    result = URLAnalyzer.detect_platform(url or "")
    if result.get("supported"):
        return {"platform": result["platform"], "valid": True}
    return {"platform": None, "valid": False}


def supported_platforms() -> list:
    return URLAnalyzer.get_supported_platforms()


def _adapter_classes() -> list:
    from .adapters.ajio import AjioExtractor
    from .adapters.amazon import AmazonExtractor
    from .adapters.croma import CromaExtractor
    from .adapters.flipkart import FlipkartExtractor
    from .adapters.meesho import MeeshoExtractor
    from .adapters.myntra import MyntraExtractor
    from .adapters.reliance import RelianceExtractor
    from .adapters.tatacliq import TataCliqExtractor

    return [
        AmazonExtractor,
        FlipkartExtractor,
        AjioExtractor,
        MyntraExtractor,
        MeeshoExtractor,
        CromaExtractor,
        RelianceExtractor,
        TataCliqExtractor,
    ]


def get_adapter(platform_or_url: str):
    """Resolve an adapter by platform name or full URL. Returns None."""
    value = (platform_or_url or "").strip()
    for cls in _adapter_classes():
        if value == cls.name or cls.match(value):
            return cls()
    return None
