import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Platform, Product, ProductOffer, PriceHistory


DEMO_PRODUCTS = [
    {
        "title": "Samsung Galaxy S24 5G 256GB Onyx Black",
        "brand": "Samsung",
        "category": "Smartphones",
        "image_url": "https://placehold.co/400x400/0b0f19/06b6d4?text=Galaxy+S24",
        "description": "Samsung Galaxy S24 with AI features, 50MP camera, Exynos 2400 processor, 4000mAh battery.",
        "specifications": {
            "Display": '6.2" Dynamic AMOLED 2X, 120Hz',
            "Processor": "Exynos 2400",
            "RAM": "8 GB",
            "Storage": "256 GB",
            "Camera": "50MP + 12MP + 10MP",
            "Battery": "4000 mAh",
            "OS": "Android 14, One UI 6.1",
        },
        "offers": [
            {"store_name": "Amazon", "price": 64999, "mrp": 79999, "rating": 4.4, "reviews": 8900, "delivery_days": 2, "coupon": "BANK3000", "coupon_discount": 3000, "url": "https://www.amazon.in/dp/B0CMDL3YZ7"},
            {"store_name": "Flipkart", "price": 62999, "mrp": 79999, "rating": 4.3, "reviews": 6700, "delivery_days": 1, "coupon": "HDFC5000", "coupon_discount": 5000, "url": "https://www.flipkart.com/samsung-galaxy-s24-5g/p/itm1234"},
            {"store_name": "Croma", "price": 67999, "mrp": 79999, "rating": 4.2, "reviews": 234, "delivery_days": 3, "coupon": "", "coupon_discount": 0, "url": "https://www.croma.com/samsung-galaxy-s24-256gb"},
            {"store_name": "Reliance Digital", "price": 64999, "mrp": 79999, "rating": 4.3, "reviews": 345, "delivery_days": 2, "coupon": "EXCHANGE5000", "coupon_discount": 5000, "url": "https://www.reliancedigital.in/samsung-galaxy-s24"},
        ],
    },
    {
        "title": "Samsung Galaxy S25 5G 256GB Navy",
        "brand": "Samsung",
        "category": "Smartphones",
        "image_url": "https://placehold.co/400x400/0b0f19/06b6d4?text=Galaxy+S25",
        "description": "Samsung Galaxy S25 5G with 12GB RAM, 256GB storage, 50MP camera, Snapdragon 8 Elite processor.",
        "specifications": {
            "Display": '6.2" Dynamic AMOLED 2X, 120Hz',
            "Processor": "Snapdragon 8 Elite for Galaxy",
            "RAM": "12 GB",
            "Storage": "256 GB",
            "Camera": "50MP + 12MP + 10MP",
            "Battery": "4000 mAh",
            "OS": "Android 15, One UI 7",
            "5G": "Yes",
        },
        "offers": [
            {"store_name": "Amazon", "price": 74999, "mrp": 84999, "rating": 4.5, "reviews": 12450, "delivery_days": 2, "coupon": "BANK1000", "coupon_discount": 1000, "url": "https://www.amazon.in/dp/B0DXYZ1234"},
            {"store_name": "Flipkart", "price": 72999, "mrp": 84999, "rating": 4.4, "reviews": 8920, "delivery_days": 1, "coupon": "FLAT3000", "coupon_discount": 3000, "url": "https://www.flipkart.com/samsung-galaxy-s25-5g-256gb-navy/p/itm1234"},
            {"store_name": "Croma", "price": 75999, "mrp": 84999, "rating": 4.3, "reviews": 342, "delivery_days": 3, "coupon": "", "coupon_discount": 0, "url": "https://www.croma.com/samsung-galaxy-s25-5g-256gb"},
            {"store_name": "Reliance Digital", "price": 74499, "mrp": 84999, "rating": 4.4, "reviews": 567, "delivery_days": 2, "coupon": "RELIANCE500", "coupon_discount": 500, "url": "https://www.reliancedigital.in/samsung-galaxy-s25"},
            {"store_name": "Tata CLiQ", "price": 73999, "mrp": 84999, "rating": 4.3, "reviews": 234, "delivery_days": 3, "coupon": "", "coupon_discount": 0, "url": "https://www.tatacliq.com/samsung-galaxy-s25-256gb"},
        ],
    },
    {
        "title": "Apple iPhone 16 128GB Black",
        "brand": "Apple",
        "category": "Smartphones",
        "image_url": "https://placehold.co/400x400/0b0f19/f59e0b?text=iPhone+16",
        "description": "Apple iPhone 16 with A18 chip, 48MP camera system, 6.1 inch Super Retina XDR display.",
        "specifications": {
            "Display": '6.1" Super Retina XDR OLED',
            "Processor": "Apple A18 Bionic",
            "RAM": "8 GB",
            "Storage": "128 GB",
            "Camera": "48MP + 12MP",
            "Battery": "3561 mAh",
            "OS": "iOS 18",
            "5G": "Yes",
        },
        "offers": [
            {"store_name": "Amazon", "price": 79900, "mrp": 84900, "rating": 4.6, "reviews": 5670, "delivery_days": 2, "coupon": "", "coupon_discount": 0, "url": "https://www.amazon.in/dp/B0DXYZ5678"},
            {"store_name": "Flipkart", "price": 78999, "mrp": 84900, "rating": 4.5, "reviews": 4320, "delivery_days": 1, "coupon": "HDFC5000", "coupon_discount": 5000, "url": "https://www.flipkart.com/apple-iphone-16-128gb-black/p/itm5678"},
            {"store_name": "Croma", "price": 81900, "mrp": 84900, "rating": 4.4, "reviews": 189, "delivery_days": 3, "coupon": "", "coupon_discount": 0, "url": "https://www.croma.com/apple-iphone-16-128gb"},
            {"store_name": "Reliance Digital", "price": 79900, "mrp": 84900, "rating": 4.5, "reviews": 345, "delivery_days": 2, "coupon": "EXCHANGE5000", "coupon_discount": 5000, "url": "https://www.reliancedigital.in/apple-iphone-16"},
        ],
    },
    {
        "title": "Sony WH-1000XM5 Wireless Noise Cancelling Headphones Black",
        "brand": "Sony",
        "category": "Headphones",
        "image_url": "https://placehold.co/400x400/0b0f19/8b5cf6?text=Sony+XM5",
        "description": "Industry-leading noise cancellation with Auto NC Optimizer, 30-hour battery, multipoint connection.",
        "specifications": {
            "Type": "Over-Ear, Wireless",
            "Driver": "30mm",
            "Frequency Response": "4Hz - 40kHz",
            "Battery": "30 hours (NC ON)",
            "Noise Cancellation": "Adaptive",
            "Bluetooth": "5.2",
            "Weight": "250g",
            "Codec": "LDAC, AAC, SBC",
        },
        "offers": [
            {"store_name": "Amazon", "price": 26990, "mrp": 34990, "rating": 4.5, "reviews": 8930, "delivery_days": 2, "coupon": "SONY2000", "coupon_discount": 2000, "url": "https://www.amazon.in/dp/B0DXYZ9012"},
            {"store_name": "Flipkart", "price": 25990, "mrp": 34990, "rating": 4.4, "reviews": 6540, "delivery_days": 1, "coupon": "FLAT1000", "coupon_discount": 1000, "url": "https://www.flipkart.com/sony-wh-1000xm5-black/p/itm9012"},
            {"store_name": "Croma", "price": 27990, "mrp": 34990, "rating": 4.3, "reviews": 234, "delivery_days": 3, "coupon": "", "coupon_discount": 0, "url": "https://www.croma.com/sony-wh-1000xm5"},
            {"store_name": "Reliance Digital", "price": 26490, "mrp": 34990, "rating": 4.4, "reviews": 456, "delivery_days": 2, "coupon": "RELIANCE1500", "coupon_discount": 1500, "url": "https://www.reliancedigital.in/sony-wh-1000xm5"},
            {"store_name": "Tata CLiQ", "price": 26990, "mrp": 34990, "rating": 4.3, "reviews": 123, "delivery_days": 3, "coupon": "", "coupon_discount": 0, "url": "https://www.tatacliq.com/sony-wh-1000xm5"},
        ],
    },
    {
        "title": "Apple MacBook Air M3 15-inch 16GB 512GB Midnight",
        "brand": "Apple",
        "category": "Laptops",
        "image_url": "https://placehold.co/400x400/0b0f19/10b981?text=MacBook+Air",
        "description": "Apple MacBook Air with M3 chip, 15.3-inch Liquid Retina display, 18-hour battery, 1080p FaceTime camera.",
        "specifications": {
            "Display": '15.3" Liquid Retina',
            "Processor": "Apple M3 (8-core CPU, 10-core GPU)",
            "RAM": "16 GB Unified",
            "Storage": "512 GB SSD",
            "Battery": "Up to 18 hours",
            "Weight": "1.51 kg",
            "Ports": "2x Thunderbolt 4, MagSafe 3, 3.5mm",
            "OS": "macOS Sonoma",
        },
        "offers": [
            {"store_name": "Amazon", "price": 144900, "mrp": 154900, "rating": 4.7, "reviews": 2340, "delivery_days": 3, "coupon": "HDFC10000", "coupon_discount": 10000, "url": "https://www.amazon.in/dp/B0DXYZ3456"},
            {"store_name": "Flipkart", "price": 142999, "mrp": 154900, "rating": 4.6, "reviews": 1890, "delivery_days": 2, "coupon": "AXIS7500", "coupon_discount": 7500, "url": "https://www.flipkart.com/apple-macbook-air-m3-15inch/p/itm3456"},
            {"store_name": "Croma", "price": 149900, "mrp": 154900, "rating": 4.5, "reviews": 89, "delivery_days": 5, "coupon": "", "coupon_discount": 0, "url": "https://www.croma.com/apple-macbook-air-m3-15"},
            {"store_name": "Reliance Digital", "price": 146900, "mrp": 154900, "rating": 4.6, "reviews": 123, "delivery_days": 3, "coupon": "EXCHANGE8000", "coupon_discount": 8000, "url": "https://www.reliancedigital.in/apple-macbook-air-m3"},
        ],
    },
    {
        "title": "Samsung Galaxy S24 Ultra 5G AI Smartphone with Galaxy AI (Titanium Black, 12GB, 256GB Storage), Snapdragon 8 Gen 3, 200 MP Camera with ProVisual Engine and 5000mAh Battery",
        "brand": "Samsung",
        "category": "Smartphones",
        "image_url": "https://placehold.co/400x400/0b0f19/06b6d4?text=Galaxy+S24+Ultra",
        "description": "Samsung Galaxy S24 Ultra with AI features, 200MP camera, Snapdragon 8 Gen 3, titanium frame, S Pen.",
        "specifications": {
            "Display": '6.8" Dynamic AMOLED 2X, 120Hz',
            "Processor": "Snapdragon 8 Gen 3 for Galaxy",
            "RAM": "12 GB",
            "Storage": "256 GB",
            "Camera": "200MP + 12MP + 10MP + 50MP",
            "Battery": "5000 mAh",
            "OS": "Android 14, One UI 6.1",
            "S Pen": "Yes, built-in",
        },
        "offers": [
            {"store_name": "Amazon", "price": 99999, "mrp": 134999, "rating": 4.6, "reviews": 12500, "delivery_days": 3, "coupon": "BANK5000", "coupon_discount": 5000, "url": "https://www.amazon.in/dp/B0CMDL4WP2"},
            {"store_name": "Flipkart", "price": 97999, "mrp": 134999, "rating": 4.5, "reviews": 9800, "delivery_days": 2, "coupon": "HDFC8000", "coupon_discount": 8000, "url": "https://www.flipkart.com/samsung-galaxy-s24-ultra/p/itm6ac6485512ae3"},
            {"store_name": "Croma", "price": 104999, "mrp": 134999, "rating": 4.4, "reviews": 345, "delivery_days": 5, "coupon": "", "coupon_discount": 0, "url": "https://www.croma.com/samsung-galaxy-s24-ultra-256gb"},
            {"store_name": "Reliance Digital", "price": 99999, "mrp": 134999, "rating": 4.5, "reviews": 567, "delivery_days": 3, "coupon": "EXCHANGE10000", "coupon_discount": 10000, "url": "https://www.reliancedigital.in/samsung-galaxy-s24-ultra"},
            {"store_name": "Tata CLiQ", "price": 98999, "mrp": 134999, "rating": 4.4, "reviews": 234, "delivery_days": 4, "coupon": "", "coupon_discount": 0, "url": "https://www.tatacliq.com/samsung-galaxy-s24-ultra-256gb"},
        ],
    },
    {
        "title": "Samsung Galaxy S25 Ultra 5G 512GB Titanium Black",
        "brand": "Samsung",
        "category": "Smartphones",
        "image_url": "https://placehold.co/400x400/0b0f19/06b6d4?text=Galaxy+S25+Ultra",
        "description": "Samsung Galaxy S25 Ultra with S Pen, 200MP camera, Snapdragon 8 Elite, titanium frame.",
        "specifications": {
            "Display": '6.9" Dynamic AMOLED 2X, 120Hz',
            "Processor": "Snapdragon 8 Elite for Galaxy",
            "RAM": "12 GB",
            "Storage": "512 GB",
            "Camera": "200MP + 50MP + 10MP + 50MP",
            "Battery": "5000 mAh",
            "OS": "Android 15, One UI 7",
            "S Pen": "Yes, built-in",
        },
        "offers": [
            {"store_name": "Amazon", "price": 134999, "mrp": 154999, "rating": 4.6, "reviews": 7890, "delivery_days": 2, "coupon": "BANK5000", "coupon_discount": 5000, "url": "https://www.amazon.in/dp/B0DXYZ7890"},
            {"store_name": "Flipkart", "price": 131999, "mrp": 154999, "rating": 4.5, "reviews": 5670, "delivery_days": 1, "coupon": "HDFC10000", "coupon_discount": 10000, "url": "https://www.flipkart.com/samsung-galaxy-s25-ultra-512gb/p/itm7890"},
            {"store_name": "Croma", "price": 137999, "mrp": 154999, "rating": 4.4, "reviews": 456, "delivery_days": 3, "coupon": "", "coupon_discount": 0, "url": "https://www.croma.com/samsung-galaxy-s25-ultra-512gb"},
            {"store_name": "Reliance Digital", "price": 134999, "mrp": 154999, "rating": 4.5, "reviews": 678, "delivery_days": 2, "coupon": "RELIANCE3000", "coupon_discount": 3000, "url": "https://www.reliancedigital.in/samsung-galaxy-s25-ultra"},
            {"store_name": "Tata CLiQ", "price": 133999, "mrp": 154999, "rating": 4.4, "reviews": 234, "delivery_days": 3, "coupon": "", "coupon_discount": 0, "url": "https://www.tatacliq.com/samsung-galaxy-s25-ultra"},
        ],
    },
    {
        "title": "Boat Airdopes 141 TWS Earbuds with 42H Playtime Black",
        "brand": "Boat",
        "category": "Earbuds",
        "image_url": "https://placehold.co/400x400/0b0f19/f43f5e?text=Boat+Airdopes",
        "description": "Boat Airdopes 141 with ENx noise cancellation, ASAP charge, 42 hours total playtime, IPX4.",
        "specifications": {
            "Type": "TWS In-Ear",
            "Driver": "8mm",
            "Battery": "42 hours total (with case)",
            "Charging": "ASAP Charge (5 min = 90 min)",
            "Noise Cancellation": "ENx (Environmental Noise)",
            "Bluetooth": "5.3",
            "IP Rating": "IPX4",
            "Weight": "42g (with case)",
        },
        "offers": [
            {"store_name": "Amazon", "price": 1299, "mrp": 4490, "rating": 4.1, "reviews": 45670, "delivery_days": 2, "coupon": "", "coupon_discount": 0, "url": "https://www.amazon.in/dp/B0DXYZ1111"},
            {"store_name": "Flipkart", "price": 1199, "mrp": 4490, "rating": 4.0, "reviews": 34560, "delivery_days": 1, "coupon": "BOAT200", "coupon_discount": 200, "url": "https://www.flipkart.com/boat-airdopes-141-black/p/itm1111"},
            {"store_name": "Meesho", "price": 1099, "mrp": 4490, "rating": 3.9, "reviews": 8900, "delivery_days": 4, "coupon": "", "coupon_discount": 0, "url": "https://www.meesho.com/boat-airdopes-141"},
        ],
    },
    {
        "title": "Apple iPad Air M2 11-inch 128GB Wi-Fi Space Gray",
        "brand": "Apple",
        "category": "Tablets",
        "image_url": "https://placehold.co/400x400/0b0f19/3b82f6?text=iPad+Air",
        "description": "Apple iPad Air with M2 chip, 11-inch Liquid Retina display, Touch ID, 10-hour battery.",
        "specifications": {
            "Display": '11" Liquid Retina IPS LCD',
            "Processor": "Apple M2",
            "RAM": "8 GB",
            "Storage": "128 GB",
            "Battery": "Up to 10 hours",
            "Camera": "12MP Wide + 12MP Ultra Wide",
            "Connectivity": "Wi-Fi 6E",
            "Weight": "462g",
        },
        "offers": [
            {"store_name": "Amazon", "price": 59900, "mrp": 64900, "rating": 4.6, "reviews": 3450, "delivery_days": 2, "coupon": "HDFC3000", "coupon_discount": 3000, "url": "https://www.amazon.in/dp/B0DXYZ2222"},
            {"store_name": "Flipkart", "price": 58999, "mrp": 64900, "rating": 4.5, "reviews": 2890, "delivery_days": 1, "coupon": "", "coupon_discount": 0, "url": "https://www.flipkart.com/apple-ipad-air-m2-11inch/p/itm2222"},
            {"store_name": "Croma", "price": 61900, "mrp": 64900, "rating": 4.4, "reviews": 123, "delivery_days": 5, "coupon": "", "coupon_discount": 0, "url": "https://www.croma.com/apple-ipad-air-m2-11"},
            {"store_name": "Reliance Digital", "price": 59900, "mrp": 64900, "rating": 4.5, "reviews": 234, "delivery_days": 3, "coupon": "EXCHANGE4000", "coupon_discount": 4000, "url": "https://www.reliancedigital.in/apple-ipad-air-m2"},
        ],
    },
    {
        "title": "Nike Air Max 270 React Men's Running Shoes Black/White",
        "brand": "Nike",
        "category": "Footwear",
        "image_url": "https://placehold.co/400x400/0b0f19/f59e0b?text=Nike+Air+Max",
        "description": "Nike Air Max 270 React with soft foam, Max Air unit for cushioning, lightweight mesh upper.",
        "specifications": {
            "Type": "Running Shoes",
            "Upper": "Mesh + Synthetic",
            "Sole": "Rubber",
            "Cushioning": "Air Max 270 + React Foam",
            "Closure": "Lace-Up",
            "Weight": "280g (approx)",
            "Gender": "Men",
            "Color": "Black/White",
        },
        "offers": [
            {"store_name": "Amazon", "price": 12995, "mrp": 16995, "rating": 4.3, "reviews": 2340, "delivery_days": 3, "coupon": "NIKE2000", "coupon_discount": 2000, "url": "https://www.amazon.in/dp/B0DXYZ3333"},
            {"store_name": "Flipkart", "price": 11999, "mrp": 16995, "rating": 4.2, "reviews": 1890, "delivery_days": 2, "coupon": "EXTRA1000", "coupon_discount": 1000, "url": "https://www.flipkart.com/nike-air-max-270-react/p/itm3333"},
            {"store_name": "Myntra", "price": 11499, "mrp": 16995, "rating": 4.4, "reviews": 4560, "delivery_days": 3, "coupon": "MYNTRA1500", "coupon_discount": 1500, "url": "https://www.myntra.com/nike-air-max-270-react"},
            {"store_name": "AJIO", "price": 11999, "mrp": 16995, "rating": 4.3, "reviews": 1230, "delivery_days": 4, "coupon": "AJIO2000", "coupon_discount": 2000, "url": "https://www.ajio.com/nike-air-max-270-react"},
        ],
    },
    {
        "title": "LG 55 Inch 4K OLED Smart TV OLED55C4PSA",
        "brand": "LG",
        "category": "TVs",
        "image_url": "https://placehold.co/400x400/0b0f19/06b6d4?text=LG+OLED+TV",
        "description": "LG 55 inch OLED evo 4K TV with a9 Gen7 AI Processor, Dolby Vision & Atmos, webOS 24.",
        "specifications": {
            "Display": '55" OLED evo',
            "Resolution": "4K (3840 x 2160)",
            "Processor": "a9 Gen7 AI Processor",
            "HDR": "Dolby Vision, HDR10, HLG",
            "Audio": "40W, Dolby Atmos",
            "Smart TV": "webOS 24",
            "HDMI": "4x HDMI 2.1",
            "Refresh Rate": "120Hz",
        },
        "offers": [
            {"store_name": "Amazon", "price": 134990, "mrp": 199990, "rating": 4.5, "reviews": 1230, "delivery_days": 5, "coupon": "LG15000", "coupon_discount": 15000, "url": "https://www.amazon.in/dp/B0DXYZ4444"},
            {"store_name": "Flipkart", "price": 129990, "mrp": 199990, "rating": 4.4, "reviews": 980, "delivery_days": 3, "coupon": "HDFC20000", "coupon_discount": 20000, "url": "https://www.flipkart.com/lg-55-inch-4k-oled-tv/p/itm4444"},
            {"store_name": "Croma", "price": 139990, "mrp": 199990, "rating": 4.3, "reviews": 67, "delivery_days": 7, "coupon": "", "coupon_discount": 0, "url": "https://www.croma.com/lg-55-oled-c4"},
            {"store_name": "Reliance Digital", "price": 134990, "mrp": 199990, "rating": 4.4, "reviews": 145, "delivery_days": 5, "coupon": "INSTALL5000", "coupon_discount": 5000, "url": "https://www.reliancedigital.in/lg-55-oled-c4"},
        ],
    },
    {
        "title": "OnePlus 13 5G 256GB Midnight Ocean",
        "brand": "OnePlus",
        "category": "Smartphones",
        "image_url": "https://placehold.co/400x400/0b0f19/f43f5e?text=OnePlus+13",
        "description": "OnePlus 13 with Snapdragon 8 Elite, 50MP Hasselblad camera, 6000mAh battery, 100W SUPERVOOC.",
        "specifications": {
            "Display": '6.82" LTPO AMOLED, 120Hz',
            "Processor": "Snapdragon 8 Elite",
            "RAM": "12 GB",
            "Storage": "256 GB",
            "Camera": "50MP + 50MP + 50MP (Hasselblad)",
            "Battery": "6000 mAh",
            "Charging": "100W SUPERVOOC",
            "OS": "Android 15, OxygenOS 15",
        },
        "offers": [
            {"store_name": "Amazon", "price": 69999, "mrp": 79999, "rating": 4.5, "reviews": 6780, "delivery_days": 2, "coupon": "BANK2000", "coupon_discount": 2000, "url": "https://www.amazon.in/dp/B0DXYZ5555"},
            {"store_name": "Flipkart", "price": 67999, "mrp": 79999, "rating": 4.4, "reviews": 5430, "delivery_days": 1, "coupon": "FLAT5000", "coupon_discount": 5000, "url": "https://www.flipkart.com/oneplus-13-5g-256gb/p/itm5555"},
            {"store_name": "Croma", "price": 71999, "mrp": 79999, "rating": 4.3, "reviews": 234, "delivery_days": 3, "coupon": "", "coupon_discount": 0, "url": "https://www.croma.com/oneplus-13-5g-256gb"},
            {"store_name": "Reliance Digital", "price": 69999, "mrp": 79999, "rating": 4.4, "reviews": 456, "delivery_days": 2, "coupon": "RELIANCE1000", "coupon_discount": 1000, "url": "https://www.reliancedigital.in/oneplus-13"},
        ],
    },
    {
        "title": "JBL Tune 770NC Wireless Over-Ear Headphones Black",
        "brand": "JBL",
        "category": "Headphones",
        "image_url": "https://placehold.co/400x400/0b0f19/3b82f6?text=JBL+770NC",
        "description": "JBL Pure Bass Sound, Adaptive Noise Cancelling, 70-hour battery, lightweight foldable design.",
        "specifications": {
            "Type": "Over-Ear, Wireless",
            "Driver": "40mm",
            "Battery": "70 hours (ANC OFF), 44 hours (ANC ON)",
            "Noise Cancellation": "Adaptive ANC",
            "Bluetooth": "5.3",
            "Weight": "252g",
            "Foldable": "Yes",
            "Multi-Point": "Yes",
        },
        "offers": [
            {"store_name": "Amazon", "price": 5999, "mrp": 9999, "rating": 4.3, "reviews": 12340, "delivery_days": 2, "coupon": "JBL1000", "coupon_discount": 1000, "url": "https://www.amazon.in/dp/B0DXYZ6666"},
            {"store_name": "Flipkart", "price": 5499, "mrp": 9999, "rating": 4.2, "reviews": 9870, "delivery_days": 1, "coupon": "FLAT500", "coupon_discount": 500, "url": "https://www.flipkart.com/jbl-tune-770nc-black/p/itm6666"},
            {"store_name": "Croma", "price": 6499, "mrp": 9999, "rating": 4.1, "reviews": 123, "delivery_days": 3, "coupon": "", "coupon_discount": 0, "url": "https://www.croma.com/jbl-tune-770nc"},
        ],
    },
    {
        "title": "Prestige Iris 750W Mixer Grinder with 3 Jars Black",
        "brand": "Prestige",
        "category": "Kitchen Appliances",
        "image_url": "https://placehold.co/400x400/0b0f19/10b981?text=Prestige+Mixer",
        "description": "Prestige Iris 750W mixer grinder with 3 stainless steel jars, vacuum suction base, 3-speed control.",
        "specifications": {
            "Power": "750W",
            "Jars": "3 (Liquidizing, Dry Grinding, Chutney)",
            "Jar Material": "Stainless Steel",
            "Speed": "3 Speed + Pulse",
            "Motor": "Copper Winding",
            "Base": "Vacuum Suction",
            "Warranty": "2 Years",
            "Blade": "Stainless Steel",
        },
        "offers": [
            {"store_name": "Amazon", "price": 2499, "mrp": 5495, "rating": 4.2, "reviews": 23450, "delivery_days": 2, "coupon": "", "coupon_discount": 0, "url": "https://www.amazon.in/dp/B0DXYZ7777"},
            {"store_name": "Flipkart", "price": 2299, "mrp": 5495, "rating": 4.1, "reviews": 18900, "delivery_days": 1, "coupon": "FLAT300", "coupon_discount": 300, "url": "https://www.flipkart.com/prestige-iris-750w/p/itm7777"},
            {"store_name": "Meesho", "price": 2199, "mrp": 5495, "rating": 4.0, "reviews": 5670, "delivery_days": 5, "coupon": "", "coupon_discount": 0, "url": "https://www.meesho.com/prestige-iris-750w"},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed demo products across 8 platforms for comparison testing"

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo products...")

        platforms = {}
        for p in Platform.objects.all():
            platforms[p.name] = p

        Product.objects.all().delete()

        for data in DEMO_PRODUCTS:
            product = Product.objects.create(
                title=data["title"],
                brand=data["brand"],
                category=data["category"],
                image_url=data.get("image_url", ""),
                description=data.get("description", ""),
                specifications=data.get("specifications", {}),
            )

            for offer_data in data["offers"]:
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
                    data_source="demo",
                )

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

        products = Product.objects.count()
        offers = ProductOffer.objects.count()
        history = PriceHistory.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Seeded {products} products, {offers} offers, {history} price history records"
        ))
