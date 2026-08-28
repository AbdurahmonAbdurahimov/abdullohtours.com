"""
Telegram bot: plain Django webhook view, no separate process/polling
(CLAUDE.md §8). Uses python-telegram-bot in webhook mode — an incoming
Telegram update is POSTed by Telegram to /tg/webhook/<secret>/, parsed with
Update.de_json(), and handled synchronously (python-telegram-bot's Bot
methods are async in v20+, so we drive them with asyncio.run() from this
plain Django view rather than pulling in a whole Application/dispatcher).

Auth: only chat IDs present in TelegramAdmin are served; everything else is
ignored silently (CLAUDE.md §8).
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import timedelta

from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update

from apps.bookings.models import BookingRequest

from .models import TelegramAdmin

logger = logging.getLogger(__name__)


def get_bot() -> Bot:
    return Bot(token=settings.TELEGRAM_BOT_TOKEN)


# ---------------------------------------------------------------------------
# Message formatting
# ---------------------------------------------------------------------------

_COUNTRY_FLAG_UNKNOWN = "🌍"


def format_new_booking_message(booking: BookingRequest, availability: dict | None = None) -> str:
    """Renders the exact template shape from CLAUDE.md §8."""
    date_range = ""
    if booking.start_date and booking.end_date:
        date_range = f"{booking.start_date:%d %b} – {booking.end_date:%d %b %Y}"

    destinations = ""
    if booking.package_id:
        destinations = booking.package.title

    lines = [
        f"🆕 NEW REQUEST  #{booking.ref_code}",
        "",
        f"👤 {booking.full_name} · {_COUNTRY_FLAG_UNKNOWN} {booking.country or 'Unknown'}",
    ]
    if date_range:
        lines.append(
            f"📅 {date_range} · {booking.adults} adults"
            + (f", {booking.children} children" if booking.children else "")
        )
    if booking.vehicle_class_id:
        lines.append(f"🚗 {booking.vehicle_class.name}")
    if destinations:
        lines.append(f"🗺 {destinations}")
    if booking.estimated_total_usd:
        lines.append(f"💰 Estimated: ${booking.estimated_total_usd:,.0f}")

    lines.append("")
    if booking.phone or booking.whatsapp:
        lines.append(f"📱 {booking.whatsapp or booking.phone}")
    lines.append(f"✉️ {booking.email}")

    if availability and availability.get("limited"):
        lines.append("")
        lines.append(
            f"⚠️ {booking.start_date}: {availability['booked']}/{availability['fleet_size']} vehicles booked"
        )

    return "\n".join(lines)


def build_booking_keyboard(booking: BookingRequest) -> InlineKeyboardMarkup:
    admin_url = f"{settings.CANONICAL_HOST}/admin/bookings/bookingrequest/{booking.pk}/change/"
    buttons = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm:{booking.ref_code}"),
            InlineKeyboardButton("💬 Contacted", callback_data=f"contacted:{booking.ref_code}"),
        ],
        [
            InlineKeyboardButton("❌ Reject", callback_data=f"reject:{booking.ref_code}"),
            InlineKeyboardButton("🔗 Open in admin", url=admin_url),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


_CALLBACK_STATUS_MAP = {
    "confirm": BookingRequest.Status.CONFIRMED,
    "contacted": BookingRequest.Status.CONTACTED,
    "reject": BookingRequest.Status.CANCELLED,
}


# ---------------------------------------------------------------------------
# Bot commands
# ---------------------------------------------------------------------------


def cmd_today() -> str:
    today = timezone.localdate()
    qs = BookingRequest.objects.filter(created_at__date=today)
    if not qs.exists():
        return "No requests today yet."
    return "📅 Today's requests:\n" + "\n".join(
        f"#{b.ref_code} — {b.full_name} ({b.status})" for b in qs
    )


def cmd_pending() -> str:
    qs = BookingRequest.objects.filter(status=BookingRequest.Status.NEW)
    if not qs.exists():
        return "Nothing pending. 🎉"
    return "⏳ Pending requests:\n" + "\n".join(f"#{b.ref_code} — {b.full_name}" for b in qs)


def cmd_week() -> str:
    since = timezone.now() - timedelta(days=7)
    qs = BookingRequest.objects.filter(created_at__gte=since)
    return f"📈 {qs.count()} requests in the last 7 days."


def cmd_stats() -> str:
    total = BookingRequest.objects.count()
    confirmed = BookingRequest.objects.filter(status=BookingRequest.Status.CONFIRMED).count()
    completed = BookingRequest.objects.filter(status=BookingRequest.Status.COMPLETED).count()
    return f"📊 Stats — total: {total} · confirmed: {confirmed} · completed: {completed}"


_COMMANDS = {
    "/today": cmd_today,
    "/pending": cmd_pending,
    "/week": cmd_week,
    "/stats": cmd_stats,
}


# ---------------------------------------------------------------------------
# Webhook view
# ---------------------------------------------------------------------------


def _is_known_admin(chat_id: str) -> bool:
    return TelegramAdmin.objects.filter(chat_id=str(chat_id), is_active=True).exists()


async def _handle_update(update: Update, bot: Bot) -> None:
    if update.callback_query is not None:
        query = update.callback_query
        chat_id = query.from_user.id if query.from_user else None
        if chat_id is None or not await _is_known_admin_async(chat_id):
            await query.answer()  # ack silently, do nothing
            return

        data = query.data or ""
        action, _, ref_code = data.partition(":")
        new_status = _CALLBACK_STATUS_MAP.get(action)
        if new_status and ref_code:
            await _apply_status_update(ref_code, new_status)
            try:
                await query.edit_message_text(
                    text=f"{query.message.text}\n\n— Updated to {new_status} by {query.from_user.first_name}",
                )
            except Exception:  # noqa: BLE001 - Telegram edit failures shouldn't crash the webhook
                logger.exception("Failed to edit Telegram message after status update")
        await query.answer()
        return

    if update.message is not None and update.message.text:
        chat_id = update.message.chat_id
        if not await _is_known_admin_async(chat_id):
            return  # unknown sender: ignored silently, per CLAUDE.md §8

        text = update.message.text.strip()
        command = text.split()[0].lower()
        handler = _COMMANDS.get(command)
        if handler:
            reply = await _run_sync(handler)
            await bot.send_message(chat_id=chat_id, text=reply)


async def _is_known_admin_async(chat_id) -> bool:
    return await _run_sync(_is_known_admin, str(chat_id))


async def _apply_status_update(ref_code: str, new_status: str) -> None:
    def _update():
        BookingRequest.objects.filter(ref_code=ref_code).update(status=new_status)

    await _run_sync(_update)


async def _run_sync(func, *args):
    from asgiref.sync import sync_to_async

    return await sync_to_async(func, thread_sensitive=True)(*args)


@csrf_exempt
@require_POST
def telegram_webhook(request: HttpRequest, secret: str) -> HttpResponse:
    if secret != settings.TELEGRAM_WEBHOOK_SECRET:
        return HttpResponseForbidden()

    try:
        data = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return HttpResponse(status=400)

    bot = get_bot()
    update = Update.de_json(data, bot)

    try:
        asyncio.run(_handle_update(update, bot))
    except Exception:  # noqa: BLE001 - never let a bot-handling bug break the webhook 200
        logger.exception("Error handling Telegram update")

    return JsonResponse({"ok": True})
