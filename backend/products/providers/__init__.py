from typing import Dict
from .base import BaseProvider, ProductData
from .amazon import AmazonProvider
from .flipkart import FlipkartProvider
from .ajio import AJIOProvider
from .myntra import MyntraProvider
from .meesho import MeeshoProvider
from .croma import CromaProvider
from .reliance_digital import RelianceDigitalProvider
from .tata_cliq import TataCLiQProvider

__all__ = [
    'BaseProvider',
    'ProductData',
    'AmazonProvider',
    'FlipkartProvider',
    'AJIOProvider',
    'MyntraProvider',
    'MeeshoProvider',
    'CromaProvider',
    'RelianceDigitalProvider',
    'TataCLiQProvider',
]

# Provider registry
PROVIDERS = {
    'amazon': AmazonProvider,
    'flipkart': FlipkartProvider,
    'ajio': AJIOProvider,
    'myntra': MyntraProvider,
    'meesho': MeeshoProvider,
    'croma': CromaProvider,
    'reliance_digital': RelianceDigitalProvider,
    'tata_cliq': TataCLiQProvider,
}


def get_provider(platform_key: str) -> BaseProvider:
    """Get provider instance by platform key."""
    provider_class = PROVIDERS.get(platform_key)
    if provider_class:
        return provider_class()
    raise ValueError(f"Unknown platform: {platform_key}")


def get_all_providers() -> Dict[str, BaseProvider]:
    """Get all provider instances."""
    return {key: cls() for key, cls in PROVIDERS.items()}
