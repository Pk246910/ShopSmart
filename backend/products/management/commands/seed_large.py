import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Platform, Product, ProductOffer, PriceHistory


def _img(category, label):
    import re as _re
    slug = label.lower()
    slug = _re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = _re.sub(r'[\s]+', '-', slug.strip())
    slug = _re.sub(r'-+', '-', slug)
    slug = slug[:80].rstrip('-')
    return f"/products/{slug}.svg"


def _make_offers(product_data, base_price, mrp, category):
    """Generate 3-5 offers across appropriate platforms for the given category."""
    electronics_platforms = ["Amazon", "Flipkart", "Croma", "Reliance Digital", "Tata CLiQ"]
    fashion_platforms = ["Amazon", "Flipkart", "Myntra", "AJIO"]
    kitchen_platforms = ["Amazon", "Flipkart", "Croma"]
    watch_platforms = ["Amazon", "Flipkart", "Croma"]

    if category in ("Fashion", "Footwear"):
        platforms = fashion_platforms
    elif category == "Kitchen Appliances":
        platforms = kitchen_platforms
    elif category == "Watches":
        platforms = watch_platforms
    else:
        platforms = electronics_platforms

    num_offers = random.randint(3, 5)
    chosen_platforms = random.sample(platforms, min(num_offers, len(platforms)))

    coupon_pool = [
        ("BANK2000", 2000), ("HDFC3000", 3000), ("FLAT500", 500),
        ("FLAT1000", 1000), ("EXCHANGE5000", 5000), ("RELIANCE1000", 1000),
        ("", 0), ("", 0), ("", 0),
    ]

    # Explicit per-platform domains (same approach as seed_target.py).
    # The naive f"{store}.in" pattern produced wrong domains such as
    # flipkart.in, croma.in and tatacliq.in.
    domain_map = {
        "Amazon": "amazon.in",
        "Flipkart": "flipkart.com",
        "Croma": "croma.com",
        "Reliance Digital": "reliancedigital.in",
        "Tata CLiQ": "tatacliq.com",
        "Myntra": "myntra.com",
        "AJIO": "ajio.com",
    }

    offers = []
    for store in chosen_platforms:
        variation = random.uniform(-0.10, 0.10)
        price = round(base_price * (1 + variation), 0)
        if price > mrp:
            price = round(mrp * random.uniform(0.85, 0.98), 0)
        price = int(price // 1 * 1)  # round to integer

        rating = round(random.uniform(3.5, 4.8), 1)
        reviews = random.randint(100, 45000)
        delivery = random.randint(1, 7)

        if random.random() < 0.4:
            c_code, c_disc = random.choice([c for c in coupon_pool if c[0]])
            # coupon_discount should not exceed the price
            c_disc = min(c_disc, price // 4)
        else:
            c_code, c_disc = "", 0

        offers.append({
            "store_name": store,
            "price": price,
            "mrp": mrp,
            "rating": rating,
            "reviews": reviews,
            "delivery_days": delivery,
            "coupon": c_code,
            "coupon_discount": c_disc,
            "url": f"https://www.{domain_map.get(store, store.lower().replace(' ', ''))}/{product_data['title'][:30].replace(' ', '-').lower()}",
        })
    return offers


# ---------------------------------------------------------------------------
# SMARTPHONES (50 products)
# ---------------------------------------------------------------------------
SMARTPHONES = [
    # Samsung
    {"title": "Samsung Galaxy S24 5G 128GB Onyx Black", "brand": "Samsung", "price": 64999, "mrp": 79999, "specs": {"Display": '6.2" Dynamic AMOLED 2X, 120Hz', "Processor": "Exynos 2400", "RAM": "8 GB", "Storage": "128 GB", "Camera": "50MP + 12MP + 10MP", "Battery": "4000 mAh"}},
    {"title": "Samsung Galaxy S24 5G 256GB Cobalt Violet", "brand": "Samsung", "price": 69999, "mrp": 84999, "specs": {"Display": '6.2" Dynamic AMOLED 2X, 120Hz', "Processor": "Exynos 2400", "RAM": "8 GB", "Storage": "256 GB", "Camera": "50MP + 12MP + 10MP", "Battery": "4000 mAh"}},
    {"title": "Samsung Galaxy S24+ 5G 256GB Amber Yellow", "brand": "Samsung", "price": 79999, "mrp": 99999, "specs": {"Display": '6.7" Dynamic AMOLED 2X, 120Hz', "Processor": "Exynos 2400", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 12MP + 10MP", "Battery": "4900 mAh"}},
    {"title": "Samsung Galaxy S24 Ultra 5G 256GB Titanium Black", "brand": "Samsung", "price": 104999, "mrp": 134999, "specs": {"Display": '6.8" Dynamic AMOLED 2X, 120Hz', "Processor": "Snapdragon 8 Gen 3", "RAM": "12 GB", "Storage": "256 GB", "Camera": "200MP + 12MP + 10MP + 50MP", "Battery": "5000 mAh"}},
    {"title": "Samsung Galaxy S24 Ultra 5G 512GB Titanium Gray", "brand": "Samsung", "price": 124999, "mrp": 154999, "specs": {"Display": '6.8" Dynamic AMOLED 2X, 120Hz', "Processor": "Snapdragon 8 Gen 3", "RAM": "12 GB", "Storage": "512 GB", "Camera": "200MP + 12MP + 10MP + 50MP", "Battery": "5000 mAh"}},
    {"title": "Samsung Galaxy S25 5G 256GB Navy", "brand": "Samsung", "price": 74999, "mrp": 84999, "specs": {"Display": '6.2" Dynamic AMOLED 2X, 120Hz', "Processor": "Snapdragon 8 Elite", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 12MP + 10MP", "Battery": "4000 mAh"}},
    {"title": "Samsung Galaxy S25+ 5G 256GB Ice Blue", "brand": "Samsung", "price": 89999, "mrp": 104999, "specs": {"Display": '6.7" Dynamic AMOLED 2X, 120Hz', "Processor": "Snapdragon 8 Elite", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 12MP + 10MP", "Battery": "4900 mAh"}},
    {"title": "Samsung Galaxy S25 Ultra 5G 256GB Titanium Black", "brand": "Samsung", "price": 134999, "mrp": 154999, "specs": {"Display": '6.9" Dynamic AMOLED 2X, 120Hz', "Processor": "Snapdragon 8 Elite", "RAM": "12 GB", "Storage": "256 GB", "Camera": "200MP + 50MP + 10MP + 50MP", "Battery": "5000 mAh"}},
    {"title": "Samsung Galaxy S25 Ultra 5G 512GB Titanium Silverblue", "brand": "Samsung", "price": 154999, "mrp": 174999, "specs": {"Display": '6.9" Dynamic AMOLED 2X, 120Hz', "Processor": "Snapdragon 8 Elite", "RAM": "12 GB", "Storage": "512 GB", "Camera": "200MP + 50MP + 10MP + 50MP", "Battery": "5000 mAh"}},
    {"title": "Samsung Galaxy A54 5G 128GB Awesome Graphite", "brand": "Samsung", "price": 28999, "mrp": 38999, "specs": {"Display": '6.4" Super AMOLED, 120Hz', "Processor": "Exynos 1380", "RAM": "8 GB", "Storage": "128 GB", "Camera": "50MP + 12MP + 5MP", "Battery": "5000 mAh"}},
    {"title": "Samsung Galaxy A54 5G 256GB Awesome White", "brand": "Samsung", "price": 32999, "mrp": 40999, "specs": {"Display": '6.4" Super AMOLED, 120Hz', "Processor": "Exynos 1380", "RAM": "8 GB", "Storage": "256 GB", "Camera": "50MP + 12MP + 5MP", "Battery": "5000 mAh"}},
    {"title": "Samsung Galaxy A35 5G 128GB Awesome Lilac", "brand": "Samsung", "price": 23999, "mrp": 29999, "specs": {"Display": '6.6" Super AMOLED, 120Hz', "Processor": "Exynos 1380", "RAM": "8 GB", "Storage": "128 GB", "Camera": "50MP + 8MP + 5MP", "Battery": "5000 mAh"}},
    {"title": "Samsung Galaxy M54 5G 256GB Midnight Blue", "brand": "Samsung", "price": 26999, "mrp": 35999, "specs": {"Display": '6.7" Super AMOLED, 120Hz', "Processor": "Snapdragon 782G", "RAM": "8 GB", "Storage": "256 GB", "Camera": "108MP + 8MP + 2MP", "Battery": "6000 mAh"}},
    {"title": "Samsung Galaxy F54 5G 256GB Meteor Blue", "brand": "Samsung", "price": 27999, "mrp": 34999, "specs": {"Display": '6.7" Super AMOLED, 120Hz', "Processor": "Exynos 1380", "RAM": "8 GB", "Storage": "256 GB", "Camera": "108MP + 8MP + 2MP", "Battery": "6000 mAh"}},
    {"title": "Samsung Galaxy Z Fold5 5G 256GB Phantom Black", "brand": "Samsung", "price": 134999, "mrp": 164999, "specs": {"Display": '7.6" Foldable AMOLED + 6.2" Cover', "Processor": "Snapdragon 8 Gen 2", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 12MP + 10MP", "Battery": "4400 mAh"}},
    {"title": "Samsung Galaxy Z Flip5 5G 256GB Mint", "brand": "Samsung", "price": 84999, "mrp": 99999, "specs": {"Display": '6.7" Foldable AMOLED + 3.4" Cover', "Processor": "Snapdragon 8 Gen 2", "RAM": "8 GB", "Storage": "256 GB", "Camera": "12MP + 12MP", "Battery": "3700 mAh"}},
    # Apple
    {"title": "Apple iPhone 15 128GB Black", "brand": "Apple", "price": 65900, "mrp": 79900, "specs": {"Display": '6.1" Super Retina XDR OLED', "Processor": "Apple A16 Bionic", "RAM": "6 GB", "Storage": "128 GB", "Camera": "48MP + 12MP", "Battery": "3349 mAh"}},
    {"title": "Apple iPhone 15 128GB Blue", "brand": "Apple", "price": 65900, "mrp": 79900, "specs": {"Display": '6.1" Super Retina XDR OLED', "Processor": "Apple A16 Bionic", "RAM": "6 GB", "Storage": "128 GB", "Camera": "48MP + 12MP", "Battery": "3349 mAh"}},
    {"title": "Apple iPhone 15 Plus 128GB Yellow", "brand": "Apple", "price": 76900, "mrp": 89900, "specs": {"Display": '6.7" Super Retina XDR OLED', "Processor": "Apple A16 Bionic", "RAM": "6 GB", "Storage": "128 GB", "Camera": "48MP + 12MP", "Battery": "4383 mAh"}},
    {"title": "Apple iPhone 15 Pro 128GB Natural Titanium", "brand": "Apple", "price": 104900, "mrp": 134900, "specs": {"Display": '6.1" Super Retina XDR ProMotion', "Processor": "Apple A17 Pro", "RAM": "8 GB", "Storage": "128 GB", "Camera": "48MP + 12MP + 12MP", "Battery": "3274 mAh"}},
    {"title": "Apple iPhone 15 Pro 256GB Blue Titanium", "brand": "Apple", "price": 119900, "mrp": 149900, "specs": {"Display": '6.1" Super Retina XDR ProMotion', "Processor": "Apple A17 Pro", "RAM": "8 GB", "Storage": "256 GB", "Camera": "48MP + 12MP + 12MP", "Battery": "3274 mAh"}},
    {"title": "Apple iPhone 15 Pro Max 256GB Natural Titanium", "brand": "Apple", "price": 134900, "mrp": 159900, "specs": {"Display": '6.7" Super Retina XDR ProMotion', "Processor": "Apple A17 Pro", "RAM": "8 GB", "Storage": "256 GB", "Camera": "48MP + 12MP + 12MP", "Battery": "4441 mAh"}},
    {"title": "Apple iPhone 16 128GB Black", "brand": "Apple", "price": 79900, "mrp": 84900, "specs": {"Display": '6.1" Super Retina XDR OLED', "Processor": "Apple A18", "RAM": "8 GB", "Storage": "128 GB", "Camera": "48MP + 12MP", "Battery": "3561 mAh"}},
    {"title": "Apple iPhone 16 128GB Ultramarine", "brand": "Apple", "price": 79900, "mrp": 84900, "specs": {"Display": '6.1" Super Retina XDR OLED', "Processor": "Apple A18", "RAM": "8 GB", "Storage": "128 GB", "Camera": "48MP + 12MP", "Battery": "3561 mAh"}},
    {"title": "Apple iPhone 16 Plus 128GB Teal", "brand": "Apple", "price": 89900, "mrp": 94900, "specs": {"Display": '6.7" Super Retina XDR OLED', "Processor": "Apple A18", "RAM": "8 GB", "Storage": "128 GB", "Camera": "48MP + 12MP", "Battery": "4674 mAh"}},
    {"title": "Apple iPhone 16 Pro 128GB Desert Titanium", "brand": "Apple", "price": 119900, "mrp": 134900, "specs": {"Display": '6.3" Super Retina XDR ProMotion', "Processor": "Apple A18 Pro", "RAM": "8 GB", "Storage": "128 GB", "Camera": "48MP + 12MP + 12MP", "Battery": "3582 mAh"}},
    {"title": "Apple iPhone 16 Pro 256GB Natural Titanium", "brand": "Apple", "price": 134900, "mrp": 149900, "specs": {"Display": '6.3" Super Retina XDR ProMotion', "Processor": "Apple A18 Pro", "RAM": "8 GB", "Storage": "256 GB", "Camera": "48MP + 12MP + 12MP", "Battery": "3582 mAh"}},
    {"title": "Apple iPhone 16 Pro Max 256GB Black Titanium", "brand": "Apple", "price": 149900, "mrp": 159900, "specs": {"Display": '6.9" Super Retina XDR ProMotion', "Processor": "Apple A18 Pro", "RAM": "8 GB", "Storage": "256 GB", "Camera": "48MP + 12MP + 12MP", "Battery": "4685 mAh"}},
    {"title": "Apple iPhone SE (2022) 64GB Starlight", "brand": "Apple", "price": 42900, "mrp": 49900, "specs": {"Display": '4.7" Retina IPS LCD', "Processor": "Apple A15 Bionic", "RAM": "4 GB", "Storage": "64 GB", "Camera": "12MP", "Battery": "2018 mAh"}},
    # OnePlus
    {"title": "OnePlus 12 5G 256GB Silky Black", "brand": "OnePlus", "price": 64999, "mrp": 74999, "specs": {"Display": '6.82" LTPO AMOLED, 120Hz', "Processor": "Snapdragon 8 Gen 3", "RAM": "16 GB", "Storage": "256 GB", "Camera": "50MP + 48MP + 64MP", "Battery": "5400 mAh"}},
    {"title": "OnePlus 11 5G 256GB Titan Black", "brand": "OnePlus", "price": 49999, "mrp": 64999, "specs": {"Display": '6.7" LTPO AMOLED, 120Hz', "Processor": "Snapdragon 8 Gen 2", "RAM": "16 GB", "Storage": "256 GB", "Camera": "50MP + 48MP + 32MP", "Battery": "5000 mAh"}},
    {"title": "OnePlus Nord CE4 5G 128GB Dark Chrome", "brand": "OnePlus", "price": 21999, "mrp": 26999, "specs": {"Display": '6.7" AMOLED, 120Hz', "Processor": "Snapdragon 7 Gen 3", "RAM": "8 GB", "Storage": "128 GB", "Camera": "50MP + 2MP", "Battery": "5500 mAh"}},
    {"title": "OnePlus Nord CE4 5G 256GB Celadon Marble", "brand": "OnePlus", "price": 24999, "mrp": 29999, "specs": {"Display": '6.7" AMOLED, 120Hz', "Processor": "Snapdragon 7 Gen 3", "RAM": "8 GB", "Storage": "256 GB", "Camera": "50MP + 2MP", "Battery": "5500 mAh"}},
    # Xiaomi
    {"title": "Xiaomi 14 5G 256GB Black", "brand": "Xiaomi", "price": 64999, "mrp": 74999, "specs": {"Display": '6.36" LTPO AMOLED, 120Hz', "Processor": "Snapdragon 8 Gen 3", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 50MP + 50MP (Leica)", "Battery": "4610 mAh"}},
    {"title": "Xiaomi 13 5G 256GB Black", "brand": "Xiaomi", "price": 44999, "mrp": 59999, "specs": {"Display": '6.36" LTPO AMOLED, 120Hz', "Processor": "Snapdragon 8 Gen 2", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 12MP + 10MP (Leica)", "Battery": "4500 mAh"}},
    {"title": "Redmi Note 13 5G 128GB Arctic White", "brand": "Xiaomi", "price": 15999, "mrp": 19999, "specs": {"Display": '6.67" AMOLED, 120Hz', "Processor": "Snapdragon 685", "RAM": "6 GB", "Storage": "128 GB", "Camera": "108MP + 2MP + 2MP", "Battery": "5000 mAh"}},
    {"title": "Redmi Note 13 Pro 5G 128GB Midnight Black", "brand": "Xiaomi", "price": 21999, "mrp": 27999, "specs": {"Display": '6.67" AMOLED, 120Hz', "Processor": "Snapdragon 7s Gen 2", "RAM": "8 GB", "Storage": "128 GB", "Camera": "200MP + 8MP + 2MP", "Battery": "5100 mAh"}},
    # Realme
    {"title": "Realme 12 Pro 5G 256GB Navigator Beige", "brand": "Realme", "price": 25999, "mrp": 32999, "specs": {"Display": '6.7" AMOLED, 120Hz', "Processor": "Snapdragon 7s Gen 2", "RAM": "8 GB", "Storage": "256 GB", "Camera": "50MP + 8MP + 32MP (Periscope)", "Battery": "5000 mAh"}},
    {"title": "Realme GT 6 5G 256GB Fluid Silver", "brand": "Realme", "price": 35999, "mrp": 42999, "specs": {"Display": '6.78" LTPO AMOLED, 120Hz', "Processor": "Snapdragon 8s Gen 3", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 8MP + 50MP", "Battery": "5500 mAh"}},
    # Vivo
    {"title": "Vivo X100 5G 256GB Asteroid Black", "brand": "Vivo", "price": 64999, "mrp": 79999, "specs": {"Display": '6.78" LTPO AMOLED, 120Hz', "Processor": "Dimensity 9300", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 50MP + 64MP (Zeiss)", "Battery": "5000 mAh"}},
    {"title": "Vivo V30 5G 256GB Noble Black", "brand": "Vivo", "price": 33999, "mrp": 41999, "specs": {"Display": '6.78" AMOLED, 120Hz', "Processor": "Snapdragon 7 Gen 3", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 50MP", "Battery": "5000 mAh"}},
    # OPPO
    {"title": "OPPO Find X7 5G 256GB海闊天空 Black", "brand": "OPPO", "price": 64999, "mrp": 79999, "specs": {"Display": '6.78" LTPO AMOLED, 120Hz', "Processor": "Dimensity 9300", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 50MP + 64MP (Hasselblad)", "Battery": "5000 mAh"}},
    {"title": "OPPO Reno 11 5G 256GB Rock Grey", "brand": "OPPO", "price": 29999, "mrp": 37999, "specs": {"Display": '6.7" AMOLED, 120Hz', "Processor": "Dimensity 7050", "RAM": "8 GB", "Storage": "256 GB", "Camera": "50MP + 8MP + 32MP", "Battery": "5000 mAh"}},
    # Nothing
    {"title": "Nothing Phone (2a) 128GB Black", "brand": "Nothing", "price": 19999, "mrp": 23999, "specs": {"Display": '6.7" AMOLED, 120Hz', "Processor": "Dimensity 7200 Pro", "RAM": "8 GB", "Storage": "128 GB", "Camera": "50MP + 50MP", "Battery": "5000 mAh"}},
    {"title": "Nothing Phone (2) 256GB White", "brand": "Nothing", "price": 33999, "mrp": 45999, "specs": {"Display": '6.7" LTPO OLED, 120Hz', "Processor": "Snapdragon 8+ Gen 1", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 50MP", "Battery": "4700 mAh"}},
    # Motorola
    {"title": "Motorola Edge 50 Pro 5G 256GB Black Beauty", "brand": "Motorola", "price": 31999, "mrp": 39999, "specs": {"Display": '6.7" pOLED, 144Hz', "Processor": "Snapdragon 7 Gen 3", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 13MP + 10MP", "Battery": "4500 mAh"}},
    {"title": "Motorola Razr 50 Ultra 5G 256GB Midnight Blue", "brand": "Motorola", "price": 69999, "mrp": 89999, "specs": {"Display": '6.9" Foldable pOLED + 4" Cover', "Processor": "Snapdragon 8s Gen 3", "RAM": "12 GB", "Storage": "256 GB", "Camera": "50MP + 50MP", "Battery": "4000 mAh"}},
    # Google
    {"title": "Google Pixel 8 128GB Obsidian", "brand": "Google", "price": 69999, "mrp": 79999, "specs": {"Display": '6.2" OLED, 120Hz', "Processor": "Google Tensor G3", "RAM": "8 GB", "Storage": "128 GB", "Camera": "50MP + 12MP", "Battery": "4575 mAh"}},
    {"title": "Google Pixel 8a 128GB Charcoal", "brand": "Google", "price": 44999, "mrp": 52999, "specs": {"Display": '6.1" OLED, 120Hz', "Processor": "Google Tensor G3", "RAM": "8 GB", "Storage": "128 GB", "Camera": "64MP + 13MP", "Battery": "4492 mAh"}},
]

# ---------------------------------------------------------------------------
# LAPTOPS (30 products)
# ---------------------------------------------------------------------------
LAPTOPS = [
    {"title": "Apple MacBook Air M2 13-inch 8GB 256GB Midnight", "brand": "Apple", "price": 99900, "mrp": 119900, "specs": {"Display": '13.6" Liquid Retina', "Processor": "Apple M2 (8-core)", "RAM": "8 GB Unified", "Storage": "256 GB SSD", "Battery": "Up to 18 hours", "Weight": "1.24 kg"}},
    {"title": "Apple MacBook Air M2 13-inch 16GB 512GB Starlight", "brand": "Apple", "price": 124900, "mrp": 144900, "specs": {"Display": '13.6" Liquid Retina', "Processor": "Apple M2 (8-core)", "RAM": "16 GB Unified", "Storage": "512 GB SSD", "Battery": "Up to 18 hours", "Weight": "1.24 kg"}},
    {"title": "Apple MacBook Air M3 15-inch 16GB 512GB Midnight", "brand": "Apple", "price": 144900, "mrp": 154900, "specs": {"Display": '15.3" Liquid Retina', "Processor": "Apple M3 (8-core CPU, 10-core GPU)", "RAM": "16 GB Unified", "Storage": "512 GB SSD", "Battery": "Up to 18 hours", "Weight": "1.51 kg"}},
    {"title": "Apple MacBook Pro M3 14-inch 18GB 512GB Space Black", "brand": "Apple", "price": 169900, "mrp": 179900, "specs": {"Display": '14.2" Liquid Retina XDR', "Processor": "Apple M3 (8-core CPU, 10-core GPU)", "RAM": "18 GB Unified", "Storage": "512 GB SSD", "Battery": "Up to 17 hours", "Weight": "1.55 kg"}},
    {"title": "Dell XPS 15 9530 13th Gen i7 16GB 512GB", "brand": "Dell", "price": 134999, "mrp": 169999, "specs": {"Display": '15.6" 3.5K OLED, 60Hz', "Processor": "Intel Core i7-13700H", "RAM": "16 GB DDR5", "Storage": "512 GB SSD", "GPU": "NVIDIA RTX 4050 6GB", "Weight": "1.86 kg"}},
    {"title": "Dell XPS 16 9640 Ultra 7 32GB 1TB", "brand": "Dell", "price": 199999, "mrp": 249999, "specs": {"Display": '16.3" OLED, 120Hz', "Processor": "Intel Core Ultra 7 155H", "RAM": "32 GB LPDDR5x", "Storage": "1 TB SSD", "GPU": "NVIDIA RTX 4060 8GB", "Weight": "2.0 kg"}},
    {"title": "Dell Inspiron 15 3520 12th Gen i5 8GB 512GB", "brand": "Dell", "price": 42999, "mrp": 57999, "specs": {"Display": '15.6" FHD IPS', "Processor": "Intel Core i5-1235U", "RAM": "8 GB DDR4", "Storage": "512 GB SSD", "GPU": "Intel Iris Xe", "Weight": "1.65 kg"}},
    {"title": "Dell Latitude 5440 13th Gen i5 16GB 512GB", "brand": "Dell", "price": 72999, "mrp": 89999, "specs": {"Display": '14" FHD IPS', "Processor": "Intel Core i5-1345U vPro", "RAM": "16 GB DDR5", "Storage": "512 GB SSD", "GPU": "Intel Iris Xe", "Weight": "1.48 kg"}},
    {"title": "HP Pavilion 15 13th Gen i5 8GB 512GB", "brand": "HP", "price": 47999, "mrp": 62999, "specs": {"Display": '15.6" FHD IPS, 144Hz', "Processor": "Intel Core i5-1335U", "RAM": "8 GB DDR4", "Storage": "512 GB SSD", "GPU": "Intel Iris Xe", "Weight": "1.74 kg"}},
    {"title": "HP Spectre x360 14 2-in-1 13th Gen i7 16GB 1TB", "brand": "HP", "price": 139999, "mrp": 169999, "specs": {"Display": '14" 2.8K OLED Touch, 120Hz', "Processor": "Intel Core i7-1355U", "RAM": "16 GB LPDDR5", "Storage": "1 TB SSD", "GPU": "Intel Iris Xe", "Weight": "1.44 kg"}},
    {"title": "HP Victus 15 13th Gen i5 RTX 4050 16GB 512GB", "brand": "HP", "price": 69999, "mrp": 84999, "specs": {"Display": '15.6" FHD IPS, 144Hz', "Processor": "Intel Core i5-13500H", "RAM": "16 GB DDR4", "Storage": "512 GB SSD", "GPU": "NVIDIA RTX 4050 6GB", "Weight": "2.29 kg"}},
    {"title": "Lenovo IdeaPad Slim 5 14 13th Gen i5 16GB 512GB", "brand": "Lenovo", "price": 54999, "mrp": 69999, "specs": {"Display": '14" WUXGA IPS, 60Hz', "Processor": "Intel Core i5-1335U", "RAM": "16 GB LPDDR5", "Storage": "512 GB SSD", "GPU": "Intel Iris Xe", "Weight": "1.46 kg"}},
    {"title": "Lenovo ThinkPad E16 Gen 1 13th Gen i5 16GB 512GB", "brand": "Lenovo", "price": 64999, "mrp": 79999, "specs": {"Display": '16" WUXGA IPS', "Processor": "Intel Core i5-1335U", "RAM": "16 GB DDR4", "Storage": "512 GB SSD", "GPU": "Intel Iris Xe", "Weight": "1.81 kg"}},
    {"title": "Lenovo Legion 5 16IAH7H 12th Gen i7 RTX 4060 16GB 1TB", "brand": "Lenovo", "price": 109999, "mrp": 139999, "specs": {"Display": '16" WQXGA IPS, 165Hz', "Processor": "Intel Core i7-12700H", "RAM": "16 GB DDR5", "Storage": "1 TB SSD", "GPU": "NVIDIA RTX 4060 8GB", "Weight": "2.49 kg"}},
    {"title": "ASUS ZenBook 14 OLED 13th Gen i7 16GB 1TB", "brand": "ASUS", "price": 99999, "mrp": 124999, "specs": {"Display": '14" 2.8K OLED, 120Hz', "Processor": "Intel Core i7-1355U", "RAM": "16 GB LPDDR5", "Storage": "1 TB SSD", "GPU": "Intel Iris Xe", "Weight": "1.39 kg"}},
    {"title": "ASUS ROG Strix G16 2024 14th Gen i9 RTX 4070 32GB 1TB", "brand": "ASUS", "price": 179999, "mrp": 209999, "specs": {"Display": '16" QHD+ IPS, 240Hz', "Processor": "Intel Core i9-14900HX", "RAM": "32 GB DDR5", "Storage": "1 TB SSD", "GPU": "NVIDIA RTX 4070 8GB", "Weight": "2.50 kg"}},
    {"title": "ASUS TUF Gaming A15 2024 Ryzen 7 RTX 4050 16GB 512GB", "brand": "ASUS", "price": 79999, "mrp": 94999, "specs": {"Display": '15.6" FHD IPS, 144Hz', "Processor": "AMD Ryzen 7 7435HS", "RAM": "16 GB DDR5", "Storage": "512 GB SSD", "GPU": "NVIDIA RTX 4050 6GB", "Weight": "2.20 kg"}},
    {"title": "Acer Aspire Lite 15 13th Gen i5 8GB 512GB", "brand": "Acer", "price": 39999, "mrp": 52999, "specs": {"Display": '15.6" FHD IPS', "Processor": "Intel Core i5-1335U", "RAM": "8 GB DDR4", "Storage": "512 GB SSD", "GPU": "Intel Iris Xe", "Weight": "1.78 kg"}},
    {"title": "Acer Predator Helios 18 14th Gen i9 RTX 4080 32GB 1TB", "brand": "Acer", "price": 229999, "mrp": 269999, "specs": {"Display": '18" QHD+ IPS, 250Hz', "Processor": "Intel Core i9-14900HX", "RAM": "32 GB DDR5", "Storage": "1 TB SSD", "GPU": "NVIDIA RTX 4080 12GB", "Weight": "3.20 kg"}},
    {"title": "Dell Inspiron 14 5430 13th Gen i7 16GB 1TB", "brand": "Dell", "price": 69999, "mrp": 84999, "specs": {"Display": '14" QHD+ IPS', "Processor": "Intel Core i7-1360P", "RAM": "16 GB LPDDR5", "Storage": "1 TB SSD", "GPU": "Intel Iris Xe", "Weight": "1.53 kg"}},
    {"title": "HP Spectre 16 13th Gen i7 16GB 1TB RTX 4050", "brand": "HP", "price": 159999, "mrp": 194999, "specs": {"Display": '16" 3K+ OLED, 120Hz', "Processor": "Intel Core i7-13700H", "RAM": "16 GB DDR5", "Storage": "1 TB SSD", "GPU": "NVIDIA RTX 4050 6GB", "Weight": "2.06 kg"}},
    {"title": "Lenovo IdeaPad Gaming 3 15ACH6 Ryzen 5 RTX 3050 8GB 512GB", "brand": "Lenovo", "price": 54999, "mrp": 72999, "specs": {"Display": '15.6" FHD IPS, 120Hz', "Processor": "AMD Ryzen 5 5600H", "RAM": "8 GB DDR4", "Storage": "512 GB SSD", "GPU": "NVIDIA RTX 3050 4GB", "Weight": "2.25 kg"}},
    {"title": "ASUS VivoBook 15 13th Gen i5 8GB 512GB", "brand": "ASUS", "price": 42999, "mrp": 54999, "specs": {"Display": '15.6" FHD IPS', "Processor": "Intel Core i5-1335U", "RAM": "8 GB DDR4", "Storage": "512 GB SSD", "GPU": "Intel Iris Xe", "Weight": "1.70 kg"}},
    {"title": "Acer Nitro V 15 13th Gen i5 RTX 4050 16GB 512GB", "brand": "Acer", "price": 74999, "mrp": 89999, "specs": {"Display": '15.6" FHD IPS, 144Hz', "Processor": "Intel Core i5-13420H", "RAM": "16 GB DDR5", "Storage": "512 GB SSD", "GPU": "NVIDIA RTX 4050 6GB", "Weight": "2.10 kg"}},
    {"title": "Apple MacBook Pro M3 Pro 14-inch 18GB 512GB Space Black", "brand": "Apple", "price": 199900, "mrp": 219900, "specs": {"Display": '14.2" Liquid Retina XDR', "Processor": "Apple M3 Pro (11-core CPU, 14-core GPU)", "RAM": "18 GB Unified", "Storage": "512 GB SSD", "Battery": "Up to 17 hours", "Weight": "1.61 kg"}},
    {"title": "Dell XPS 13 9340 Ultra 5 16GB 512GB", "brand": "Dell", "price": 109999, "mrp": 134999, "specs": {"Display": '13.4" FHD+ IPS', "Processor": "Intel Core Ultra 5 125H", "RAM": "16 GB LPDDR5x", "Storage": "512 GB SSD", "GPU": "Intel Arc", "Weight": "1.19 kg"}},
    {"title": "HP Pavilion x360 14 13th Gen i5 8GB 512GB", "brand": "HP", "price": 54999, "mrp": 67999, "specs": {"Display": '14" FHD IPS Touch, 360°', "Processor": "Intel Core i5-1335U", "RAM": "8 GB DDR4", "Storage": "512 GB SSD", "GPU": "Intel Iris Xe", "Weight": "1.57 kg"}},
    {"title": "Lenovo ThinkPad X1 Carbon Gen 11 13th Gen i7 16GB 512GB", "brand": "Lenovo", "price": 139999, "mrp": 174999, "specs": {"Display": '14" WUXGA IPS', "Processor": "Intel Core i7-1365U vPro", "RAM": "16 GB LPDDR5", "Storage": "512 GB SSD", "GPU": "Intel Iris Xe", "Weight": "1.12 kg"}},
    {"title": "ASUS ROG Zephyrus G14 2024 Ryzen 9 RTX 4070 16GB 1TB", "brand": "ASUS", "price": 164999, "mrp": 194999, "specs": {"Display": '14" QHD+ OLED, 120Hz', "Processor": "AMD Ryzen 9 8945HS", "RAM": "16 GB LPDDR5x", "Storage": "1 TB SSD", "GPU": "NVIDIA RTX 4070 8GB", "Weight": "1.72 kg"}},
    {"title": "Acer Swift Go 14 13th Gen i7 16GB 512GB", "brand": "Acer", "price": 64999, "mrp": 79999, "specs": {"Display": '14" WUXGA IPS', "Processor": "Intel Core i7-1355U", "RAM": "16 GB LPDDR5", "Storage": "512 GB SSD", "GPU": "Intel Iris Xe", "Weight": "1.25 kg"}},
]

# ---------------------------------------------------------------------------
# HEADPHONES (30 products)
# ---------------------------------------------------------------------------
HEADPHONES = [
    {"title": "Sony WH-1000XM5 Wireless NC Headphones Black", "brand": "Sony", "price": 26990, "mrp": 34990, "specs": {"Type": "Over-Ear", "Driver": "30mm", "Battery": "30 hours", "ANC": "Adaptive", "Bluetooth": "5.2", "Weight": "250g"}},
    {"title": "Sony WH-1000XM5 Wireless NC Headphones Silver", "brand": "Sony", "price": 27990, "mrp": 34990, "specs": {"Type": "Over-Ear", "Driver": "30mm", "Battery": "30 hours", "ANC": "Adaptive", "Bluetooth": "5.2", "Weight": "250g"}},
    {"title": "Sony WH-1000XM4 Wireless NC Headphones Black", "brand": "Sony", "price": 19990, "mrp": 29990, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "30 hours", "ANC": "Adaptive", "Bluetooth": "5.0", "Weight": "254g"}},
    {"title": "JBL Tune 770NC Wireless Over-Ear Headphones Black", "brand": "JBL", "price": 5999, "mrp": 9999, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "70 hours", "ANC": "Adaptive", "Bluetooth": "5.3", "Weight": "252g"}},
    {"title": "JBL Tune 770NC Wireless Over-Ear Headphones Blue", "brand": "JBL", "price": 5999, "mrp": 9999, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "70 hours", "ANC": "Adaptive", "Bluetooth": "5.3", "Weight": "252g"}},
    {"title": "JBL Tune 520BT Wireless On-Ear Headphones Black", "brand": "JBL", "price": 2499, "mrp": 4999, "specs": {"Type": "On-Ear", "Driver": "32mm", "Battery": "57 hours", "ANC": "No", "Bluetooth": "5.3", "Weight": "174g"}},
    {"title": "JBL Live 660NC Wireless NC Headphones Black", "brand": "JBL", "price": 8999, "mrp": 14999, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "50 hours", "ANC": "Adaptive", "Bluetooth": "5.2", "Weight": "265g"}},
    {"title": "Boat Rockerz 450 Wireless On-Ear Headphones Black", "brand": "Boat", "price": 1499, "mrp": 3990, "specs": {"Type": "On-Ear", "Driver": "40mm", "Battery": "15 hours", "ANC": "No", "Bluetooth": "5.0", "Weight": "230g"}},
    {"title": "Boat Rockerz 550 Over-Ear Wireless Headphones Black", "brand": "Boat", "price": 1999, "mrp": 5990, "specs": {"Type": "Over-Ear", "Driver": "50mm", "Battery": "20 hours", "ANC": "No", "Bluetooth": "5.0", "Weight": "280g"}},
    {"title": "Noise Air-cancel+ Wireless ANC Headphones Black", "brand": "Noise", "price": 3999, "mrp": 7999, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "62 hours", "ANC": "Hybrid ANC", "Bluetooth": "5.3", "Weight": "260g"}},
    {"title": "Bose QuietComfort Ultra Headphones Black", "brand": "Bose", "price": 33999, "mrp": 39999, "specs": {"Type": "Over-Ear", "Driver": "35mm", "Battery": "24 hours", "ANC": "CustomTune ANC", "Bluetooth": "5.3", "Weight": "250g"}},
    {"title": "Bose QuietComfort Headphones Black", "brand": "Bose", "price": 24999, "mrp": 29999, "specs": {"Type": "Over-Ear", "Driver": "35mm", "Battery": "24 hours", "ANC": "Adjustable", "Bluetooth": "5.1", "Weight": "296g"}},
    {"title": "Sennheiser HD 450BT Wireless NC Headphones Black", "brand": "Sennheiser", "price": 8990, "mrp": 14990, "specs": {"Type": "Over-Ear", "Driver": "32mm", "Battery": "30 hours", "ANC": "Active", "Bluetooth": "5.0", "Weight": "238g"}},
    {"title": "Sony WH-CH720N Wireless NC Headphones Black", "brand": "Sony", "price": 8990, "mrp": 12990, "specs": {"Type": "Over-Ear", "Driver": "30mm", "Battery": "35 hours", "ANC": "Adaptive", "Bluetooth": "5.0", "Weight": "192g"}},
    {"title": "JBL Tune 510BT Wireless On-Ear Headphones Blue", "brand": "JBL", "price": 2299, "mrp": 3999, "specs": {"Type": "On-Ear", "Driver": "32mm", "Battery": "40 hours", "ANC": "No", "Bluetooth": "5.0", "Weight": "160g"}},
    {"title": "Boat Rockerz 450 Pro Wireless On-Ear Headphones Honeydew", "brand": "Boat", "price": 1799, "mrp": 4990, "specs": {"Type": "On-Ear", "Driver": "40mm", "Battery": "70 hours", "ANC": "No", "Bluetooth": "5.2", "Weight": "240g"}},
    {"title": "Sennheiser HD 560S Open-Back Headphones", "brand": "Sennheiser", "price": 14990, "mrp": 19990, "specs": {"Type": "Over-Ear, Wired, Open-Back", "Driver": "38mm", "Battery": "N/A", "ANC": "No", "Connector": "3.5mm + 6.35mm", "Weight": "240g"}},
    {"title": "Audio-Technica ATH-M50x Professional Studio Headphones", "brand": "Audio-Technica", "price": 12990, "mrp": 17990, "specs": {"Type": "Over-Ear, Wired, Closed-Back", "Driver": "45mm", "Battery": "N/A", "ANC": "No", "Impedance": "38 ohms", "Weight": "285g"}},
    {"title": "JBL Live Pro 2 Over-Ear NC Headphones Black", "brand": "JBL", "price": 7999, "mrp": 11999, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "65 hours", "ANC": "True Adaptive ANC", "Bluetooth": "5.3", "Weight": "256g"}},
    {"title": "Sony WH-1000XM4 Wireless NC Headphones Silver", "brand": "Sony", "price": 19990, "mrp": 29990, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "30 hours", "ANC": "Adaptive", "Bluetooth": "5.0", "Weight": "254g"}},
    {"title": "Boat Nirvanaa 751 ANC Wireless Over-Ear Headphones Black", "brand": "Boat", "price": 3499, "mrp": 7999, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "54 hours", "ANC": "Hybrid ANC", "Bluetooth": "5.2", "Weight": "260g"}},
    {"title": "Noise Air Buds Pro Wireless NC Headphones Black", "brand": "Noise", "price": 2999, "mrp": 5999, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "50 hours", "ANC": "Hybrid ANC", "Bluetooth": "5.3", "Weight": "250g"}},
    {"title": "JBL Tune 760NC Wireless Over-Ear Headphones Black", "brand": "JBL", "price": 5499, "mrp": 8999, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "50 hours (ANC OFF)", "ANC": "Adaptive", "Bluetooth": "5.3", "Weight": "252g"}},
    {"title": "Sony ULT WEAR Wireless NC Headphones Black", "brand": "Sony", "price": 14990, "mrp": 19990, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "50 hours", "ANC": "Adaptive", "Bluetooth": "5.2", "Weight": "261g"}},
    {"title": "Sennheiser Momentum 4 Wireless NC Headphones Black", "brand": "Sennheiser", "price": 24990, "mrp": 34990, "specs": {"Type": "Over-Ear", "Driver": "42mm", "Battery": "60 hours", "ANC": "Adaptive", "Bluetooth": "5.2", "Weight": "293g"}},
    {"title": "Beats Solo 4 Wireless On-Ear Headphones Black", "brand": "Beats", "price": 19999, "mrp": 24999, "specs": {"Type": "On-Ear", "Driver": "Custom", "Battery": "50 hours", "ANC": "No", "Bluetooth": "5.3", "Weight": "217g"}},
    {"title": "Marshall Major IV Wireless On-Ear Headphones Black", "brand": "Marshall", "price": 14999, "mrp": 17999, "specs": {"Type": "On-Ear", "Driver": "Custom 40mm", "Battery": "80+ hours", "ANC": "No", "Bluetooth": "5.0", "Weight": "165g"}},
    {"title": "JBL Quantum 910 Wireless Gaming Headphones", "brand": "JBL", "price": 14999, "mrp": 19999, "specs": {"Type": "Over-Ear, Gaming", "Driver": "50mm", "Battery": "43 hours", "ANC": "ANC + ANC Mic", "Bluetooth": "5.2 / 2.4GHz", "Weight": "320g"}},
    {"title": "Audio-Technica ATH-M20xBT Wireless Headphones Black", "brand": "Audio-Technica", "price": 4999, "mrp": 7990, "specs": {"Type": "Over-Ear", "Driver": "40mm", "Battery": "60 hours", "ANC": "No", "Bluetooth": "5.0", "Weight": "216g"}},
    {"title": "Razer BlackShark V2 Pro 2023 Wireless Gaming Headphones", "brand": "Razer", "price": 16999, "mrp": 19999, "specs": {"Type": "Over-Ear, Gaming", "Driver": "50mm TriForce", "Battery": "70 hours", "ANC": "THX Spatial Audio", "Bluetooth": "5.2 / 2.4GHz", "Weight": "320g"}},
]

# ---------------------------------------------------------------------------
# EARBUDS (30 products)
# ---------------------------------------------------------------------------
EARBUDS = [
    {"title": "Apple AirPods Pro (2nd Gen) USB-C", "brand": "Apple", "price": 22900, "mrp": 24900, "specs": {"Type": "TWS In-Ear", "Driver": "Custom Apple", "Battery": "6 hours + 30h case", "ANC": "Active + Transparency", "Connectivity": "Bluetooth 5.3", "Chip": "Apple H2"}},
    {"title": "Apple AirPods (3rd Gen)", "brand": "Apple", "price": 17900, "mrp": 19900, "specs": {"Type": "TWS In-Ear", "Driver": "Custom Apple", "Battery": "6 hours + 30h case", "ANC": "No", "Connectivity": "Bluetooth 5.0", "Chip": "Apple H1"}},
    {"title": "Samsung Galaxy Buds2 Pro Wi-Fi", "brand": "Samsung", "price": 12999, "mrp": 17999, "specs": {"Type": "TWS In-Ear", "Driver": "10mm + 5.3mm", "Battery": "5 hours + 18h case", "ANC": "Intelligent ANC", "Connectivity": "Bluetooth 5.3", "Codec": "SSC HiFi"}},
    {"title": "Samsung Galaxy Buds FE", "brand": "Samsung", "price": 5999, "mrp": 9999, "specs": {"Type": "TWS In-Ear", "Driver": "1-way 12mm", "Battery": "6 hours + 21h case", "ANC": "ANC", "Connectivity": "Bluetooth 5.2", "IP Rating": "IPX2"}},
    {"title": "Boat Airdopes 141 TWS Earbuds Black", "brand": "Boat", "price": 1299, "mrp": 4490, "specs": {"Type": "TWS In-Ear", "Driver": "8mm", "Battery": "42 hours total", "ANC": "ENx", "Connectivity": "Bluetooth 5.3", "IP Rating": "IPX4"}},
    {"title": "Boat Airdopes 441 TWS Earbuds Black", "brand": "Boat", "price": 1599, "mrp": 5990, "specs": {"Type": "TWS In-Ear", "Driver": "8mm", "Battery": "18 hours total", "ANC": "ENx", "Connectivity": "Bluetooth 5.1", "IP Rating": "IPX7"}},
    {"title": "Boat Airdopes 611 ANC TWS Earbuds Black", "brand": "Boat", "price": 2999, "mrp": 7990, "specs": {"Type": "TWS In-Ear", "Driver": "10mm", "Battery": "31 hours total", "ANC": "Hybrid ANC 32dB", "Connectivity": "Bluetooth 5.3", "IP Rating": "IPX5"}},
    {"title": "Noise Air Buds Pro 2 TWS Earbuds Black", "brand": "Noise", "price": 2499, "mrp": 4999, "specs": {"Type": "TWS In-Ear", "Driver": "10mm", "Battery": "44 hours total", "ANC": "Hybrid ANC 32dB", "Connectivity": "Bluetooth 5.3", "IP Rating": "IPX5"}},
    {"title": "JBL Tune 230NC TWS Earbuds Black", "brand": "JBL", "price": 4999, "mrp": 8999, "specs": {"Type": "TWS In-Ear", "Driver": "10mm", "Battery": "40 hours total", "ANC": "Active ANC", "Connectivity": "Bluetooth 5.2", "IP Rating": "IPX4"}},
    {"title": "JBL Tune 230NC TWS Earbuds White", "brand": "JBL", "price": 4999, "mrp": 8999, "specs": {"Type": "TWS In-Ear", "Driver": "10mm", "Battery": "40 hours total", "ANC": "Active ANC", "Connectivity": "Bluetooth 5.2", "IP Rating": "IPX4"}},
    {"title": "Sony WF-1000XM5 TWS Earbuds Black", "brand": "Sony", "price": 24990, "mrp": 27990, "specs": {"Type": "TWS In-Ear", "Driver": "8.4mm Dynamic Driver X", "Battery": "8 hours + 24h case", "ANC": "Integrated Processor V2", "Connectivity": "Bluetooth 5.3", "Codec": "LDAC, AAC, SBC"}},
    {"title": "Sony WF-1000XM4 TWS Earbuds Black", "brand": "Sony", "price": 17990, "mrp": 23990, "specs": {"Type": "TWS In-Ear", "Driver": "6mm", "Battery": "8 hours + 24h case", "ANC": "Integrated Processor V1", "Connectivity": "Bluetooth 5.2", "Codec": "LDAC, AAC"}},
    {"title": "OnePlus Buds Pro 2 TWS Earbuds Black", "brand": "OnePlus", "price": 8999, "mrp": 12999, "specs": {"Type": "TWS In-Ear", "Driver": "11mm + 6mm", "Battery": "6 hours + 39h case", "ANC": "Smart ANC 48dB", "Connectivity": "Bluetooth 5.3", "Codec": "LDAC, LHDC 4.0"}},
    {"title": "Realme Buds T300 TWS Earbuds Black", "brand": "Realme", "price": 1999, "mrp": 3999, "specs": {"Type": "TWS In-Ear", "Driver": "12.4mm", "Battery": "40 hours total", "ANC": "ANC 30dB", "Connectivity": "Bluetooth 5.3", "IP Rating": "IPX5"}},
    {"title": "Boat Airdopes 131 TWS Earbuds Black", "brand": "Boat", "price": 999, "mrp": 3990, "specs": {"Type": "TWS In-Ear", "Driver": "8mm", "Battery": "60 hours total", "ANC": "No", "Connectivity": "Bluetooth 5.1", "IP Rating": "IPX4"}},
    {"title": "Samsung Galaxy Buds2 Pro Graphite", "brand": "Samsung", "price": 11999, "mrp": 17999, "specs": {"Type": "TWS In-Ear", "Driver": "10mm + 5.3mm", "Battery": "5 hours + 18h case", "ANC": "Intelligent ANC", "Connectivity": "Bluetooth 5.3", "Codec": "SSC HiFi"}},
    {"title": "JBL Live Pro 2 TWS Earbuds Black", "brand": "JBL", "price": 7999, "mrp": 12999, "specs": {"Type": "TWS In-Ear", "Driver": "10mm", "Battery": "40 hours total", "ANC": "True Adaptive ANC", "Connectivity": "Bluetooth 5.3", "IP Rating": "IPX5"}},
    {"title": "Sony LinkBuds S WF-LS900N TWS Earbuds White", "brand": "Sony", "price": 14990, "mrp": 19990, "specs": {"Type": "TWS In-Ear", "Driver": "5mm", "Battery": "6 hours + 20h case", "ANC": "Adaptive Sound", "Connectivity": "Bluetooth 5.2", "Codec": "LDAC, AAC"}},
    {"title": "Noise Air Buds Lite TWS Earbuds Charcoal Black", "brand": "Noise", "price": 1299, "mrp": 3999, "specs": {"Type": "TWS In-Ear", "Driver": "10mm", "Battery": "45 hours total", "ANC": "No", "Connectivity": "Bluetooth 5.3", "IP Rating": "IPX5"}},
    {"title": "Boat Airdopes 411 ANC TWS Earbuds Black", "brand": "Boat", "price": 1999, "mrp": 5990, "specs": {"Type": "TWS In-Ear", "Driver": "10mm", "Battery": "17.5 hours total", "ANC": "ANC 25dB", "Connectivity": "Bluetooth 5.0", "IP Rating": "IPX4"}},
    {"title": "OnePlus Nord Buds 2r TWS Earbuds Triple Black", "brand": "OnePlus", "price": 2299, "mrp": 3999, "specs": {"Type": "TWS In-Ear", "Driver": "12.4mm", "Battery": "39 hours total", "ANC": "No", "Connectivity": "Bluetooth 5.3", "IP Rating": "IP55"}},
    {"title": "Realme Buds Air 5 TWS Earbuds Black", "brand": "Realme", "price": 2499, "mrp": 4999, "specs": {"Type": "TWS In-Ear", "Driver": "12.4mm", "Battery": "38 hours total", "ANC": "ANC 50dB", "Connectivity": "Bluetooth 5.3", "IP Rating": "IPX4"}},
    {"title": "JBL Wave Beam TWS Earbuds Black", "brand": "JBL", "price": 2499, "mrp": 4999, "specs": {"Type": "TWS In-Ear", "Driver": "8mm", "Battery": "32 hours total", "ANC": "No", "Connectivity": "Bluetooth 5.2", "IP Rating": "IP54"}},
    {"title": "Sony WF-C700N TWS Earbuds Black", "brand": "Sony", "price": 7990, "mrp": 9990, "specs": {"Type": "TWS In-Ear", "Driver": "5.8mm", "Battery": "7.5 hours + 15h case", "ANC": "Adaptive", "Connectivity": "Bluetooth 5.2", "IP Rating": "IPX4"}},
    {"title": "Samsung Galaxy Buds FE Graphite", "brand": "Samsung", "price": 5499, "mrp": 9999, "specs": {"Type": "TWS In-Ear", "Driver": "1-way 12mm", "Battery": "6 hours + 21h case", "ANC": "ANC", "Connectivity": "Bluetooth 5.2", "IP Rating": "IPX2"}},
    {"title": "JBL Tune Buds TWS Earbuds Black", "brand": "JBL", "price": 3999, "mrp": 7999, "specs": {"Type": "TWS In-Ear", "Driver": "10mm", "Battery": "48 hours total", "ANC": "True Adaptive ANC", "Connectivity": "Bluetooth 5.3", "IP Rating": "IP54"}},
    {"title": "Nothing Ear (2) TWS Earbuds White", "brand": "Nothing", "price": 7999, "mrp": 9999, "specs": {"Type": "TWS In-Ear", "Driver": "11.6mm", "Battery": "6 hours + 30h case", "ANC": "ANC up to 40dB", "Connectivity": "Bluetooth 5.3", "Codec": "LDAC, AAC, SBC"}},
    {"title": "Boat Airdopes 181 TWS Earbuds Black", "brand": "Boat", "price": 1099, "mrp": 4490, "specs": {"Type": "TWS In-Ear", "Driver": "10mm", "Battery": "50 hours total", "ANC": "ENx", "Connectivity": "Bluetooth 5.3", "IP Rating": "IPX5"}},
    {"title": "Apple AirPods Max Silver", "brand": "Apple", "price": 54900, "mrp": 59900, "specs": {"Type": "Over-Ear, Wireless", "Driver": "40mm Custom", "Battery": "20 hours", "ANC": "Active + Transparency", "Connectivity": "Bluetooth 5.0", "Chip": "Apple H1"}},
]

# ---------------------------------------------------------------------------
# TABLETS (15 products)
# ---------------------------------------------------------------------------
TABLETS = [
    {"title": "Apple iPad (10th Gen) 10.9-inch 64GB Wi-Fi Silver", "brand": "Apple", "price": 34900, "mrp": 44900, "specs": {"Display": '10.9" Liquid Retina', "Processor": "Apple A14 Bionic", "RAM": "4 GB", "Storage": "64 GB", "Battery": "Up to 10 hours", "Camera": "12MP"}},
    {"title": "Apple iPad (10th Gen) 10.9-inch 256GB Wi-Fi Blue", "brand": "Apple", "price": 49900, "mrp": 59900, "specs": {"Display": '10.9" Liquid Retina', "Processor": "Apple A14 Bionic", "RAM": "4 GB", "Storage": "256 GB", "Battery": "Up to 10 hours", "Camera": "12MP"}},
    {"title": "Apple iPad Air M2 11-inch 128GB Wi-Fi Space Gray", "brand": "Apple", "price": 59900, "mrp": 64900, "specs": {"Display": '11" Liquid Retina', "Processor": "Apple M2", "RAM": "8 GB", "Storage": "128 GB", "Battery": "Up to 10 hours", "Camera": "12MP + 12MP UW"}},
    {"title": "Apple iPad Air M2 11-inch 256GB Wi-Fi Starlight", "brand": "Apple", "price": 69900, "mrp": 74900, "specs": {"Display": '11" Liquid Retina', "Processor": "Apple M2", "RAM": "8 GB", "Storage": "256 GB", "Battery": "Up to 10 hours", "Camera": "12MP + 12MP UW"}},
    {"title": "Apple iPad Pro M4 11-inch 256GB Wi-Fi Space Black", "brand": "Apple", "price": 99900, "mrp": 109900, "specs": {"Display": '11" Ultra Retina XDR OLED', "Processor": "Apple M4", "RAM": "8 GB", "Storage": "256 GB", "Battery": "Up to 10 hours", "Camera": "12MP + 10MP UW"}},
    {"title": "Samsung Galaxy Tab S9 11-inch 128GB Wi-Fi Graphite", "brand": "Samsung", "price": 59999, "mrp": 74999, "specs": {"Display": '11" Dynamic AMOLED 2X, 120Hz', "Processor": "Snapdragon 8 Gen 2", "RAM": "8 GB", "Storage": "128 GB", "Battery": "8400 mAh", "S Pen": "Included"}},
    {"title": "Samsung Galaxy Tab S9 FE 10.9-inch 128GB Wi-Fi Gray", "brand": "Samsung", "price": 34999, "mrp": 44999, "specs": {"Display": '10.9" TFT LCD, 90Hz', "Processor": "Exynos 1380", "RAM": "6 GB", "Storage": "128 GB", "Battery": "8000 mAh", "S Pen": "Included"}},
    {"title": "Samsung Galaxy Tab A9 8.7-inch 64GB Wi-Fi Graphite", "brand": "Samsung", "price": 14999, "mrp": 19999, "specs": {"Display": '8.7" TFT LCD', "Processor": "Helio G99", "RAM": "4 GB", "Storage": "64 GB", "Battery": "5100 mAh", "S Pen": "No"}},
    {"title": "Samsung Galaxy Tab S9 Ultra 14.6-inch 256GB Wi-Fi Graphite", "brand": "Samsung", "price": 94999, "mrp": 114999, "specs": {"Display": '14.6" Dynamic AMOLED 2X, 120Hz', "Processor": "Snapdragon 8 Gen 2", "RAM": "12 GB", "Storage": "256 GB", "Battery": "11200 mAh", "S Pen": "Included"}},
    {"title": "Lenovo Tab P12 12.7-inch 128GB Wi-Fi Storm Grey", "brand": "Lenovo", "price": 24999, "mrp": 34999, "specs": {"Display": '12.7" 2.9K IPS, 144Hz', "Processor": "Dimensity 7050", "RAM": "8 GB", "Storage": "128 GB", "Battery": "10200 mAh", "S Pen": "Included"}},
    {"title": "Amazon Fire HD 10 10.1-inch 32GB Wi-Fi Black", "brand": "Amazon", "price": 12999, "mrp": 17999, "specs": {"Display": '10.1" 1080p IPS', "Processor": "MediaTek MT8186A", "RAM": "3 GB", "Storage": "32 GB", "Battery": "Up to 13 hours", "Camera": "5MP + 2MP"}},
    {"title": "Lenovo Tab M10 5G 10.6-inch 128GB Wi-Fi Storm Grey", "brand": "Lenovo", "price": 19999, "mrp": 27999, "specs": {"Display": '10.6" 2K IPS, 90Hz', "Processor": "Snapdragon 695", "RAM": "6 GB", "Storage": "128 GB", "Battery": "7700 mAh", "S Pen": "No"}},
    {"title": "Samsung Galaxy Tab A9+ 11-inch 64GB Wi-Fi Graphite", "brand": "Samsung", "price": 20999, "mrp": 26999, "specs": {"Display": '11" TFT LCD, 90Hz', "Processor": "Snapdragon 695", "RAM": "4 GB", "Storage": "64 GB", "Battery": "7040 mAh", "S Pen": "No"}},
    {"title": "Apple iPad mini (6th Gen) 8.3-inch 64GB Wi-Fi Space Gray", "brand": "Apple", "price": 44900, "mrp": 49900, "specs": {"Display": '8.3" Liquid Retina', "Processor": "Apple A15 Bionic", "RAM": "4 GB", "Storage": "64 GB", "Battery": "Up to 10 hours", "Camera": "12MP"}},
    {"title": "Apple iPad Pro M4 13-inch 256GB Wi-Fi Space Black", "brand": "Apple", "price": 129900, "mrp": 139900, "specs": {"Display": '13" Ultra Retina XDR OLED', "Processor": "Apple M4", "RAM": "16 GB", "Storage": "256 GB", "Battery": "Up to 10 hours", "Camera": "12MP + 10MP UW"}},
]

# ---------------------------------------------------------------------------
# TVs (20 products)
# ---------------------------------------------------------------------------
TVS = [
    {"title": "Samsung 55-inch Crystal 4K UHD Smart TV CU7700", "brand": "Samsung", "price": 42990, "mrp": 59990, "specs": {"Display": '55" Crystal UHD', "Resolution": "4K (3840x2160)", "HDR": "HDR10+", "Audio": "20W", "Smart TV": "Tizen OS", "HDMI": "3x HDMI"}},
    {"title": "Samsung 65-inch Crystal 4K UHD Smart TV CU7700", "brand": "Samsung", "price": 59990, "mrp": 79990, "specs": {"Display": '65" Crystal UHD', "Resolution": "4K (3840x2160)", "HDR": "HDR10+", "Audio": "20W", "Smart TV": "Tizen OS", "HDMI": "3x HDMI"}},
    {"title": "Samsung 55-inch QLED 4K Smart TV Q60C", "brand": "Samsung", "price": 64990, "mrp": 84990, "specs": {"Display": '55" QLED', "Resolution": "4K (3840x2160)", "HDR": "Quantum HDR", "Audio": "20W OTS", "Smart TV": "Tizen OS", "Refresh Rate": "120Hz"}},
    {"title": "Samsung 65-inch QLED 4K Smart TV Q60C", "brand": "Samsung", "price": 89990, "mrp": 114990, "specs": {"Display": '65" QLED', "Resolution": "4K (3840x2160)", "HDR": "Quantum HDR", "Audio": "20W OTS", "Smart TV": "Tizen OS", "Refresh Rate": "120Hz"}},
    {"title": "Samsung 55-inch OLED 4K Smart TV S90C", "brand": "Samsung", "price": 109990, "mrp": 149990, "specs": {"Display": '55" OLED', "Resolution": "4K (3840x2160)", "HDR": "HDR10+ Adaptive", "Audio": "60W OTS+", "Smart TV": "Tizen OS", "Refresh Rate": "120Hz"}},
    {"title": "Samsung 65-inch Neo QLED 4K Smart TV QN85C", "brand": "Samsung", "price": 129990, "mrp": 174990, "specs": {"Display": '65" Neo QLED', "Resolution": "4K (3840x2160)", "HDR": "Neo Quantum HDR+", "Audio": "60W OTS+", "Smart TV": "Tizen OS", "Refresh Rate": "120Hz"}},
    {"title": "LG 55-inch OLED evo 4K Smart TV OLED55C4PSA", "brand": "LG", "price": 109990, "mrp": 199990, "specs": {"Display": '55" OLED evo', "Resolution": "4K (3840x2160)", "HDR": "Dolby Vision, HDR10", "Audio": "40W Dolby Atmos", "Smart TV": "webOS 24", "Refresh Rate": "120Hz"}},
    {"title": "LG 65-inch OLED evo 4K Smart TV OLED65C4PSA", "brand": "LG", "price": 174990, "mrp": 299990, "specs": {"Display": '65" OLED evo', "Resolution": "4K (3840x2160)", "HDR": "Dolby Vision, HDR10", "Audio": "40W Dolby Atmos", "Smart TV": "webOS 24", "Refresh Rate": "120Hz"}},
    {"title": "LG 55-inch NanoCell 4K Smart TV 55NANO77TQA", "brand": "LG", "price": 54990, "mrp": 74990, "specs": {"Display": '55" NanoCell', "Resolution": "4K (3840x2160)", "HDR": "HDR10 Pro, HLG", "Audio": "20W", "Smart TV": "webOS 24", "Refresh Rate": "120Hz"}},
    {"title": "Sony 55-inch BRAVIA XR 4K OLED Smart TV XR55A80L", "brand": "Sony", "price": 129990, "mrp": 179990, "specs": {"Display": '55" OLED', "Resolution": "4K (3840x2160)", "HDR": "Dolby Vision, XR HDR Remaster", "Audio": "30W + 10W Acoustic Surface Audio", "Smart TV": "Google TV", "Refresh Rate": "120Hz"}},
    {"title": "Sony 65-inch BRAVIA XR 4K Mini LED Smart TV XR65X95L", "brand": "Sony", "price": 179990, "mrp": 249990, "specs": {"Display": '65" Mini LED', "Resolution": "4K (3840x2160)", "HDR": "XR HDR Remaster", "Audio": "Acoustic Multi-Audio", "Smart TV": "Google TV", "Refresh Rate": "120Hz"}},
    {"title": "TCL 55-inch QLED 4K Smart TV 55C645", "brand": "TCL", "price": 42990, "mrp": 64990, "specs": {"Display": '55" QLED', "Resolution": "4K (3840x2160)", "HDR": "Dolby Vision, HDR10+", "Audio": "30W Dolby Atmos", "Smart TV": "Google TV", "Refresh Rate": "120Hz"}},
    {"title": "TCL 65-inch QLED 4K Smart TV 65C645", "brand": "TCL", "price": 59990, "mrp": 84990, "specs": {"Display": '65" QLED', "Resolution": "4K (3840x2160)", "HDR": "Dolby Vision, HDR10+", "Audio": "30W Dolby Atmos", "Smart TV": "Google TV", "Refresh Rate": "120Hz"}},
    {"title": "Hisense 55-inch ULED 4K Smart TV 55U7K", "brand": "Hisense", "price": 54990, "mrp": 74990, "specs": {"Display": '55" ULED', "Resolution": "4K (3840x2160)", "HDR": "Dolby Vision, HDR10+ Adaptive", "Audio": "40W Dolby Atmos", "Smart TV": "Vidaa U7", "Refresh Rate": "144Hz"}},
    {"title": "Hisense 65-inch ULED 4K Smart TV 65U7K", "brand": "Hisense", "price": 74990, "mrp": 99990, "specs": {"Display": '65" ULED', "Resolution": "4K (3840x2160)", "HDR": "Dolby Vision, HDR10+ Adaptive", "Audio": "40W Dolby Atmos", "Smart TV": "Vidaa U7", "Refresh Rate": "144Hz"}},
    {"title": "Mi 55-inch QLED 4K Smart TV 55Xiaomi A Pro", "brand": "Mi", "price": 39999, "mrp": 54999, "specs": {"Display": '55" QLED', "Resolution": "4K (3840x2160)", "HDR": "Dolby Vision, HDR10+", "Audio": "30W Dolby Atmos", "Smart TV": "Google TV", "Refresh Rate": "60Hz"}},
    {"title": "Mi 65-inch QLED 4K Smart TV 65Xiaomi A Pro", "brand": "Mi", "price": 54999, "mrp": 74999, "specs": {"Display": '65" QLED', "Resolution": "4K (3840x2160)", "HDR": "Dolby Vision, HDR10+", "Audio": "30W Dolby Atmos", "Smart TV": "Google TV", "Refresh Rate": "60Hz"}},
    {"title": "Samsung 55-inch OLED 4K Smart TV S95C", "brand": "Samsung", "price": 149990, "mrp": 209990, "specs": {"Display": '55" QD-OLED', "Resolution": "4K (3840x2160)", "HDR": "HDR10+ Adaptive", "Audio": "70W OTS Pro", "Smart TV": "Tizen OS", "Refresh Rate": "120Hz"}},
    {"title": "Sony 55-inch BRAVIA XR 4K OLED Smart TV XR55A95L QD-OLED", "brand": "Sony", "price": 199990, "mrp": 349990, "specs": {"Display": '55" QD-OLED', "Resolution": "4K (3840x2160)", "HDR": "XR OLED Contrast Pro", "Audio": "Acoustic Surface Audio+", "Smart TV": "Google TV", "Refresh Rate": "120Hz"}},
    {"title": "LG 65-inch NanoCell 4K Smart TV 65NANO77TQA", "brand": "LG", "price": 74990, "mrp": 104990, "specs": {"Display": '65" NanoCell', "Resolution": "4K (3840x2160)", "HDR": "HDR10 Pro, HLG", "Audio": "20W", "Smart TV": "webOS 24", "Refresh Rate": "120Hz"}},
]

# ---------------------------------------------------------------------------
# FOOTWEAR (25 products)
# ---------------------------------------------------------------------------
FOOTWEAR = [
    {"title": "Nike Air Max 270 Men's Running Shoes Black/White", "brand": "Nike", "price": 12995, "mrp": 16995, "specs": {"Type": "Running Shoes", "Upper": "Mesh + Synthetic", "Sole": "Rubber", "Cushioning": "Air Max 270 Unit", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Nike Pegasus 41 Men's Running Shoes Black/White", "brand": "Nike", "price": 11895, "mrp": 14995, "specs": {"Type": "Running Shoes", "Upper": "Engineered Mesh", "Sole": "Rubber", "Cushioning": "React Foam + Air Zoom", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Nike Jordan 1 Mid SE Men's Shoes White/Black", "brand": "Nike", "price": 13995, "mrp": 16995, "specs": {"Type": "Casual / Lifestyle", "Upper": "Leather + Synthetic", "Sole": "Rubber", "Cushioning": "Air-Sole", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Nike Air Max 90 Men's Shoes White/Black/Infrared", "brand": "Nike", "price": 11895, "mrp": 13995, "specs": {"Type": "Casual / Lifestyle", "Upper": "Leather + Mesh", "Sole": "Rubber", "Cushioning": "Max Air Unit", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Nike Dunk Low Retro Men's Shoes White/Black", "brand": "Nike", "price": 9695, "mrp": 11895, "specs": {"Type": "Casual / Lifestyle", "Upper": "Leather", "Sole": "Rubber", "Cushioning": "Foam", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Adidas Ultraboost Light Men's Running Shoes Core Black", "brand": "Adidas", "price": 16999, "mrp": 21999, "specs": {"Type": "Running Shoes", "Upper": "Primeknit+", "Sole": "Continental Rubber", "Cushioning": "BOOST", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Adidas Stan Smith Men's Shoes White/Green", "brand": "Adidas", "price": 8999, "mrp": 10999, "specs": {"Type": "Casual / Lifestyle", "Upper": "Leather", "Sole": "Rubber", "Cushioning": "OrthoLite", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Adidas Gazelle Men's Shoes Navy", "brand": "Adidas", "price": 8999, "mrp": 10999, "specs": {"Type": "Casual / Lifestyle", "Upper": "Suede", "Sole": "Rubber", "Cushioning": "Foam", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Adidas Samba OG Men's Shoes White/Black", "brand": "Adidas", "price": 9999, "mrp": 12999, "specs": {"Type": "Casual / Lifestyle", "Upper": "Leather + Suede", "Sole": "Gum Rubber", "Cushioning": "Foam", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Puma RS-X Men's Sneakers Black/White", "brand": "Puma", "price": 8999, "mrp": 12999, "specs": {"Type": "Casual / Lifestyle", "Upper": "Mesh + Synthetic", "Sole": "Rubber", "Cushioning": "RS Foam + Running System", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Puma Suede Classic XXI Men's Sneakers Black", "brand": "Puma", "price": 7999, "mrp": 9999, "specs": {"Type": "Casual / Lifestyle", "Upper": "Suede", "Sole": "Rubber", "Cushioning": "SoftFoam+", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Puma Future Rider Men's Sneakers Peacoat/Whisper White", "brand": "Puma", "price": 7499, "mrp": 10999, "specs": {"Type": "Casual / Lifestyle", "Upper": "Mesh + Nylon", "Sole": "Rubber", "Cushioning": "Federbein", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Reebok Classic Leather Men's Shoes White", "brand": "Reebok", "price": 7999, "mrp": 10999, "specs": {"Type": "Casual / Lifestyle", "Upper": "Leather", "Sole": "Rubber", "Cushioning": "EVA Midsole", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Reebok Nano X3 Men's Training Shoes Black", "brand": "Reebok", "price": 12999, "mrp": 16999, "specs": {"Type": "Training", "Upper": "Flexweave", "Sole": "Rubber", "Cushioning": "Floatride Energy Foam", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "New Balance 550 Men's Shoes White/Grey", "brand": "New Balance", "price": 10999, "mrp": 14999, "specs": {"Type": "Casual / Lifestyle", "Upper": "Leather + Mesh", "Sole": "Rubber", "Cushioning": "EVA", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "New Balance 990v6 Men's Running Shoes Grey", "brand": "New Balance", "price": 15999, "mrp": 19999, "specs": {"Type": "Running Shoes", "Upper": "Suede + Mesh", "Sole": "Rubber", "Cushioning": "FuelCell + ENCAP", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Nike Air Force 1 '07 Men's Shoes White", "brand": "Nike", "price": 9695, "mrp": 11895, "specs": {"Type": "Casual / Lifestyle", "Upper": "Leather", "Sole": "Rubber", "Cushioning": "Air-Sole", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Adidas NMD_R1 Men's Shoes Core Black", "brand": "Adidas", "price": 13999, "mrp": 16999, "specs": {"Type": "Casual / Lifestyle", "Upper": "Primeknit", "Sole": "Rubber", "Cushioning": "BOOST", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Puma Velocity Nitro 2 Men's Running Shoes Black", "brand": "Puma", "price": 9999, "mrp": 12999, "specs": {"Type": "Running Shoes", "Upper": "Mesh", "Sole": "PUMAGRIP Rubber", "Cushioning": "NITRO Foam", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Reebok Club C 85 Men's Shoes White", "brand": "Reebok", "price": 6999, "mrp": 9999, "specs": {"Type": "Casual / Lifestyle", "Upper": "Leather", "Sole": "Rubber", "Cushioning": "EVA", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "New Balance Fresh Foam X 1080v13 Men's Running Shoes Black", "brand": "New Balance", "price": 14999, "mrp": 17999, "specs": {"Type": "Running Shoes", "Upper": "Hypoknit", "Sole": "Rubber", "Cushioning": "Fresh Foam X", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Nike Revolution 7 Men's Running Shoes Black", "brand": "Nike", "price": 3995, "mrp": 4995, "specs": {"Type": "Running Shoes", "Upper": "Mesh", "Sole": "Rubber", "Cushioning": "Foam", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Adidas Grand Court Base Men's Shoes White", "brand": "Adidas", "price": 5999, "mrp": 7999, "specs": {"Type": "Casual / Lifestyle", "Upper": "Leather", "Sole": "Rubber", "Cushioning": "Cloudfoam", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Puma Softride Enzo Evo Men's Running Shoes Black", "brand": "Puma", "price": 6499, "mrp": 8999, "specs": {"Type": "Running Shoes", "Upper": "Mesh", "Sole": "Rubber", "Cushioning": "Softride", "Closure": "Lace-Up", "Gender": "Men"}},
    {"title": "Nike React Infinity Run Flyknit 3 Men's Running Shoes Black", "brand": "Nike", "price": 14995, "mrp": 17995, "specs": {"Type": "Running Shoes", "Upper": "Flyknit", "Sole": "Rubber", "Cushioning": "React Foam", "Closure": "Lace-Up", "Gender": "Men"}},
]

# ---------------------------------------------------------------------------
# WATCHES (15 products)
# ---------------------------------------------------------------------------
WATCHES = [
    {"title": "Apple Watch SE (2nd Gen) 40mm GPS Midnight", "brand": "Apple", "price": 29900, "mrp": 32900, "specs": {"Display": '1.57" OLED LTPO', "Processor": "Apple S8 SiP", "Battery": "Up to 18 hours", "Water Resistance": "WR50", "Sensors": "Heart Rate, Gyroscope, Accelerometer", "Connectivity": "GPS, Bluetooth, Wi-Fi"}},
    {"title": "Apple Watch SE (2nd Gen) 44mm GPS Starlight", "brand": "Apple", "price": 32900, "mrp": 35900, "specs": {"Display": '1.78" OLED LTPO', "Processor": "Apple S8 SiP", "Battery": "Up to 18 hours", "Water Resistance": "WR50", "Sensors": "Heart Rate, Gyroscope, Accelerometer", "Connectivity": "GPS, Bluetooth, Wi-Fi"}},
    {"title": "Apple Watch Series 9 41mm GPS Midnight", "brand": "Apple", "price": 41900, "mrp": 44900, "specs": {"Display": '1.7" OLED LTPO 2000 nits', "Processor": "Apple S9 SiP", "Battery": "Up to 18 hours", "Water Resistance": "WR50", "Sensors": "Heart Rate, SpO2, Temperature", "Connectivity": "GPS, Bluetooth, Wi-Fi"}},
    {"title": "Apple Watch Series 9 45mm GPS+Cellular Midnight", "brand": "Apple", "price": 49900, "mrp": 54900, "specs": {"Display": '1.9" OLED LTPO 2000 nits', "Processor": "Apple S9 SiP", "Battery": "Up to 18 hours", "Water Resistance": "WR50", "Sensors": "Heart Rate, SpO2, Temperature", "Connectivity": "GPS, LTE, Bluetooth, Wi-Fi"}},
    {"title": "Apple Watch Ultra 2 GPS+Cellular 49mm Titanium", "brand": "Apple", "price": 79900, "mrp": 89900, "specs": {"Display": '1.93" OLED LTPO 3000 nits', "Processor": "Apple S9 SiP", "Battery": "Up to 36 hours", "Water Resistance": "WR100", "Sensors": "Heart Rate, SpO2, Depth, Temperature", "Connectivity": "GPS, LTE, Bluetooth, Wi-Fi"}},
    {"title": "Samsung Galaxy Watch 6 Classic 47mm Bluetooth Black", "brand": "Samsung", "price": 29999, "mrp": 37999, "specs": {"Display": '1.47" Super AMOLED', "Processor": "Exynos W930", "Battery": "425 mAh", "Water Resistance": "5ATM + IP68", "Sensors": "Heart Rate, BIA, SpO2", "Connectivity": "Bluetooth, Wi-Fi, NFC"}},
    {"title": "Samsung Galaxy Watch 6 44mm Bluetooth Graphite", "brand": "Samsung", "price": 24999, "mrp": 30999, "specs": {"Display": '1.47" Super AMOLED', "Processor": "Exynos W930", "Battery": "425 mAh", "Water Resistance": "5ATM + IP68", "Sensors": "Heart Rate, BIA, SpO2", "Connectivity": "Bluetooth, Wi-Fi, NFC"}},
    {"title": "Fire-Boltt Phoenix Ultra Smartwatch Black", "brand": "Fire-Boltt", "price": 2499, "mrp": 8999, "specs": {"Display": '1.43" AMOLED', "Battery": "Up to 7 days", "Water Resistance": "IP67", "Sensors": "Heart Rate, SpO2", "Connectivity": "Bluetooth 5.1", "GPS": "No"}},
    {"title": "Fire-Boltt Oracle Smartwatch Black", "brand": "Fire-Boltt", "price": 2999, "mrp": 11999, "specs": {"Display": '1.43" AMOLED', "Battery": "Up to 7 days", "Water Resistance": "IP67", "Sensors": "Heart Rate, SpO2", "Connectivity": "Bluetooth 5.1", "GPS": "No"}},
    {"title": "Noise ColorFit Pro 5 Max Smartwatch Jet Black", "brand": "Noise", "price": 3999, "mrp": 8999, "specs": {"Display": '1.96" AMOLED', "Battery": "Up to 10 days", "Water Resistance": "IP67", "Sensors": "Heart Rate, SpO2, Stress", "Connectivity": "Bluetooth 5.3", "GPS": "No"}},
    {"title": "Fastrack Reflex Smartwatch Black", "brand": "Fastrack", "price": 1999, "mrp": 4995, "specs": {"Display": '1.4" AMOLED', "Battery": "Up to 7 days", "Water Resistance": "IP68", "Sensors": "Heart Rate, SpO2", "Connectivity": "Bluetooth 5.1", "GPS": "No"}},
    {"title": "Noise ColorFit Pro 5 Smartwatch Rose Gold", "brand": "Noise", "price": 3499, "mrp": 7999, "specs": {"Display": '1.85" AMOLED', "Battery": "Up to 7 days", "Water Resistance": "IP67", "Sensors": "Heart Rate, SpO2", "Connectivity": "Bluetooth 5.3", "GPS": "No"}},
    {"title": "Fire-Boltt Invincible Plus Smartwatch Black", "brand": "Fire-Boltt", "price": 3499, "mrp": 12999, "specs": {"Display": '1.43" AMOLED', "Battery": "Up to 10 days", "Water Resistance": "IP67", "Sensors": "Heart Rate, SpO2", "Connectivity": "Bluetooth 5.1", "GPS": "No"}},
    {"title": "Apple Watch SE (2nd Gen) 40mm GPS+Cellular Midnight", "brand": "Apple", "price": 37900, "mrp": 41900, "specs": {"Display": '1.57" OLED LTPO', "Processor": "Apple S8 SiP", "Battery": "Up to 18 hours", "Water Resistance": "WR50", "Sensors": "Heart Rate, Gyroscope", "Connectivity": "GPS, LTE, Bluetooth, Wi-Fi"}},
    {"title": "Samsung Galaxy Watch 6 40mm Bluetooth Gold", "brand": "Samsung", "price": 22999, "mrp": 28999, "specs": {"Display": '1.31" Super AMOLED', "Processor": "Exynos W930", "Battery": "300 mAh", "Water Resistance": "5ATM + IP68", "Sensors": "Heart Rate, BIA, SpO2", "Connectivity": "Bluetooth, Wi-Fi, NFC"}},
]

# ---------------------------------------------------------------------------
# KITCHEN APPLIANCES (15 products)
# ---------------------------------------------------------------------------
KITCHEN = [
    {"title": "Prestige Iris 750W Mixer Grinder with 3 Jars Black", "brand": "Prestige", "price": 2499, "mrp": 5495, "specs": {"Power": "750W", "Jars": "3 SS Jars", "Speed": "3 Speed + Pulse", "Motor": "Copper Winding", "Warranty": "2 Years", "Blade": "Stainless Steel"}},
    {"title": "Prestige Iris Plus 750W Mixer Grinder with 3 Jars White", "brand": "Prestige", "price": 2799, "mrp": 5995, "specs": {"Power": "750W", "Jars": "3 SS Jars", "Speed": "3 Speed + Pulse", "Motor": "Copper Winding", "Warranty": "2 Years", "Blade": "Stainless Steel"}},
    {"title": "Philips HL7756/00 750W Mixer Grinder with 3 Jars Black", "brand": "Philips", "price": 3495, "mrp": 5495, "specs": {"Power": "750W", "Jars": "3 SS Jars", "Speed": "3 Speed + Pulse", "Motor": "Copper Winding", "Warranty": "2 Years", "Blade": "Superior Stainless Steel"}},
    {"title": "Philips HR7605 650W Mixer Grinder with 3 Jars White", "brand": "Philips", "price": 2995, "mrp": 4495, "specs": {"Power": "650W", "Jars": "3 SS Jars", "Speed": "3 Speed + Pulse", "Motor": "Copper Winding", "Warranty": "2 Years", "Blade": "Stainless Steel"}},
    {"title": "Bajaj Rex Mixer Grinder 500W with 3 Jars White", "brand": "Bajaj", "price": 2299, "mrp": 4299, "specs": {"Power": "500W", "Jars": "3 SS Jars", "Speed": "3 Speed", "Motor": "Copper Winding", "Warranty": "2 Years", "Blade": "Stainless Steel"}},
    {"title": "Bajaj GX-1 500W Mixer Grinder with 3 Jars White", "brand": "Bajaj", "price": 2599, "mrp": 4699, "specs": {"Power": "500W", "Jars": "3 SS Jars", "Speed": "3 Speed + Pulse", "Motor": "Copper Winding", "Warranty": "2 Years", "Blade": "Stainless Steel"}},
    {"title": "Butterfly Jet Elite 750W Mixer Grinder with 3 Jars White", "brand": "Butterfly", "price": 2799, "mrp": 5499, "specs": {"Power": "750W", "Jars": "3 SS Jars", "Speed": "3 Speed + Pulse", "Motor": "Copper Winding", "Warranty": "2 Years", "Blade": "Superior SS"}},
    {"title": "Morphy Richards Icon Superb 750W Mixer Grinder with 3 Jars Black", "brand": "Morphy Richards", "price": 4499, "mrp": 7999, "specs": {"Power": "750W", "Jars": "3 SS Jars", "Speed": "3 Speed + Pulse", "Motor": "Copper Winding", "Warranty": "2 Years", "Blade": "Stainless Steel"}},
    {"title": "Prestige PKOSS 1.5L Electric Kettle Stainless Steel", "brand": "Prestige", "price": 899, "mrp": 1695, "specs": {"Capacity": "1.5L", "Power": "1500W", "Material": "Stainless Steel", "Auto Cut-Off": "Yes", "Warranty": "1 Year", "Body": "Cool Touch"}},
    {"title": "Philips HD9200/00 4.1L Air Fryer Black", "brand": "Philips", "price": 7995, "mrp": 12995, "specs": {"Capacity": "4.1L", "Power": "1400W", "Technology": "Rapid Air", "Temperature": "80-200°C", "Warranty": "2 Years", "Dishwasher Safe": "Yes"}},
    {"title": "Prestige Induction Cooktop PKOSS 1800W Black", "brand": "Prestige", "price": 1999, "mrp": 3495, "specs": {"Power": "1800W", "Burner": "Indian Menu", "Pan Sensor": "Yes", "Auto Cut-Off": "Yes", "Warranty": "1 Year", "Preset Menus": "7"}},
    {"title": "Bajaj Majesty SWX 3 Sandwich Toaster 800W", "brand": "Bajaj", "price": 1199, "mrp": 2295, "specs": {"Power": "800W", "Capacity": "2 Slices", "Non-Stick": "Yes", "Auto Cut-Off": "Yes", "Warranty": "2 Years", "Cool Touch Handle": "Yes"}},
    {"title": "Butterfly Rapid 4 Jar Mixer Grinder 750W Red", "brand": "Butterfly", "price": 3299, "mrp": 6199, "specs": {"Power": "750W", "Jars": "4 SS Jars", "Speed": "3 Speed + Pulse", "Motor": "Copper Winding", "Warranty": "2 Years", "Blade": "Superior SS"}},
    {"title": "Philips HR7777/00 1000W Food Processor Black", "brand": "Philips", "price": 16995, "mrp": 22995, "specs": {"Power": "1000W", "Capacity": "3.1L", "Functions": "Chop, Blend, Knead, Slice", "Speed": "Variable Speed + Pulse", "Warranty": "2 Years", "Bowl": "Stainless Steel + Plastic"}},
    {"title": "Morphy Richards OTG 52L OTG102 Black", "brand": "Morphy Richards", "price": 13999, "mrp": 18999, "specs": {"Capacity": "52L", "Power": "2000W", "Temperature": "100-250°C", "Timer": "60 min", "Warranty": "2 Years", "Functions": "Bake, Toast, Grill"}},
]

# ---------------------------------------------------------------------------
# CAMERAS (10 products)
# ---------------------------------------------------------------------------
CAMERAS = [
    {"title": "Canon EOS R50 Mirrorless Camera with 18-45mm Lens Black", "brand": "Canon", "price": 74995, "mrp": 89995, "specs": {"Sensor": "24.2 MP APS-C CMOS", "Processor": "DIGIC X", "ISO": "100-32000", "AF Points": "651", "Video": "4K 30p, 1080p 60fps", "Display": "3.0\" Vari-angle LCD", "Weight": "375g (body only)"}},
    {"title": "Canon EOS R100 Mirrorless Camera with 18-45mm Lens Black", "brand": "Canon", "price": 44995, "mrp": 54995, "specs": {"Sensor": "24.1 MP APS-C CMOS", "Processor": "DIGIC 8", "ISO": "100-12800", "AF Points": "3975", "Video": "4K 24p, 1080p 60fps", "Display": "3.0\" Fixed LCD", "Weight": "356g (body only)"}},
    {"title": "Nikon Z30 Mirrorless Camera with 16-50mm Lens Black", "brand": "Nikon", "price": 64995, "mrp": 79995, "specs": {"Sensor": "20.9 MP APS-C CMOS", "Processor": "EXPEED 6", "ISO": "100-51200", "AF Points": "209", "Video": "4K 30p, 1080p 120fps", "Display": "3.0\" Vari-angle LCD", "Weight": "350g (body only)"}},
    {"title": "Nikon Z50 Mirrorless Camera with 16-50mm Lens Black", "brand": "Nikon", "price": 74995, "mrp": 89995, "specs": {"Sensor": "20.9 MP APS-C CMOS", "Processor": "EXPEED 6", "ISO": "100-51200", "AF Points": "209", "Video": "4K 30p", "Display": "3.2\" Tilting LCD", "Weight": "397g (body only)"}},
    {"title": "Sony ZV-E10 II Mirrorless Camera with 16-50mm Lens Black", "brand": "Sony", "price": 79990, "mrp": 89990, "specs": {"Sensor": "26.1 MP APS-C CMOS", "Processor": "BIONZ XR", "ISO": "100-32000", "AF Points": "759", "Video": "4K 60p, 1080p 120fps", "Display": "3.0\" Vari-angle LCD", "Weight": "292g (body only)"}},
    {"title": "Sony Alpha A6400 Mirrorless Camera with 16-50mm Lens Black", "brand": "Sony", "price": 69990, "mrp": 84990, "specs": {"Sensor": "24.2 MP APS-C CMOS", "Processor": "BIONZ X", "ISO": "100-32000", "AF Points": "425", "Video": "4K 30p, 1080p 120fps", "Display": "3.0\" Tilting LCD", "Weight": "360g (body only)"}},
    {"title": "GoPro Hero 13 Black Action Camera", "brand": "GoPro", "price": 41500, "mrp": 51500, "specs": {"Sensor": "1/1.9\" CMOS", "Video": "5.3K 60fps, 4K 120fps", "Stabilization": "HyperSmooth 6.0", "Waterproof": "10m (33ft)", "Battery": "1900mAh", "Display": "2.27\" Rear + 1.4\" Front"}},
    {"title": "GoPro Hero 13 Black Creator Edition", "brand": "GoPro", "price": 61500, "mrp": 71500, "specs": {"Sensor": "1/1.9\" CMOS", "Video": "5.3K 60fps, 4K 120fps", "Stabilization": "HyperSmooth 6.0", "Waterproof": "10m (33ft)", "Battery": "1900mAh", "Includes": "Media Mod, Light Mod, Enduro Battery"}},
    {"title": "Canon EOS R10 Mirrorless Camera with 18-150mm Lens Black", "brand": "Canon", "price": 109995, "mrp": 129995, "specs": {"Sensor": "24.2 MP APS-C CMOS", "Processor": "DIGIC X", "ISO": "100-32000", "AF Points": "651", "Video": "4K 60p, 1080p 120fps", "Display": "3.0\" Vari-angle LCD", "Weight": "429g (body only)"}},
    {"title": "Sony ZV-E10 Mirrorless Camera with 16-50mm Lens Black", "brand": "Sony", "price": 54990, "mrp": 64990, "specs": {"Sensor": "24.2 MP APS-C CMOS", "Processor": "BIONZ X", "ISO": "100-32000", "AF Points": "425", "Video": "4K 30p, 1080p 120fps", "Display": "3.0\" Vari-angle LCD", "Weight": "343g (body only)"}},
]

# ---------------------------------------------------------------------------
# FASHION (15 products)
# ---------------------------------------------------------------------------
FASHION = [
    {"title": "Levi's 511 Slim Fit Mid Rise Men's Jeans Dark Indigo", "brand": "Levi's", "price": 3299, "mrp": 4999, "specs": {"Fit": "Slim Fit", "Rise": "Mid Rise", "Material": "98% Cotton, 2% Elastane", "Closure": "Button Fly", "Care": "Machine Wash", "Gender": "Men"}},
    {"title": "Levi's 511 Slim Fit Mid Rise Men's Jeans Classic Blue", "brand": "Levi's", "price": 2999, "mrp": 4999, "specs": {"Fit": "Slim Fit", "Rise": "Mid Rise", "Material": "99% Cotton, 1% Elastane", "Closure": "Button Fly", "Care": "Machine Wash", "Gender": "Men"}},
    {"title": "Levi's 512 Slim Taper Fit Men's Jeans Black", "brand": "Levi's", "price": 3499, "mrp": 5499, "specs": {"Fit": "Slim Taper", "Rise": "Mid Rise", "Material": "98% Cotton, 2% Elastane", "Closure": "Button Fly", "Care": "Machine Wash", "Gender": "Men"}},
    {"title": "Allen Solly Men Slim Fit Formal Shirt Blue", "brand": "Allen Solly", "price": 1499, "mrp": 2799, "specs": {"Fit": "Slim Fit", "Material": "100% Cotton", "Sleeve": "Full Sleeve", "Collar": "Spread Collar", "Pattern": "Solid", "Gender": "Men"}},
    {"title": "Allen Solly Men Regular Fit Formal Shirt White", "brand": "Allen Solly", "price": 1299, "mrp": 2499, "specs": {"Fit": "Regular Fit", "Material": "100% Cotton", "Sleeve": "Full Sleeve", "Collar": "Semi Spread Collar", "Pattern": "Solid", "Gender": "Men"}},
    {"title": "Allen Solly Men Slim Fit Casual Shirt Navy Blue", "brand": "Allen Solly", "price": 1599, "mrp": 2999, "specs": {"Fit": "Slim Fit", "Material": "100% Cotton", "Sleeve": "Full Sleeve", "Collar": "Spread Collar", "Pattern": "Checks", "Gender": "Men"}},
    {"title": "Peter England Men Regular Fit Polo Shirt Black", "brand": "Peter England", "price": 899, "mrp": 1699, "specs": {"Fit": "Regular Fit", "Material": "100% Cotton", "Sleeve": "Half Sleeve", "Collar": "Polo Collar", "Pattern": "Solid", "Gender": "Men"}},
    {"title": "Peter England Men Regular Fit Polo Shirt Navy Blue", "brand": "Peter England", "price": 899, "mrp": 1699, "specs": {"Fit": "Regular Fit", "Material": "100% Cotton", "Sleeve": "Half Sleeve", "Collar": "Polo Collar", "Pattern": "Solid", "Gender": "Men"}},
    {"title": "Peter England Men Slim Fit Formal Shirt Light Blue", "brand": "Peter England", "price": 1199, "mrp": 2299, "specs": {"Fit": "Slim Fit", "Material": "60% Cotton, 40% Polyester", "Sleeve": "Full Sleeve", "Collar": "Spread Collar", "Pattern": "Solid", "Gender": "Men"}},
    {"title": "Wildcraft 35L Hiking Backpack Black", "brand": "Wildcraft", "price": 2499, "mrp": 4999, "specs": {"Capacity": "35L", "Material": "Nylon", "Compartments": "Multiple", "Padding": "Ergonomic Back Panel", "Straps": "Adjustable Padded", "Gender": "Unisex"}},
    {"title": "Wildcraft 45L Hiking Backpack Grey", "brand": "Wildcraft", "price": 2999, "mrp": 5999, "specs": {"Capacity": "45L", "Material": "Nylon", "Compartments": "Multiple + Hydration", "Padding": "Ergonomic Back Panel", "Straps": "Adjustable Padded", "Gender": "Unisex"}},
    {"title": "Wildcraft 25L Everyday Backpack Blue", "brand": "Wildcraft", "price": 1799, "mrp": 3499, "specs": {"Capacity": "25L", "Material": "Polyester", "Compartments": "3 + Laptop Sleeve", "Padding": "Padded Back", "Straps": "Adjustable", "Gender": "Unisex"}},
    {"title": "Levi's 511 Slim Fit Men's Jeans Grey", "brand": "Levi's", "price": 3299, "mrp": 4999, "specs": {"Fit": "Slim Fit", "Rise": "Mid Rise", "Material": "98% Cotton, 2% Elastane", "Closure": "Button Fly", "Care": "Machine Wash", "Gender": "Men"}},
    {"title": "Allen Solly Men Slim Fit Formal Shirt Light Pink", "brand": "Allen Solly", "price": 1399, "mrp": 2799, "specs": {"Fit": "Slim Fit", "Material": "100% Cotton", "Sleeve": "Full Sleeve", "Collar": "Spread Collar", "Pattern": "Solid", "Gender": "Men"}},
    {"title": "Peter England Men Regular Fit Chinos Khaki", "brand": "Peter England", "price": 1299, "mrp": 2499, "specs": {"Fit": "Regular Fit", "Material": "97% Cotton, 3% Elastane", "Rise": "Mid Rise", "Closure": "Zip Fly", "Care": "Machine Wash", "Gender": "Men"}},
]

# ---------------------------------------------------------------------------
# CATEGORY MAP
# ---------------------------------------------------------------------------
CATEGORY_MAP = {
    "Smartphones": SMARTPHONES,
    "Laptops": LAPTOPS,
    "Headphones": HEADPHONES,
    "Earbuds": EARBUDS,
    "Tablets": TABLETS,
    "TVs": TVS,
    "Footwear": FOOTWEAR,
    "Watches": WATCHES,
    "Kitchen Appliances": KITCHEN,
    "Cameras": CAMERAS,
    "Fashion": FASHION,
}


class Command(BaseCommand):
    help = "Seed 255+ products across 11 categories with multi-platform offers and 30-day price history"

    def handle(self, *args, **options):
        self.stdout.write("Seeding large product catalog...")

        platforms = {}
        for p in Platform.objects.all():
            platforms[p.name] = p

        Product.objects.all().delete()

        total_products = 0
        total_offers = 0
        total_history = 0

        for category, products in CATEGORY_MAP.items():
            for data in products:
                product = Product.objects.create(
                    title=data["title"],
                    brand=data["brand"],
                    category=category,
                    image_url=_img(category, data["title"][:30]),
                    description=data["title"],
                    specifications=data.get("specs", {}),
                )
                total_products += 1

                offers = _make_offers(data, data["price"], data["mrp"], category)

                for offer_data in offers:
                    store_name = offer_data["store_name"]
                    if store_name not in platforms:
                        platform, _ = Platform.objects.get_or_create(
                            name=store_name,
                            defaults={"is_active": True},
                        )
                        platforms[store_name] = platform

                    price = offer_data["price"]
                    mrp = offer_data["mrp"]
                    coupon_discount = offer_data.get("coupon_discount", 0)

                    ProductOffer.objects.create(
                        product=product,
                        platform=platforms[store_name],
                        store_name=store_name,
                        current_price=Decimal(str(price)),
                        original_price=Decimal(str(mrp)),
                        coupon_code=offer_data.get("coupon", ""),
                        coupon_discount=Decimal(str(coupon_discount)) if coupon_discount else None,
                        rating=Decimal(str(offer_data["rating"])),
                        reviews_count=offer_data["reviews"],
                        product_url=offer_data["url"],
                        in_stock=True,
                        delivery_days=offer_data.get("delivery_days", 3),
                        data_source="dataset",
                    )
                    total_offers += 1

                    for day_offset in range(30):
                        recorded = timezone.now() - timezone.timedelta(days=day_offset)
                        variation = random.uniform(-0.05, 0.05)
                        history_price = round(price * (1 + variation), 2)
                        PriceHistory.objects.create(
                            product=product,
                            store_name=store_name,
                            price=Decimal(str(history_price)),
                            recorded_at=recorded,
                        )
                        total_history += 1

            self.stdout.write(f"  {category}: {len(products)} products created")

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {total_products} products, {total_offers} offers, {total_history} price history records"
        ))
