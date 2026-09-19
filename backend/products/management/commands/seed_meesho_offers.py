"""Add Meesho offers for Meesho-relevant categories.

Purely ADDITIVE: uses update_or_create keyed on (product, store_name), never
deletes or modifies existing records. Meesho is the one supported platform
with zero offers in the database, so this restores the 8-platform
comparison workflow.

All records are labelled data_source="demo" / data_status="demonstration"
(the same convention as the other seed commands) — the frontend renders
them with the "Demo" badge, never as live scraped prices. Prices are
derived from each product's verified lowest in-stock offer.
"""

import math
import re
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from products.models import Platform, PriceHistory, Product, ProductOffer

# Categories Meesho actually sells (budget fashion, footwear, watches,
# personal audio, small appliances). Premium laptops/cameras/TVs excluded.
MEESHO_CATEGORIES = {
    "Fashion",
    "Footwear",
    "Watches",
    "Earbuds",
    "Headphones",
    "Kitchen Appliances",
}


def _slug(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60].strip("-") or "product"


class Command(BaseCommand):
    help = "Add demo-labelled Meesho offers (additive only, no deletes)"

    def handle(self, *args, **options):
        platform, _ = Platform.objects.get_or_create(
            name="Meesho", defaults={"is_active": True}
        )
        now = timezone.now()
        created_offers = 0
        created_history = 0

        products = Product.objects.filter(
            category__in=MEESHO_CATEGORIES
        ).prefetch_related("offers")

        for product in products:
            if product.offers.filter(store_name="Meesho").exists():
                continue
            base = product.offers.filter(
                in_stock=True, current_price__gt=0
            ).order_by("current_price").first()
            if not base:
                continue

            base_price = float(base.current_price)
            price = max(99, round(base_price * 0.97))
            base_mrp = float(base.original_price) if base.original_price else 0
            mrp = base_mrp if base_mrp > price else round(price * 1.35)

            offer, created = ProductOffer.objects.update_or_create(
                product=product,
                store_name="Meesho",
                defaults={
                    "platform": platform,
                    "current_price": Decimal(str(price)),
                    "original_price": Decimal(str(mrp)),
                    "product_url": f"https://www.meesho.com/{_slug(product.title)}",
                    "rating": base.rating,
                    "reviews_count": 500 + (product.id * 137) % 3500,
                    "in_stock": True,
                    "delivery_days": 4,
                    "delivery_time": "Delivery in 4 days",
                    "data_source": "demo",
                    "data_status": "demonstration",
                },
            )
            if created:
                created_offers += 1
                # Deterministic 30-day zigzag (sin-based, no randomness).
                records = []
                for day_offset in range(30, -1, -1):
                    variation = 0.04 * math.sin(day_offset * 0.7 + product.id)
                    hist_price = round(price * (1 + variation), 2)
                    records.append(PriceHistory(
                        product=product,
                        store_name="Meesho",
                        price=Decimal(str(hist_price)),
                        recorded_at=now - timezone.timedelta(days=day_offset),
                    ))
                PriceHistory.objects.bulk_create(records)
                created_history += len(records)

        self.stdout.write(self.style.SUCCESS(
            f"Meesho seed complete: {created_offers} offers, "
            f"{created_history} price history records (additive only)."
        ))
