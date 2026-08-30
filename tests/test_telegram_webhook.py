"""
Tests for apps/notifications/telegram_bot.telegram_webhook (CLAUDE.md §8):
it must return 200 to Telegram no matter what goes wrong handling an update
— webhook deliveries that get a non-2xx response enough times get disabled
by Telegram, so a bug here should never surface as a 5xx.
"""

import json

import pytest
from django.conf import settings
from django.test import Client

from apps.notifications.models import TelegramAdmin

pytestmark = pytest.mark.django_db


def _url():
    return f"/tg/webhook/{settings.TELEGRAM_WEBHOOK_SECRET}/"


def _post_update(client, chat_id=999999999, text="/today", update_id=1):
    body = {
        "update_id": update_id,
        "message": {
            "message_id": update_id,
            "date": 1735000000,
            "chat": {"id": chat_id, "type": "private"},
            "from": {"id": chat_id, "is_bot": False, "first_name": "Tester"},
            "text": text,
        },
    }
    return client.post(_url(), data=json.dumps(body), content_type="application/json")


def test_wrong_secret_is_forbidden():
    resp = Client().post("/tg/webhook/wrong-secret/", data="{}", content_type="application/json")
    assert resp.status_code == 403


def test_invalid_json_body_is_400_not_500():
    resp = Client().post(_url(), data="not json", content_type="application/json")
    assert resp.status_code == 400


def test_valid_json_but_not_an_update_shape_is_200_not_500():
    # {} is valid JSON but Update.de_json(...) can't build an Update from it
    # (missing update_id) — must be caught, not propagate as a 500.
    resp = Client().post(_url(), data="{}", content_type="application/json")
    assert resp.status_code == 200


def test_update_from_unregistered_chat_is_ignored_but_still_200():
    resp = _post_update(Client(), chat_id=1)
    assert resp.status_code == 200


def test_update_from_registered_admin_is_handled_and_still_200():
    TelegramAdmin.objects.create(chat_id="123123123", name="Test admin", is_active=True)
    resp = _post_update(Client(), chat_id=123123123, text="/today")
    assert resp.status_code == 200


def test_empty_bot_token_never_surfaces_as_500(settings):
    # Regression: get_bot() (Bot(token=...)) used to run *outside* the
    # try/except in telegram_webhook(), so python-telegram-bot's own
    # synchronous check in Bot.__init__ (`if not token: raise InvalidToken`,
    # before any network call — it does NOT validate the token's shape,
    # only that it's non-empty) turned a momentarily-empty TELEGRAM_BOT_TOKEN
    # into a hard 500 instead of the graceful "log and return 200" every
    # other failure mode here gets. Reproduced live: .env was mid-edit and
    # read back empty for one request.
    settings.TELEGRAM_BOT_TOKEN = ""
    resp = _post_update(Client(), chat_id=1)
    assert resp.status_code == 200
