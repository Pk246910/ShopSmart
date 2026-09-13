import os
import time
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from products.models import Product

PEXELS_API_KEY = os.environ.get('PEXELS_API_KEY', '')


class Command(BaseCommand):
    help = 'Fetch real product images from Pexels'

    def add_arguments(self, parser):
        parser.add_argument('--api-key', type=str, help='Pexels API key')

    def handle(self, *args, **options):
        api_key = options.get('api_key') or PEXELS_API_KEY
        if not api_key:
            self.stderr.write('No Pexels API key. Set PEXELS_API_KEY env var or use --api-key')
            self.stderr.write('Get free key at: https://www.pexels.com/api/')
            return

        products = Product.objects.filter(image_url__contains='placehold.co')
        total = products.count()
        self.stdout.write(f'Found {total} products with placeholder images')

        updated = 0
        failed = 0
        headers = {'Authorization': api_key}

        for i, product in enumerate(products):
            query = f'{product.brand} {product.title}'
            self.stdout.write(f'[{i+1}/{total}] Searching: {query[:60]}...')

            try:
                resp = requests.get(
                    'https://api.pexels.com/v1/search',
                    headers=headers,
                    params={'query': query, 'per_page': 3, 'orientation': 'square'},
                    timeout=10,
                )

                if resp.status_code == 429:
                    self.stdout.write(self.style.WARNING('  -> Rate limited, waiting 15s...'))
                    time.sleep(15)
                    continue

                resp.raise_for_status()
                data = resp.json()
                photos = data.get('photos', [])

                if photos:
                    image_url = photos[0]['src']['medium']
                    product.image_url = image_url
                    product.save(update_fields=['image_url'])
                    updated += 1
                    self.stdout.write(self.style.SUCCESS(f'  -> Found image'))
                else:
                    failed += 1
                    self.stdout.write(self.style.WARNING(f'  -> No results'))

                time.sleep(1.5)

            except Exception as e:
                failed += 1
                self.stdout.write(self.style.ERROR(f'  -> Error: {e}'))
                time.sleep(2)

        self.stdout.write(self.style.SUCCESS(f'\nDone: {updated} updated, {failed} failed'))
