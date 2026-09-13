import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Platform, Product, ProductOffer, PriceHistory


def _smart_round(price):
    """Round price to a sensible precision based on magnitude."""
    if price < 1000:
        return round(price / 10) * 10
    elif price < 10000:
        return round(price / 50) * 50
    elif price < 100000:
        return round(price / 100) * 100
    else:
        return round(price / 500) * 500


def _img(category, label):
    colors = {
        "Smartphones": "06b6d4", "Laptops": "10b981", "Headphones": "8b5cf6",
        "Earbuds": "f43f5e", "Tablets": "3b82f6", "TVs": "06b6d4",
        "Footwear": "f59e0b", "Watches": "ec4899", "Kitchen Appliances": "10b981",
        "Cameras": "f97316", "Fashion": "6366f1",
    }
    c = colors.get(category, "06b6d4")
    return f"https://placehold.co/400x400/0b0f19/{c}?text={label.replace(' ', '+')}"


def _make_offers(base_price, mrp, category, product_url_slug):
    electronics = ["Amazon", "Flipkart", "Croma", "Reliance Digital", "Tata CLiQ"]
    fashion = ["Amazon", "Flipkart", "Myntra", "AJIO"]
    kitchen = ["Amazon", "Flipkart", "Croma"]
    watches = ["Amazon", "Flipkart", "Croma"]

    if category in ("Fashion", "Footwear"):
        pool = fashion
    elif category == "Kitchen Appliances":
        pool = kitchen
    elif category == "Watches":
        pool = watches
    else:
        pool = electronics

    selected = random.sample(pool, min(4, len(pool)))
    offers = []
    for store in selected:
        variation = random.uniform(-0.08, 0.08)
        price = round(base_price * (1 + variation) / 100) * 100
        price = max(price, 499)
        if mrp and price > mrp:
            price = round(mrp * 0.85 / 100) * 100

        coupon = ""
        coupon_discount = 0
        if random.random() < 0.3:
            codes = ["BANK500", "HDFC1000", "ICICI750", "AXIS500", "EXCHANGE1000", "FLAT10OFF"]
            coupon = random.choice(codes)
            coupon_discount = round(price * random.uniform(0.03, 0.10) / 10) * 10

        domain_map = {
            "Amazon": "amazon.in", "Flipkart": "flipkart.com",
            "Croma": "croma.com", "Reliance Digital": "reliancedigital.in",
            "Tata CLiQ": "tatacliq.com", "Myntra": "myntra.com", "AJIO": "ajio.com",
        }
        url = f"https://www.{domain_map[store]}/{product_url_slug}"

        offers.append({
            "store_name": store,
            "current_price": Decimal(str(price)),
            "original_price": Decimal(str(mrp)),
            "product_url": url,
            "rating": round(random.uniform(3.8, 4.8), 1),
            "reviews_count": random.randint(100, 15000),
            "in_stock": random.random() > 0.1,
            "delivery_days": random.randint(1, 5),
            "delivery_time": f"{random.randint(1, 5)} days",
            "coupon_code": coupon,
            "coupon_discount": Decimal(str(coupon_discount)),
            "data_source": "demo",
        })
    return offers


