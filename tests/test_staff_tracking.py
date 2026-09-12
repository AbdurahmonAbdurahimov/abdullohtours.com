"""
Tests for the admin/staff activity tracking feature (CLAUDE.md §11): audit
trail of login/logout/failed-login events, and a live "who's online" table
kept fresh by TrackActiveSessionMiddleware.
"""

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

from apps.core.models import ActiveSession, LoginEvent

pytestmark = pytest.mark.django_db

User = get_user_model()


def _make_staff_user(username="staff", password="testpass123"):
    return User.objects.create_user(
        username=username, password=password, is_staff=True, is_superuser=True
    )


def test_successful_login_creates_login_event_and_active_session(client):
    user = _make_staff_user()
    response = client.post(
        reverse("admin:login"),
        {"username": "staff", "password": "testpass123", "next": "/admin/"},
    )
    assert response.status_code == 302

    event = LoginEvent.objects.get(user=user)
    assert event.event_type == LoginEvent.EventType.LOGIN

    session = ActiveSession.objects.get(user=user)
    assert session.session_key == client.session.session_key


def test_failed_login_records_username_attempted_with_no_user(client):
    _make_staff_user()
    client.post(
        reverse("admin:login"),
        {"username": "staff", "password": "wrong-password", "next": "/admin/"},
    )

    event = LoginEvent.objects.get(event_type=LoginEvent.EventType.FAILED)
    assert event.user is None
    assert event.username_attempted == "staff"


def test_logout_removes_active_session_and_logs_event(client):
    user = _make_staff_user()
    client.post(
        reverse("admin:login"),
        {"username": "staff", "password": "testpass123", "next": "/admin/"},
    )
    assert ActiveSession.objects.filter(user=user).exists()

    client.post(reverse("admin:logout"))

    assert not ActiveSession.objects.filter(user=user).exists()
    assert LoginEvent.objects.filter(user=user, event_type=LoginEvent.EventType.LOGOUT).exists()


def test_active_session_last_seen_is_touched_by_middleware(client):
    user = _make_staff_user()
    client.post(
        reverse("admin:login"),
        {"username": "staff", "password": "testpass123", "next": "/admin/"},
    )
    session = ActiveSession.objects.get(user=user)

    # Force the throttle window open so the next request is treated as due
    # for a refresh (TrackActiveSessionMiddleware only writes ~once/minute).
    django_session = client.session
    django_session["_active_session_touched_at"] = (
        timezone.now() - timedelta(minutes=5)
    ).isoformat()
    django_session.save()

    stale_last_seen = timezone.now() - timedelta(minutes=5)
    ActiveSession.objects.filter(pk=session.pk).update(last_seen_at=stale_last_seen)

    client.get("/admin/")

    session.refresh_from_db()
    assert session.last_seen_at > stale_last_seen


def test_non_staff_login_does_not_create_active_session():
    """ActiveSession is an internal ops tool (CLAUDE.md), not analytics on
    ordinary site visitors — only staff logins get tracked."""
    from django.test import Client

    User.objects.create_user(username="visitor", password="testpass123", is_staff=False)
    client = Client()
    client.login(username="visitor", password="testpass123")

    assert not ActiveSession.objects.exists()


def test_login_event_admin_is_read_only(admin_client):
    response = admin_client.get(reverse("admin:core_loginevent_add"))
    assert response.status_code == 403


def test_active_session_and_login_event_changelists_render(admin_client):
    assert admin_client.get(reverse("admin:core_loginevent_changelist")).status_code == 200
    assert admin_client.get(reverse("admin:core_activesession_changelist")).status_code == 200


def test_prune_stale_sessions_command_deletes_only_expired(settings):
    from django.core.management import call_command

    user = _make_staff_user()
    settings.SESSION_COOKIE_AGE = 3600  # 1 hour

    fresh = ActiveSession.objects.create(user=user, session_key="fresh-session")
    stale = ActiveSession.objects.create(user=user, session_key="stale-session")
    # last_seen_at is auto_now=True, so it's stamped to "now" on create();
    # backdate it directly via .update() to bypass that and simulate a
    # session that's been idle for a while.
    ActiveSession.objects.filter(pk=stale.pk).update(
        last_seen_at=timezone.now() - timedelta(hours=2)
    )

    call_command("prune_stale_sessions")

    assert ActiveSession.objects.filter(pk=fresh.pk).exists()
    assert not ActiveSession.objects.filter(pk=stale.pk).exists()
