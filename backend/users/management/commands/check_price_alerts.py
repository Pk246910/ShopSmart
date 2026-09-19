import logging
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import PriceAlert
from products.models import ProductOffer

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Check price alerts and send emails when target price is reached"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run", action="store_true",
            help="Show what would be processed without sending emails",
        )

    def handle(self, *args, **options):
        dry_run = options.get("dry_run", False)
        active_alerts = PriceAlert.objects.filter(active=True).select_related("user", "product")

        self.stdout.write(f"Checking {active_alerts.count()} active price alerts...")

        triggered_count = 0
        emailed_count = 0

        for alert in active_alerts:
            product = alert.product

            best_offer = ProductOffer.objects.filter(
                product=product, in_stock=True
            ).order_by("current_price").first()

            if not best_offer:
                continue

            current_price = best_offer.current_price

            if current_price <= alert.target_price:
                triggered_count += 1
                self.stdout.write(
                    f"  TRIGGERED: {product.title[:50]} | "
                    f"Current: ₹{current_price} | Target: ₹{alert.target_price} | "
                    f"Platform: {best_offer.store_name}"
                )

                if not alert.email_sent:
                    if dry_run:
                        self.stdout.write(f"    (dry-run) Would send email to {alert.user.email if alert.user else 'no user'}")
                    else:
                        from users.services.email_service import send_price_alert_email
                        sent = send_price_alert_email(alert, current_price)
                        if sent:
                            alert.email_sent = True
                            alert.email_sent_at = timezone.now()
                            alert.save(update_fields=["email_sent", "email_sent_at"])
                            emailed_count += 1
                            self.stdout.write(f"    Email sent to {alert.user.email}")
                        else:
                            self.stdout.write(f"    Email failed for {alert.user.email if alert.user else 'unknown'}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. {triggered_count} alerts triggered, {emailed_count} emails sent."
        ))