PRODUCTS = [
    # ===== SMARTPHONES (15) =====
    ("Samsung Galaxy S24 Ultra 5G 256GB Titanium Black", "Samsung", "Smartphones",
     115000, 134999, {"Display": '6.8" Dynamic AMOLED 2X', "RAM": "12 GB", "Storage": "256 GB", "Camera": "200 MP", "Battery": "5000 mAh"}, "samsung-galaxy-s24-ultra-256gb-titanium-black"),
    ("Samsung Galaxy S24+ 5G 256GB Amber Yellow", "Samsung", "Smartphones",
     74999, 99999, {"Display": '6.7" Dynamic AMOLED 2X', "RAM": "12 GB", "Storage": "256 GB", "Camera": "50 MP"}, "samsung-galaxy-s24-plus-256gb"),
    ("Samsung Galaxy A54 5G 128GB Awesome Graphite", "Samsung", "Smartphones",
     28999, 38999, {"Display": '6.4" Super AMOLED', "RAM": "8 GB", "Storage": "128 GB"}, "samsung-galaxy-a54-128gb"),
    ("Samsung Galaxy A35 5G 128GB Awesome Lilac", "Samsung", "Smartphones",
     22999, 29999, {"Display": '6.6" Super AMOLED', "RAM": "6 GB", "Storage": "128 GB"}, "samsung-galaxy-a35-128gb"),
    ("Apple iPhone 15 Pro Max 256GB Natural Titanium", "Apple", "Smartphones",
     144900, 159900, {"Display": '6.7" Super Retina XDR', "RAM": "8 GB", "Storage": "256 GB", "Camera": "48 MP"}, "apple-iphone-15-pro-max-256gb"),
    ("Apple iPhone 15 128GB Black", "Apple", "Smartphones",
     65999, 79900, {"Display": '6.1" Super Retina XDR', "RAM": "6 GB", "Storage": "128 GB"}, "apple-iphone-15-128gb-black"),
    ("Apple iPhone 16 128GB Ultramarine", "Apple", "Smartphones",
     73999, 79900, {"Display": '6.1" Super Retina XDR', "RAM": "8 GB", "Storage": "128 GB", "Camera": "48 MP"}, "apple-iphone-16-128gb"),
    ("OnePlus 12 5G 256GB Silky Black", "OnePlus", "Smartphones",
     64999, 69999, {"Display": '6.82" LTPO AMOLED', "RAM": "16 GB", "Storage": "256 GB"}, "oneplus-12-256gb-black"),
    ("OnePlus Nord CE4 5G 128GB Dark Chrome", "OnePlus", "Smartphones",
     21999, 26999, {"Display": '6.7" AMOLED', "RAM": "8 GB", "Storage": "128 GB"}, "oneplus-nord-ce4-128gb"),
    ("Xiaomi 14 5G 256GB Black", "Xiaomi", "Smartphones",
     62999, 69999, {"Display": '6.36" LTPO AMOLED', "RAM": "12 GB", "Storage": "256 GB"}, "xiaomi-14-256gb-black"),
    ("Realme GT 6 5G 256GB Fluid Silver", "Realme", "Smartphones",
     34999, 39999, {"Display": '6.78" LTPO AMOLED', "RAM": "12 GB", "Storage": "256 GB"}, "realme-gt-6-256gb"),
    ("Motorola Edge 50 Pro 5G 256GB Black Beauty", "Motorola", "Smartphones",
     31999, 35999, {"Display": '6.7" pOLED', "RAM": "12 GB", "Storage": "256 GB"}, "motorola-edge-50-pro-256gb"),
    ("Nothing Phone (2a) 128GB Black", "Nothing", "Smartphones",
     19999, 23999, {"Display": '6.7" AMOLED', "RAM": "8 GB", "Storage": "128 GB"}, "nothing-phone-2a-128gb"),
    ("Google Pixel 8 128GB Obsidian", "Google", "Smartphones",
     69999, 79999, {"Display": '6.2" OLED', "RAM": "8 GB", "Storage": "128 GB", "Camera": "50 MP"}, "google-pixel-8-128gb"),
    ("Vivo X100 5G 256GB Asteroid Black", "Vivo", "Smartphones",
     63999, 69999, {"Display": '6.78" LTPO AMOLED', "RAM": "12 GB", "Storage": "256 GB"}, "vivo-x100-256gb"),

    # ===== LAPTOPS (10) =====
    ("Apple MacBook Air M3 15-inch 16GB 512GB Midnight", "Apple", "Laptops",
     134999, 149900, {"Display": '15.3" Liquid Retina', "Chip": "Apple M3", "RAM": "16 GB", "Storage": "512 GB SSD"}, "macbook-air-m3-15"),
    ("Apple MacBook Air M2 13-inch 8GB 256GB Midnight", "Apple", "Laptops",
     99999, 119900, {"Display": '13.6" Liquid Retina', "Chip": "Apple M2", "RAM": "8 GB", "Storage": "256 GB SSD"}, "macbook-air-m2-13"),
    ("HP Pavilion 15 13th Gen i5 8GB 512GB", "HP", "Laptops",
     47999, 58999, {"Display": '15.6" FHD IPS', "Processor": "Intel i5-1335U", "RAM": "8 GB", "Storage": "512 GB SSD"}, "hp-pavilion-15-i5"),
    ("Dell XPS 15 9530 13th Gen i7 16GB 512GB", "Dell", "Laptops",
     139999, 159999, {"Display": '15.6" OLED 3.5K', "Processor": "Intel i7-13700H", "RAM": "16 GB", "Storage": "512 GB SSD"}, "dell-xps-15-9530"),
    ("Lenovo ThinkPad E16 Gen 1 i5 16GB 512GB", "Lenovo", "Laptops",
     65999, 78999, {"Display": '16" WUXGA IPS', "Processor": "Intel i5-1335U", "RAM": "16 GB", "Storage": "512 GB SSD"}, "lenovo-thinkpad-e16"),
    ("ASUS ROG Strix G16 2024 i9 RTX 4070 32GB 1TB", "ASUS", "Laptops",
     169999, 199999, {"Display": '16" QHD 240Hz', "Processor": "Intel i9-14900HX", "GPU": "RTX 4070", "RAM": "32 GB"}, "asus-rog-strix-g16"),
    ("Acer Nitro V 15 i5 RTX 4050 16GB 512GB", "Acer", "Laptops",
     72999, 89999, {"Display": '15.6" FHD 144Hz', "Processor": "Intel i5-13420H", "GPU": "RTX 4050", "RAM": "16 GB"}, "acer-nitro-v-15"),
    ("HP Victus 15 i5 RTX 4050 16GB 512GB", "HP", "Laptops",
     68999, 79999, {"Display": '15.6" FHD 144Hz', "Processor": "Intel i5-13500H", "GPU": "RTX 4050"}, "hp-victus-15"),
    ("Lenovo Legion 5 i7 RTX 4060 16GB 1TB", "Lenovo", "Laptops",
     109999, 129999, {"Display": '16" WQXGA 165Hz', "Processor": "Intel i7-12700H", "GPU": "RTX 4060"}, "lenovo-legion-5"),
    ("ASUS ZenBook 14 OLED i7 16GB 1TB", "ASUS", "Laptops",
     96999, 109999, {"Display": '14" 2.8K OLED', "Processor": "Intel i7-1360P", "RAM": "16 GB"}, "asus-zenbook-14-oled"),

    # ===== HEADPHONES (10) =====
    ("Sony WH-1000XM5 Wireless NC Headphones Black", "Sony", "Headphones",
     26990, 34990, {"Type": "Over-Ear", "ANC": "Yes", "Battery": "30 hours", "Driver": "30mm"}, "sony-wh-1000xm5-black"),
    ("Sony WH-1000XM4 Wireless NC Headphones Black", "Sony", "Headphones",
     19990, 29990, {"Type": "Over-Ear", "ANC": "Yes", "Battery": "30 hours"}, "sony-wh-1000xm4-black"),
    ("Bose QuietComfort Ultra Headphones Black", "Bose", "Headphones",
     34990, 39990, {"Type": "Over-Ear", "ANC": "Yes", "Battery": "24 hours"}, "bose-qc-ultra-headphones"),
    ("JBL Tune 770NC Wireless Over-Ear Black", "JBL", "Headphones",
     5999, 7999, {"Type": "Over-Ear", "ANC": "Yes", "Battery": "44 hours"}, "jbl-tune-770nc-black"),
    ("Sennheiser Momentum 4 Wireless NC Black", "Sennheiser", "Headphones",
     24999, 32999, {"Type": "Over-Ear", "ANC": "Yes", "Battery": "60 hours"}, "sennheiser-momentum-4"),
    ("Boat Rockerz 550 Over-Ear Wireless Black", "Boat", "Headphones",
     1999, 3999, {"Type": "Over-Ear", "ANC": "No", "Battery": "20 hours"}, "boat-rockerz-550-black"),
    ("Sony ULT WEAR Wireless NC Headphones Black", "Sony", "Headphones",
     15990, 19990, {"Type": "Over-Ear", "ANC": "Yes", "Battery": "30 hours"}, "sony-ult-wear"),
    ("JBL Tune 520BT Wireless On-Ear Black", "JBL", "Headphones",
     2499, 3999, {"Type": "On-Ear", "ANC": "No", "Battery": "57 hours"}, "jbl-tune-520bt-black"),
    ("Audio-Technica ATH-M20xBT Wireless Black", "Audio-Technica", "Headphones",
     4999, 5999, {"Type": "Over-Ear", "ANC": "No", "Battery": "60 hours"}, "audio-technica-ath-m20xbt"),
    ("Noise Air-cancel+ Wireless ANC Black", "Noise", "Headphones",
     4499, 5999, {"Type": "Over-Ear", "ANC": "Yes", "Battery": "50 hours"}, "noise-air-cancel-plus"),

    # ===== EARBUDS (10) =====
    ("Apple AirPods Pro (2nd Gen) USB-C", "Apple", "Earbuds",
     21999, 24900, {"Type": "TWS", "ANC": "Yes", "Battery": "6 hours", "Connectivity": "Bluetooth 5.3"}, "apple-airpods-pro-2"),
    ("Samsung Galaxy Buds FE Graphite", "Samsung", "Earbuds",
     5499, 9999, {"Type": "TWS", "ANC": "Yes", "Battery": "6 hours"}, "samsung-galaxy-buds-fe"),
    ("Sony WF-1000XM5 TWS Earbuds Black", "Sony", "Earbuds",
     24990, 29990, {"Type": "TWS", "ANC": "Yes", "Battery": "8 hours"}, "sony-wf-1000xm5"),
    ("OnePlus Buds Pro 2 TWS Earbuds Black", "OnePlus", "Earbuds",
     8999, 11999, {"Type": "TWS", "ANC": "Yes", "Battery": "6 hours"}, "oneplus-buds-pro-2"),
    ("Boat Airdopes 141 TWS Earbuds Black", "Boat", "Earbuds",
     1299, 2999, {"Type": "TWS", "ANC": "No", "Battery": "42 hours total"}, "boat-airdopes-141"),
    ("JBL Tune Buds TWS Earbuds Black", "JBL", "Earbuds",
     3999, 5999, {"Type": "TWS", "ANC": "Yes", "Battery": "8 hours"}, "jbl-tune-buds"),
    ("Realme Buds T300 TWS Earbuds Black", "Realme", "Earbuds",
     1999, 3999, {"Type": "TWS", "ANC": "Yes", "Battery": "6 hours"}, "realme-buds-t300"),
    ("Nothing Ear (2) TWS Earbuds White", "Nothing", "Earbuds",
     7999, 9999, {"Type": "TWS", "ANC": "Yes", "Battery": "6 hours"}, "nothing-ear-2"),
    ("Sony LinkBuds S WF-LS900N White", "Sony", "Earbuds",
     14990, 19990, {"Type": "TWS", "ANC": "Yes", "Battery": "6 hours"}, "sony-linkbuds-s"),
    ("OnePlus Nord Buds 2r Triple Black", "OnePlus", "Earbuds",
     2299, 3999, {"Type": "TWS", "ANC": "No", "Battery": "8 hours"}, "oneplus-nord-buds-2r"),

    # ===== TABLETS (6) =====
    ("Apple iPad (10th Gen) 64GB Wi-Fi Silver", "Apple", "Tablets",
     34999, 44900, {"Display": '10.9" Liquid Retina', "Chip": "A14 Bionic", "Storage": "64 GB"}, "apple-ipad-10th-gen-64gb"),
    ("Apple iPad Air M2 11-inch 128GB Space Gray", "Apple", "Tablets",
     59999, 69900, {"Display": '11" Liquid Retina', "Chip": "Apple M2", "Storage": "128 GB"}, "apple-ipad-air-m2-11"),
    ("Samsung Galaxy Tab S9 FE 10.9-inch 128GB", "Samsung", "Tablets",
     34999, 44999, {"Display": '10.9" TFT LCD', "RAM": "6 GB", "Storage": "128 GB"}, "samsung-galaxy-tab-s9-fe"),
    ("Samsung Galaxy Tab A9 8.7-inch 64GB", "Samsung", "Tablets",
     14999, 19999, {"Display": '8.7" TFT LCD', "Storage": "64 GB"}, "samsung-galaxy-tab-a9"),
    ("Lenovo Tab P12 12.7-inch 128GB", "Lenovo", "Tablets",
     24999, 31999, {"Display": '12.7" 2.9K LCD', "RAM": "4 GB", "Storage": "128 GB"}, "lenovo-tab-p12"),
    ("Apple iPad Pro M4 11-inch 256GB Space Black", "Apple", "Tablets",
     99999, 119900, {"Display": '11" Ultra Retina XDR', "Chip": "Apple M4", "Storage": "256 GB"}, "apple-ipad-pro-m4-11"),

    # ===== TVs (8) =====
    ("Samsung 55-inch Crystal 4K UHD Smart TV CU7700", "Samsung", "TVs",
     42999, 54999, {"Display": '55" Crystal 4K UHD', "HDR": "HDR10+", "OS": "Tizen"}, "samsung-55-crystal-4k-cu7700"),
    ("Samsung 65-inch Neo QLED 4K Smart TV QN85C", "Samsung", "TVs",
     129999, 159999, {"Display": '65" Neo QLED 4K', "HDR": "Neo QLED", "OS": "Tizen"}, "samsung-65-neo-qled-qn85c"),
    ("LG 55-inch OLED evo 4K Smart TV OLED55C4", "LG", "TVs",
     109999, 129999, {"Display": '55" OLED evo 4K', "HDR": "Dolby Vision", "OS": "webOS"}, "lg-55-oled-c4"),
    ("Sony 65-inch BRAVIA XR 4K Mini LED XR65X95L", "Sony", "TVs",
     169999, 199999, {"Display": '65" Mini LED 4K', "HDR": "XR HDR", "OS": "Google TV"}, "sony-65-bravia-xr-x95l"),
    ("TCL 55-inch QLED 4K Smart TV 55C645", "TCL", "TVs",
     41999, 54999, {"Display": '55" QLED 4K', "HDR": "Dolby Vision", "OS": "Google TV"}, "tcl-55-qled-c645"),
    ("Hisense 55-inch ULED 4K Smart TV 55U7K", "Hisense", "TVs",
     49999, 59999, {"Display": '55" ULED 4K', "HDR": "Dolby Vision", "OS": "VIDAA"}, "hisense-55-uled-u7k"),
    ("Mi 55-inch QLED 4K Smart TV", "Mi", "TVs",
     39999, 49999, {"Display": '55" QLED 4K', "HDR": "Dolby Vision", "OS": "PatchWall"}, "mi-55-qled"),
    ("Samsung 55-inch OLED 4K Smart TV S90C", "Samsung", "TVs",
     109999, 129999, {"Display": '55" OLED 4K', "HDR": "HDR10+", "OS": "Tizen"}, "samsung-55-oled-s90c"),

    # ===== FOOTWEAR (8) =====
    ("Nike Air Max 270 Men's Running Shoes", "Nike", "Footwear",
     12999, 15999, {"Type": "Running", "Sole": "Rubber", "Upper": "Mesh"}, "nike-air-max-270"),
    ("Nike Pegasus 41 Men's Running Shoes", "Nike", "Footwear",
     11999, 13999, {"Type": "Running", "Sole": "Rubber", "Cushioning": "React"}, "nike-pegasus-41"),
    ("Adidas Ultraboost Light Men's Running", "Adidas", "Footwear",
     16999, 19999, {"Type": "Running", "Sole": "Continental Rubber", "Upper": "Primeknit"}, "adidas-ultraboost-light"),
    ("Adidas Stan Smith Men's Shoes", "Adidas", "Footwear",
     8999, 10999, {"Type": "Casual", "Sole": "Rubber", "Upper": "Leather"}, "adidas-stan-smith"),
    ("Puma RS-X Men's Sneakers", "Puma", "Footwear",
     8999, 11999, {"Type": "Sneaker", "Sole": "Rubber", "Upper": "Mesh/Leather"}, "puma-rs-x"),
    ("Reebok Club C 85 Men's Shoes", "Reebok", "Footwear",
     6999, 8999, {"Type": "Casual", "Sole": "Rubber", "Upper": "Leather"}, "reebok-club-c-85"),
    ("New Balance 550 Men's Shoes", "New Balance", "Footwear",
     10999, 12999, {"Type": "Casual", "Sole": "Rubber", "Upper": "Leather"}, "new-balance-550"),
    ("Nike Dunk Low Retro Men's Shoes", "Nike", "Footwear",
     9499, 11999, {"Type": "Sneaker", "Sole": "Rubber", "Upper": "Leather"}, "nike-dunk-low-retro"),

    # ===== WATCHES (6) =====
    ("Apple Watch SE (2nd Gen) 40mm GPS Midnight", "Apple", "Watches",
     29999, 34999, {"Display": '1.78" OLED', "Chip": "S8 SiP", "Battery": "18 hours"}, "apple-watch-se-2nd-40mm"),
    ("Samsung Galaxy Watch 6 44mm Bluetooth", "Samsung", "Watches",
     26999, 30999, {"Display": '1.47" Super AMOLED', "Chip": "Exynos W930", "Battery": "40 hours"}, "samsung-galaxy-watch-6-44mm"),
    ("Fire-Boltt Phoenix Ultra Smartwatch", "Fire-Boltt", "Watches",
     2999, 5999, {"Display": '1.39" AMOLED', "Battery": "7 days", "Water": "IP67"}, "fire-boltt-phoenix-ultra"),
    ("Noise ColorFit Pro 5 Smartwatch", "Noise", "Watches",
     3499, 5999, {"Display": '1.85" AMOLED', "Battery": "7 days", "Water": "IP68"}, "noise-colorfit-pro-5"),
    ("Fastrack Reflex Smartwatch", "Fastrack", "Watches",
     1999, 3499, {"Display": "1.4 inch TFT LCD", "Battery": "5 days", "Water": "IP68"}, "fastrack-reflex"),
    ("Apple Watch Series 9 41mm GPS Midnight", "Apple", "Watches",
     41999, 49999, {"Display": '1.7" OLED', "Chip": "S9 SiP", "Battery": "18 hours"}, "apple-watch-series-9-41mm"),

    # ===== KITCHEN (6) =====
    ("Philips HL7756/00 750W Mixer Grinder 3 Jars", "Philips", "Kitchen Appliances",
     3499, 4495, {"Power": "750W", "Jars": "3", "Warranty": "2 Years"}, "philips-hl7756-mixer-grinder"),
    ("Prestige Iris 750W Mixer Grinder 3 Jars", "Prestige", "Kitchen Appliances",
     2599, 3195, {"Power": "750W", "Jars": "3", "Warranty": "2 Years"}, "prestige-iris-750w"),
    ("Bajaj Rex Mixer Grinder 500W 3 Jars", "Bajaj", "Kitchen Appliances",
     2199, 2795, {"Power": "500W", "Jars": "3", "Warranty": "2 Years"}, "bajaj-rex-mixer-grinder"),
    ("Butterfly Jet Elite 750W Mixer Grinder", "Butterfly", "Kitchen Appliances",
     2799, 3495, {"Power": "750W", "Jars": "3", "Warranty": "2 Years"}, "butterfly-jet-elite-750w"),
    ("Philips HD9200 Air Fryer 4.1L", "Philips", "Kitchen Appliances",
     7499, 9995, {"Capacity": "4.1L", "Power": "1400W", "Warranty": "2 Years"}, "philips-hd9200-air-fryer"),
    ("Prestige PKOSS 1.5L Electric Kettle", "Prestige", "Kitchen Appliances",
     899, 1195, {"Capacity": "1.5L", "Power": "1500W", "Material": "Stainless Steel"}, "prestige-pkoss-kettle"),

    # ===== CAMERAS (6) =====
    ("Sony ZV-E10 Mirrorless Camera 16-50mm", "Sony", "Cameras",
     54999, 64999, {"Sensor": "APS-C 24.2 MP", "Lens": "16-50mm", "Video": "4K 30fps"}, "sony-zv-e10"),
    ("Canon EOS R50 Mirrorless 18-45mm", "Canon", "Cameras",
     74999, 89999, {"Sensor": "APS-C 24.2 MP", "Lens": "18-45mm", "Video": "4K 30fps"}, "canon-eos-r50"),
    ("Nikon Z30 Mirrorless 16-50mm", "Nikon", "Cameras",
     64999, 74999, {"Sensor": "APS-C 20.9 MP", "Lens": "16-50mm", "Video": "4K 30fps"}, "nikon-z30"),
    ("GoPro Hero 13 Black Action Camera", "GoPro", "Cameras",
     41999, 49999, {"Sensor": "27 MP", "Video": "5.3K 60fps", "Waterproof": "10m"}, "gopro-hero-13-black"),
    ("Sony Alpha A6400 Mirrorless 16-50mm", "Sony", "Cameras",
     72999, 84999, {"Sensor": "APS-C 24.2 MP", "Lens": "16-50mm", "Video": "4K 30fps"}, "sony-alpha-a6400"),
    ("Canon EOS R100 Mirrorless 18-45mm", "Canon", "Cameras",
     44999, 54999, {"Sensor": "APS-C 24.1 MP", "Lens": "18-45mm", "Video": "4K 25fps"}, "canon-eos-r100"),

    # ===== FASHION (6) =====
    ("Levi's 511 Slim Fit Mid Rise Jeans Classic Blue", "Levi's", "Fashion",
     2999, 3999, {"Fit": "Slim", "Rise": "Mid Rise", "Material": "Cotton Denim"}, "levi-511-slim-fit-jeans-blue"),
    ("Levi's 512 Slim Taper Fit Jeans Black", "Levi's", "Fashion",
     3499, 4499, {"Fit": "Slim Taper", "Rise": "Mid Rise", "Material": "Cotton Denim"}, "levi-512-slim-taper-black"),
    ("Allen Solly Men Slim Fit Formal Shirt Blue", "Allen Solly", "Fashion",
     1499, 1999, {"Fit": "Slim Fit", "Sleeve": "Full Sleeve", "Material": "Cotton Blend"}, "allen-solly-slim-formal-blue"),
    ("Peter England Men Regular Fit Polo Navy Blue", "Peter England", "Fashion",
     899, 1299, {"Fit": "Regular", "Sleeve": "Half Sleeve", "Material": "Cotton"}, "peter-england-polo-navy"),
    ("Wildcraft 35L Hiking Backpack Black", "Wildcraft", "Fashion",
     2499, 3499, {"Capacity": "35L", "Material": "Nylon", "Type": "Hiking"}, "wildcraft-35l-backpack"),
    ("Allen Solly Men Casual Shirt Navy Blue", "Allen Solly", "Fashion",
     1699, 2299, {"Fit": "Slim Fit", "Sleeve": "Full Sleeve", "Material": "Cotton"}, "allen-solly-casual-navy"),
]


