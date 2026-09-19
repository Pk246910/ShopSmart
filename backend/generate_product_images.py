#!/usr/bin/env python
"""
Generate SVG product images for all predefined products and update DB image_url.
Run: python generate_product_images.py
"""
import os
import re
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from products.models import Product

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'public', 'products')

# Category color schemes: (bg_color, accent_color, icon_color)
CATEGORY_COLORS = {
    'Smartphones': ('#0f172a', '#06b6d4', '#22d3ee'),
    'Laptops': ('#0f172a', '#10b981', '#34d399'),
    'Headphones': ('#0f172a', '#8b5cf6', '#a78bfa'),
    'Earbuds': ('#0f172a', '#f43f5e', '#fb7185'),
    'Tablets': ('#0f172a', '#3b82f6', '#60a5fa'),
    'TVs': ('#0f172a', '#06b6d4', '#22d3ee'),
    'Footwear': ('#0f172a', '#f59e0b', '#fbbf24'),
    'Watches': ('#0f172a', '#ec4899', '#f472b6'),
    'Kitchen Appliances': ('#0f172a', '#10b981', '#34d399'),
    'Cameras': ('#0f172a', '#f97316', '#fb923c'),
    'Fashion': ('#0f172a', '#6366f1', '#818cf8'),
}

# SVG icon paths for each category
CATEGORY_ICONS = {
    'Smartphones': '''<rect x="148" y="80" width="104" height="180" rx="16" fill="none" stroke="{accent}" stroke-width="4"/>
      <rect x="156" y="96" width="88" height="140" rx="4" fill="{accent}" opacity="0.15"/>
      <circle cx="200" cy="248" r="8" fill="none" stroke="{accent}" stroke-width="2"/>
      <rect x="180" y="86" width="40" height="4" rx="2" fill="{accent}" opacity="0.5"/>''',

    'Laptops': '''<rect x="110" y="100" width="180" height="110" rx="8" fill="none" stroke="{accent}" stroke-width="4"/>
      <rect x="118" y="108" width="164" height="86" rx="4" fill="{accent}" opacity="0.15"/>
      <path d="M90 210 L110 210 L290 210 L310 210 L300 220 L100 220 Z" fill="none" stroke="{accent}" stroke-width="3"/>''',

    'Headphones': '''<path d="M140 180 Q140 110 200 110 Q260 110 260 180" fill="none" stroke="{accent}" stroke-width="6" stroke-linecap="round"/>
      <rect x="124" y="170" width="32" height="50" rx="10" fill="{accent}" opacity="0.3" stroke="{accent}" stroke-width="3"/>
      <rect x="244" y="170" width="32" height="50" rx="10" fill="{accent}" opacity="0.3" stroke="{accent}" stroke-width="3"/>''',

    'Earbuds': '''<ellipse cx="170" cy="180" rx="28" ry="30" fill="{accent}" opacity="0.2" stroke="{accent}" stroke-width="3"/>
      <ellipse cx="230" cy="180" rx="28" ry="30" fill="{accent}" opacity="0.2" stroke="{accent}" stroke-width="3"/>
      <circle cx="170" cy="178" r="8" fill="{accent}" opacity="0.5"/>
      <circle cx="230" cy="178" r="8" fill="{accent}" opacity="0.5"/>
      <path d="M170 210 Q170 240 160 260" fill="none" stroke="{accent}" stroke-width="2" opacity="0.4"/>
      <path d="M230 210 Q230 240 240 260" fill="none" stroke="{accent}" stroke-width="2" opacity="0.4"/>''',

    'Tablets': '''<rect x="130" y="80" width="140" height="190" rx="12" fill="none" stroke="{accent}" stroke-width="4"/>
      <rect x="140" y="92" width="120" height="160" rx="4" fill="{accent}" opacity="0.15"/>
      <circle cx="200" cy="264" r="4" fill="{accent}" opacity="0.5"/>''',

    'TVs': '''<rect x="90" y="100" width="220" height="130" rx="8" fill="none" stroke="{accent}" stroke-width="4"/>
      <rect x="98" y="108" width="204" height="110" rx="4" fill="{accent}" opacity="0.12"/>
      <line x1="200" y1="230" x2="200" y2="250" stroke="{accent}" stroke-width="4"/>
      <line x1="160" y1="250" x2="240" y2="250" stroke="{accent}" stroke-width="4" stroke-linecap="round"/>''',

    'Footwear': '''<path d="M110 200 Q110 170 140 160 L260 155 Q290 153 295 170 L300 195 Q302 210 290 215 L120 220 Q110 220 110 200Z" fill="{accent}" opacity="0.15" stroke="{accent}" stroke-width="3"/>
      <path d="M140 160 L140 140 Q145 125 160 125 L170 125" fill="none" stroke="{accent}" stroke-width="2" opacity="0.4"/>
      <circle cx="250" cy="185" r="15" fill="none" stroke="{accent}" stroke-width="2" opacity="0.3"/>''',

    'Watches': '''<circle cx="200" cy="175" r="55" fill="none" stroke="{accent}" stroke-width="4"/>
      <circle cx="200" cy="175" r="45" fill="{accent}" opacity="0.1"/>
      <line x1="200" y1="175" x2="200" y2="145" stroke="{accent}" stroke-width="3" stroke-linecap="round"/>
      <line x1="200" y1="175" x2="222" y2="185" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>
      <rect x="190" y="108" width="20" height="12" rx="3" fill="none" stroke="{accent}" stroke-width="2"/>
      <rect x="190" y="230" width="20" height="12" rx="3" fill="none" stroke="{accent}" stroke-width="2"/>''',

    'Kitchen Appliances': '''<rect x="155" y="100" width="90" height="130" rx="10" fill="none" stroke="{accent}" stroke-width="4"/>
      <rect x="140" y="230" width="120" height="20" rx="6" fill="none" stroke="{accent}" stroke-width="3"/>
      <rect x="175" y="80" width="50" height="20" rx="4" fill="none" stroke="{accent}" stroke-width="2"/>
      <line x1="175" y1="140" x2="225" y2="140" stroke="{accent}" stroke-width="2" opacity="0.4"/>
      <line x1="175" y1="160" x2="225" y2="160" stroke="{accent}" stroke-width="2" opacity="0.4"/>''',

    'Cameras': '''<rect x="120" y="110" width="160" height="110" rx="10" fill="none" stroke="{accent}" stroke-width="4"/>
      <circle cx="200" cy="165" r="35" fill="{accent}" opacity="0.12" stroke="{accent}" stroke-width="3"/>
      <circle cx="200" cy="165" r="22" fill="none" stroke="{accent}" stroke-width="2"/>
      <circle cx="200" cy="165" r="10" fill="{accent}" opacity="0.3"/>
      <rect x="240" y="115" width="30" height="16" rx="4" fill="{accent}" opacity="0.2"/>
      <rect x="135" y="100" width="40" height="14" rx="4" fill="{accent}" opacity="0.2"/>''',

    'Fashion': '''<path d="M160 120 L200 100 L240 120 L260 140 L240 150 L235 260 L165 260 L160 150 L140 140 Z" fill="{accent}" opacity="0.12" stroke="{accent}" stroke-width="3"/>
      <line x1="200" y1="100" x2="200" y2="260" stroke="{accent}" stroke-width="1.5" opacity="0.3"/>
      <path d="M160 120 L200 140 L240 120" fill="none" stroke="{accent}" stroke-width="2" opacity="0.5"/>''',
}


