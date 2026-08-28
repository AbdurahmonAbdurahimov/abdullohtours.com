from decimal import Decimal

from django.core.management.base import BaseCommand

from apps.core.models import ExchangeRate

CURRENCIES = ["EUR", "GBP", "UZS"]


def fetch_rates() -> dict[str, Decimal]:
    """Fetch current USD -> {EUR, GBP, UZS} rates from an external FX API.

    TODO: wire up a real FX API call (e.g. exchangerate.host, openexchangerates.org)
    once an API key/provider is chosen. Returning a fixed fallback table for
    now so the pluggable structure (fetch -> cache in DB) is in place and
    testable without a network call.
    """
    return {
        "EUR": Decimal("0.92"),
        "GBP": Decimal("0.79"),
        "UZS": Decimal("12700"),
    }


class Command(BaseCommand):
    help = "Refresh cached USD -> EUR/GBP/UZS exchange rates. Run daily via cron (03:00)."

    def handle(self, *args, **options):
        rates = fetch_rates()
        updated = 0
        for currency in CURRENCIES:
            rate = rates.get(currency)
            if rate is None:
                self.stderr.write(self.style.WARNING(f"No rate returned for {currency}, skipping."))
                continue
            ExchangeRate.objects.update_or_create(
                currency=currency, defaults={"rate_from_usd": rate}
            )
            updated += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {updated} exchange rate(s)."))
