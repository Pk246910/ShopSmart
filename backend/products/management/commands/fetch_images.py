import time
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Product

try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None


class Command(BaseCommand):
    help = 'Fetch real product images from DuckDuckGo'

    def handle(self, *args, **options):
        if DDGS is None:
            self.stderr.write('duckduckgo-search not installed')
            return

        products = Product.objects.filter(image_url__contains='placehold.co')
        total = products.count()
        self.stdout.write(f'Found {total} products with placeholder images')

        updated = 0
        failed = 0

        for i, product in enumerate(products):
            query = f'{product.brand} {product.title} product image'
            self.stdout.write(f'[{i+1}/{total}] Searching: {query[:60]}...')

            try:
                with DDGS() as ddgs:
                    results = list(ddgs.images(query, max_results=5, region='in-en'))

                image_url = None
                for r in results:
                    url = r.get('image', '')
                    if url and 'placehold' not in url and 'logo' not in url.lower():
                        image_url = url
                        break

                if image_url:
                    product.image_url = image_url
                    product.save(update_fields=['image_url'])
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f'  -> Found image'))
                else:
                    failed += 1
                    self.stdout.write(self.style.WARNING(f'  -> No image found'))

                time.sleep(1)

            except Exception as e:
                failed += 1
                self.stdout.write(self.style.ERROR(f'  -> Error: {e}'))
                time.sleep(2)

        self.stdout.write(self.style.SUCCESS(f'\nDone: {updated} updated, {failed} failed'))