def slugify(title):
    """Create a URL-safe filename slug from product title."""
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s]+', '-', slug.strip())
    slug = re.sub(r'-+', '-', slug)
    # Truncate to reasonable length
    return slug[:80].rstrip('-')


def get_brand_initial(brand):
    """Get first letter of brand for display."""
    return brand[0].upper() if brand else '?'


def generate_svg(title, brand, category):
    """Generate an SVG product image."""
    bg, accent, icon_color = CATEGORY_COLORS.get(category, ('#0f172a', '#06b6d4', '#22d3ee'))
    icon = CATEGORY_ICONS.get(category, CATEGORY_ICONS['Smartphones'])

    # Format brand and short title for display
    brand_display = brand.upper() if brand else ''
    # Use first 2-3 words of title as product label
    words = title.split()
    short_title = ' '.join(words[:4]) if len(words) > 4 else title
    if len(short_title) > 35:
        short_title = short_title[:32] + '...'

    # Escape XML special characters
    def esc(s):
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 350" width="400" height="350">
  <defs>
    <linearGradient id="bg_{category.replace(' ', '_')}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{bg};stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#1e293b;stop-opacity:1"/>
    </linearGradient>
    <linearGradient id="glow_{category.replace(' ', '_')}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{accent};stop-opacity:0.08"/>
      <stop offset="100%" style="stop-color:{accent};stop-opacity:0.02"/>
    </linearGradient>
    <filter id="shadow_{category.replace(' ', '_')}">
      <feDropShadow dx="0" dy="2" stdDeviation="4" flood-color="{accent}" flood-opacity="0.15"/>
    </filter>
  </defs>

  <!-- Background -->
  <rect width="400" height="350" rx="12" fill="url(#bg_{category.replace(' ', '_')})"/>
  <rect width="400" height="350" rx="12" fill="url(#glow_{category.replace(' ', '_')})"/>

  <!-- Subtle grid pattern -->
  <g opacity="0.03" stroke="{accent}" stroke-width="0.5">
    <line x1="0" y1="50" x2="400" y2="50"/><line x1="0" y1="100" x2="400" y2="100"/>
    <line x1="0" y1="150" x2="400" y2="150"/><line x1="0" y1="200" x2="400" y2="200"/>
    <line x1="0" y1="250" x2="400" y2="250"/><line x1="0" y1="300" x2="400" y2="300"/>
    <line x1="50" y1="0" x2="50" y2="350"/><line x1="100" y1="0" x2="100" y2="350"/>
    <line x1="150" y1="0" x2="150" y2="350"/><line x1="200" y1="0" x2="200" y2="350"/>
    <line x1="250" y1="0" x2="250" y2="350"/><line x1="300" y1="0" x2="300" y2="350"/>
    <line x1="350" y1="0" x2="350" y2="350"/>
  </g>

  <!-- Category icon -->
  <g filter="url(#shadow_{category.replace(' ', '_')})">
    {icon.format(accent=accent)}
  </g>

  <!-- Brand name -->
  <text x="200" y="50" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="13" font-weight="700" fill="{accent}" letter-spacing="3" opacity="0.9">{esc(brand_display)}</text>

  <!-- Product name -->
  <text x="200" y="300" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="11" font-weight="500" fill="#94a3b8" opacity="0.8">{esc(short_title)}</text>

  <!-- Category badge -->
  <rect x="200" y="318" x="-60" width="120" height="20" rx="10" fill="{accent}" opacity="0.1" transform="translate(140, 318)"/>
  <text x="200" y="332" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="9" font-weight="600" fill="{accent}" opacity="0.7">{esc(category.upper())}</text>

  <!-- ShopSmart branding -->
  <text x="200" y="22" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="8" font-weight="400" fill="#475569" opacity="0.4">SHOPSMART</text>
