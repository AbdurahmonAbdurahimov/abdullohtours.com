"""
Takes a Notification row and actually sends it via the Telegram bot, marking
SENT/FAILED and incrementing attempts. A Notification is never deleted on
failure — cron's send_pending_notifications retries PENDING/FAILED rows
(CLAUDE.md §8/§9).

Expected `Notification.payload` shapes:
    {"text": str, "chat_ids": [str, ...]}                       -> plain message
    {"text": str, "chat_ids": [...], "reply_markup": {...}}     -> message + inline keyboard (dict form of InlineKeyboardMarkup.to_dict())
    {"document_path": str, "caption": str, "chat_ids": [...]}   -> send a file (e.g. DB backup)
If chat_ids is omitted, we fan out to every active TelegramAdmin filtered by
the `audience` key ("bookings" -> receives_bookings, "reminders" ->
receives_reminders, anything else / omitted -> all active admins).
"""

from __future__ import annotations

import asyncio
import logging

from django.utils import timezone
from telegram import Bot, InlineKeyboardMarkup

from .models import Notification, TelegramAdmin

logger = logging.getLogger(__name__)


def _resolve_chat_ids(notification: Notification) -> list[str]:
    payload = notification.payload or {}
    if payload.get("chat_ids"):
        return list(payload["chat_ids"])

    audience = payload.get("audience")
    qs = TelegramAdmin.objects.filter(is_active=True)
    if audience == "bookings":
        qs = qs.filter(receives_bookings=True)
    elif audience == "reminders":
        qs = qs.filter(receives_reminders=True)
    return list(qs.values_list("chat_id", flat=True))


async def _send_one(bot: Bot, notification: Notification, chat_id: str) -> None:
    payload = notification.payload or {}
    if payload.get("document_path"):
        with open(payload["document_path"], "rb") as fh:
            await bot.send_document(
                chat_id=chat_id, document=fh, caption=payload.get("caption", "")
            )
        return

    reply_markup = None
    if payload.get("reply_markup"):
        reply_markup = InlineKeyboardMarkup.de_json(payload["reply_markup"], bot)

    await bot.send_message(chat_id=chat_id, text=payload.get("text", ""), reply_markup=reply_markup)


async def _send_all(notification: Notification, chat_ids: list[str]) -> None:
    from django.conf import settings

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    for chat_id in chat_ids:
        await _send_one(bot, notification, chat_id)


def send_notification(notification: Notification) -> bool:
    """Send a single Notification. Returns True on success.

    Mutates and saves `notification` with the outcome (status/attempts/
    last_error/sent_at) regardless of success or failure.
    """
    notification.attempts += 1
    chat_ids = _resolve_chat_ids(notification)

    if not chat_ids:
        notification.status = Notification.Status.FAILED
        notification.last_error = "No active TelegramAdmin recipients resolved."
        notification.save(update_fields=["status", "last_error", "attempts"])
        return False

    try:
        asyncio.run(_send_all(notification, chat_ids))
    except Exception as exc:  # noqa: BLE001 - any Telegram/network failure lands here
        logger.exception("Failed to send Notification #%s", notification.pk)
        notification.status = Notification.Status.FAILED
        notification.last_error = str(exc)
        notification.save(update_fields=["status", "last_error", "attempts"])
        return False

    notification.status = Notification.Status.SENT
    notification.sent_at = timezone.now()
    notification.last_error = ""
    notification.save(update_fields=["status", "sent_at", "last_error", "attempts"])
    return True
