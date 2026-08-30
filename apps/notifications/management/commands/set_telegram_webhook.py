"""
Registers (or clears, or inspects) this bot's webhook with Telegram —
the one-time setup step that tells Telegram where to POST updates, so
apps/notifications/telegram_bot.telegram_webhook actually receives anything
(CLAUDE.md §8: webhook mode, no polling).

Usage:
    # Production: point Telegram at CANONICAL_HOST + TELEGRAM_WEBHOOK_SECRET.
    python manage.py set_telegram_webhook

    # Local dev via a tunnel (Telegram requires public HTTPS, not localhost).
    python manage.py set_telegram_webhook --url https://abc123.ngrok-free.app

    # Diagnostics: show what Telegram currently has on file, change nothing.
    python manage.py set_telegram_webhook --info

    # Stop deliveries (e.g. before tearing down a dev tunnel).
    python manage.py set_telegram_webhook --delete
"""

from __future__ import annotations

import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError, CommandParser

from apps.notifications.telegram_bot import get_bot

_PLACEHOLDER_TOKEN_MARKERS = ("your-bot-token", "local-dev-placeholder")


class Command(BaseCommand):
    help = "Register, clear, or inspect this bot's webhook registration with Telegram."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--url",
            help=(
                "Base URL to register (e.g. an ngrok/cloudflared tunnel for local "
                "testing). Defaults to CANONICAL_HOST. The command appends "
                "/tg/webhook/<TELEGRAM_WEBHOOK_SECRET>/ itself — pass the bare origin."
            ),
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Remove the current webhook instead of setting one.",
        )
        parser.add_argument(
            "--info",
            action="store_true",
            help="Print Telegram's current webhook info and exit — makes no changes.",
        )

    def handle(self, *args, **options):
        token = settings.TELEGRAM_BOT_TOKEN
        if not token or any(marker in token for marker in _PLACEHOLDER_TOKEN_MARKERS):
            raise CommandError(
                "TELEGRAM_BOT_TOKEN is unset or still the local-dev placeholder — "
                "put a real token from @BotFather in .env first."
            )

        bot = get_bot()

        if options["info"]:
            info = asyncio.run(bot.get_webhook_info())
            self.stdout.write(f"URL: {info.url or '(none registered)'}")
            self.stdout.write(f"Pending update count: {info.pending_update_count}")
            if info.last_error_message:
                self.stdout.write(
                    self.style.WARNING(
                        f"Last error: {info.last_error_message} (at {info.last_error_date})"
                    )
                )
            return

        if options["delete"]:
            asyncio.run(bot.delete_webhook())
            self.stdout.write(self.style.SUCCESS("Webhook deleted."))
            return

        secret = settings.TELEGRAM_WEBHOOK_SECRET
        if not secret or secret == "change-me":
            raise CommandError(
                "TELEGRAM_WEBHOOK_SECRET is unset or still the default 'change-me' — "
                "put a real random value in .env first (it's the secret path segment "
                "that authenticates incoming webhook calls)."
            )

        base_url = (options["url"] or settings.CANONICAL_HOST).rstrip("/")
        if not base_url.startswith("https://"):
            raise CommandError(
                f"'{base_url}' is not an https:// URL — Telegram will refuse it "
                "(it never calls plain http, and never calls localhost)."
            )

        webhook_url = f"{base_url}/tg/webhook/{secret}/"
        asyncio.run(bot.set_webhook(url=webhook_url))
        self.stdout.write(self.style.SUCCESS(f"Webhook registered: {webhook_url}"))