</svg>'''
    return svg


def generate_placeholder():
    """Generate a generic ShopSmart product placeholder SVG."""
    return '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 350" width="400" height="350">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f172a;stop-opacity:1"/>
      <stop offset="100%" style="stop-color:#1e293b;stop-opacity:1"/>
    </linearGradient>
  </defs>
  <rect width="400" height="350" rx="12" fill="url(#bg)"/>
  <g opacity="0.06" stroke="#06b6d4" stroke-width="0.5">
    <line x1="0" y1="50" x2="400" y2="50"/><line x1="0" y1="100" x2="400" y2="100"/>
    <line x1="0" y1="150" x2="400" y2="150"/><line x1="0" y1="200" x2="400" y2="200"/>
    <line x1="0" y1="250" x2="400" y2="250"/><line x1="0" y1="300" x2="400" y2="300"/>
    <line x1="50" y1="0" x2="50" y2="350"/><line x1="100" y1="0" x2="100" y2="350"/>
    <line x1="150" y1="0" x2="150" y2="350"/><line x1="200" y1="0" x2="200" y2="350"/>
    <line x1="250" y1="0" x2="250" y2="350"/><line x1="300" y1="0" x2="300" y2="350"/>
    <line x1="350" y1="0" x2="350" y2="350"/>
  </g>
  <rect x="155" y="110" width="90" height="120" rx="10" fill="none" stroke="#06b6d4" stroke-width="3" opacity="0.3"/>
  <line x1="155" y1="170" x2="245" y2="170" stroke="#06b6d4" stroke-width="1" opacity="0.2"/>
  <text x="200" y="185" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="24" fill="#06b6d4" opacity="0.3">&#x1F4E6;</text>
  <text x="200" y="300" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="12" font-weight="500" fill="#64748b" opacity="0.5">No Image Available</text>
  <text x="200" y="22" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="8" font-weight="400" fill="#475569" opacity="0.4">SHOPSMART</text>
  <rect x="140" y="315" width="120" height="20" rx="10" fill="#06b6d4" opacity="0.08"/>
  <text x="200" y="329" text-anchor="middle" font-family="system-ui, -apple-system, sans-serif" font-size="9" font-weight="600" fill="#06b6d4" opacity="0.5">PRODUCT</text>
</svg>'''


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Generate placeholder
    placeholder_path = os.path.join(OUTPUT_DIR, 'product-placeholder.svg')
    with open(placeholder_path, 'w', encoding='utf-8') as f:
        f.write(generate_placeholder())
    print(f"Created: product-placeholder.svg")

    products = Product.objects.all().order_by('id')
    updated = 0

    for product in products:
        slug = slugify(product.title)
        filename = f"{slug}.svg"
        filepath = os.path.join(OUTPUT_DIR, filename)

        svg = generate_svg(product.title, product.brand or '', product.category or '')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(svg)

        new_url = f"/products/{filename}"
        if product.image_url != new_url:
            product.image_url = new_url
            product.save(update_fields=['image_url'])
            updated += 1

        print(f"  {product.id}: {filename}")

    print(f"\nDone! Generated {products.count()} SVGs, updated {updated} image_url fields")
    print(f"Files saved to: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
