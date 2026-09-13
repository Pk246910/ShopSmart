"""Fetch real product images using Google Custom Search API + Gemini-generated queries.

Setup (free, ~5 min):
  1. Create API key: https://console.cloud.google.com/apis/credentials
     (enable "Custom Search API" for the project)
  2. Create search engine: https://programmablesearchengine.google.com/
     (enable "Image search", set "Search the entire web")
  3. Set env vars (backend/.env):
       GOOGLE_API_KEY=your_key
       GOOGLE_CX=your_engine_id
  4. Run: python manage.py fetch_images_google

Without keys it falls back to Gemini-query + Bing scraping.
"""
import os
import re
import time
import urllib.parse
import requests
from django.core.management.base import BaseCommand
from products.models import Product

GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY', '')
GOOGLE_CX = os.environ.get('GOOGLE_CX', '')

BAD = ['placehold', 'youtube', 'ytimg', 'duitang', 'zoo.org', 'logosmarcas',
       'brandslogos', 'marvel.church', 'whatamysays', 'nicenews', 'philadelphiazoo',
       'newsshooter', 'blogspot', 'alamy', 'shopify', 'logo', 'logos', 'emblem',
       'springbankpetresort', 'monasteryicons', 'talibsinstitute', 'coindesk',
       'facts.net', 'partner.ed2go', 'auto-planet', 'bhaktibhava', 'miaobi-lite',
       'alwayssavors', 'freedomperformexhaust', 'softboxkit', 'tntsports',
       'hindustantimes', 'pw.live', 'ecoustics', 'alicdn', 'gettyimages',
       'mashable', 'imgresizer', 'myfigurecollection', 'ftcdn.net', 'rawpixel',
       'laptopmedia', 'toppng', 'digitalhealthnews', 'coindesk', 'sanity.io',
       'map-', 'landmark', 'temple', 'balaji', 'spider-man', 'puma_sage',
       'noise-pollution', 'sugarloaf', 'mountain', 'church', 'lacoste']

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}


def is_bad(url):
    return (not url) or any(d in (url or '').lower() for d in BAD)


def gemini_query(product):
    """Use Gemini to craft a precise image-search query for this product."""
    try:
        from products.services.gemini_service import GeminiService
        svc = GeminiService()
        msg = (
            'Return ONLY a short web image-search query (max 10 words, no quotes) '
            'that would find an official product photo (white background, buy online) for: '
            '"%s" by %s (%s). Example: Samsung Galaxy S24 Ultra titanium black product photo buy online'
            % (product.title, product.brand, product.category)
        )
        q = svc.chat(msg)
        q = (q or '').strip().strip('"').strip("'").split('\n')[0][:120]
        return q or '%s %s product photo' % (product.brand, product.title)
    except Exception:
        return '%s %s product photo' % (product.brand, product.title)


def google_images(query, api_key, cx, num=5):
    """Google Custom Search API image search. Returns list of image URLs."""
    try:
        resp = requests.get(
            'https://www.googleapis.com/customsearch/v1',
            params={'key': api_key, 'cx': cx, 'q': query, 'searchType': 'image',
                    'num': min(num, 10), 'safe': 'active'},
            timeout=15)
        if resp.status_code != 200:
            return []
        return [i.get('link', '') for i in resp.json().get('items', [])]
    except Exception:
        return []


def bing_images(query, num=5):
    try:
        url = 'https://www.bing.com/images/search?q=%s&first=1' % urllib.parse.quote(query)
        resp = requests.get(url, headers=HEADERS, timeout=10)
        murls = re.findall(r'murl&quot;:&quot;(https?://[^&]+\.(?:jpg|jpeg|png|webp))', resp.text)
        return list(dict.fromkeys(murls))[:num]
    except Exception:
        return []


def valid_image(url):
    if is_bad(url):
        return False
    try:
        r = requests.head(url, headers=HEADERS, timeout=8, allow_redirects=True)
        if r.status_code >= 400:
            return False
        ct = r.headers.get('Content-Type', '')
        return (not ct) or ('image' in ct)
    except Exception:
        return False


class Command(BaseCommand):
    help = 'Fetch real product images via Google Custom Search + Gemini queries'

    def handle(self, *args, **options):
        targets = [p for p in Product.objects.all().order_by('id') if is_bad(p.image_url)]
        self.stdout.write('Products needing images: %d (google=%s)' % (
            len(targets), 'yes' if (GOOGLE_API_KEY and GOOGLE_CX) else 'no-keys-fallback-bing'))

        updated = 0
        for i, p in enumerate(targets):
            query = gemini_query(p)
            self.stdout.write('[%d/%d] %s' % (i + 1, len(targets), query[:70]))
            urls = []
            if GOOGLE_API_KEY and GOOGLE_CX:
                urls = google_images(query, GOOGLE_API_KEY, GOOGLE_CX)
            if not urls:
                urls = bing_images(query)
                time.sleep(1)
            picked = next((u for u in urls if valid_image(u)), None)
            if picked:
                p.image_url = picked
                p.save(update_fields=['image_url'])
                updated += 1
                self.stdout.write(self.style.SUCCESS('  -> %s' % picked[:70]))
            else:
                self.stdout.write(self.style.WARNING('  -> no valid image'))
            time.sleep(1.5)

        self.stdout.write(self.style.SUCCESS('Done: %d/%d updated' % (updated, len(targets))))