class Command(BaseCommand):
    help = "Seed 75 products with targeted data for academic demo"

    def handle(self, *args, **options):
        self.stdout.write("Deleting existing data...")
        PriceHistory.objects.all().delete()
        ProductOffer.objects.all().delete()
        Product.objects.all().delete()

        platforms_names = {
            "Amazon", "Flipkart", "Croma", "Reliance Digital", "Tata CLiQ",
            "Myntra", "AJIO", "Meesho",
        }
        platforms = {}
        for name in platforms_names:
            p, _ = Platform.objects.get_or_create(
                name=name,
            )
            platforms[name] = p

        self.stdout.write(f"Creating {len(PRODUCTS)} products...")
        total_offers = 0
        total_history = 0
        total_coupons = 0

        for title, brand, category, price, mrp, specs, slug in PRODUCTS:
            product = Product.objects.create(
                title=title,
                brand=brand,
                category=category,
                image_url=_img(category, brand),
                description=f"{title} - Best price comparison across platforms",
                specifications=specs,
            )

            offers_data = _make_offers(price, mrp, category, slug)
            now = timezone.now()

            for od in offers_data:
                offer = ProductOffer.objects.create(
                    product=product,
                    **od,
                )
                total_offers += 1
                if offer.coupon_code:
                    total_coupons += 1

                base_p = float(offer.current_price)
                current_price = base_p
                for day_offset in range(30, -1, -1):
                    change = random.uniform(-0.06, 0.06)
                    current_price = current_price * (1 + change)
                    current_price = max(current_price, 199)
                    current_price = _smart_round(current_price)
                    PriceHistory.objects.create(
                        product=product,
                        store_name=offer.store_name,
                        price=Decimal(str(current_price)),
                        recorded_at=now - timezone.timedelta(days=day_offset),
                    )
                    total_history += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Products: {Product.objects.count()}, "
            f"Offers: {total_offers}, Price History: {total_history}, "
            f"Coupons: {total_coupons}"
        ))
