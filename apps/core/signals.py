"""Deletes a WebPImageField's file (+ responsive variants) from storage when
the row that owns it is deleted. Django never does this on its own for a
plain FileField/ImageField — the replace/clear case is instead handled in
WebPImageField.pre_save (apps/core/fields.py); this covers the third way a
file becomes orphaned.

Connected generically (no `sender=`) in CoreConfig.ready() so every model
with a WebPImageField is covered without per-model boilerplate — the
receiver itself is a no-op for any model that doesn't have one.
"""

from __future__ import annotations

from . import imaging
from .fields import WebPImageField


def cleanup_webp_images_on_delete(sender, instance, **kwargs):
    for field in sender._meta.get_fields():
        if not isinstance(field, WebPImageField):
            continue
        file = getattr(instance, field.attname, None)
        if not file:
            continue
        width = getattr(instance, field.width_field, None) if field.width_field else None
        imaging.delete_with_variants(file.storage, file.name, width)


def _client_ip(request) -> str | None:
    # Trust X-Forwarded-For's first hop: Caddy (config/Caddyfile) is the only
    # reverse proxy in front of Gunicorn, so this can't be spoofed by a
    # client talking directly to the app.
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def _user_agent(request) -> str:
    return request.META.get("HTTP_USER_AGENT", "")[:255]


def record_login(sender, request, user, **kwargs):
    from .models import ActiveSession, LoginEvent

    LoginEvent.objects.create(
        user=user,
        event_type=LoginEvent.EventType.LOGIN,
        ip_address=_client_ip(request),
        user_agent=_user_agent(request),
        session_key=request.session.session_key or "",
    )
    if user.is_staff and request.session.session_key:
        ActiveSession.objects.update_or_create(
            session_key=request.session.session_key,
            defaults={
                "user": user,
                "ip_address": _client_ip(request),
                "user_agent": _user_agent(request),
            },
        )


def record_logout(sender, request, user, **kwargs):
    from .models import ActiveSession, LoginEvent

    # `user` is None for a request that hits the logout view without an
    # authenticated session (e.g. a stale/expired cookie) — nothing to log.
    if user is not None:
        LoginEvent.objects.create(
            user=user,
            event_type=LoginEvent.EventType.LOGOUT,
            ip_address=_client_ip(request),
            user_agent=_user_agent(request),
            session_key=request.session.session_key or "",
        )
    session_key = request.session.session_key
    if session_key:
        ActiveSession.objects.filter(session_key=session_key).delete()


def record_login_failed(sender, credentials, request=None, **kwargs):
    from .models import LoginEvent

    LoginEvent.objects.create(
        user=None,
        username_attempted=str(credentials.get("username", ""))[:150],
        event_type=LoginEvent.EventType.FAILED,
        ip_address=_client_ip(request) if request else None,
        user_agent=_user_agent(request) if request else "",
        session_key=(request.session.session_key or "") if request else "",
    )
