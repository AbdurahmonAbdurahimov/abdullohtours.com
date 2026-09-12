"""Keeps `ActiveSession.last_seen_at` fresh for signed-in staff/admin users.

The login/logout signals (apps.core.signals) create and delete the
`ActiveSession` row; this middleware is the thing that makes "last seen"
mean something between those two events. It only touches the DB roughly
once a minute per session (`_UPDATE_INTERVAL`) rather than on every request
— staff browsing the admin fires many requests per minute and a write on
each one would be pure overhead with no user-visible benefit.
"""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

_UPDATE_INTERVAL = timedelta(minutes=1)


class TrackActiveSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if user is not None and getattr(user, "is_authenticated", False) and user.is_staff:
            self._touch(request)

        return response

    def _touch(self, request) -> None:
        session_key = request.session.session_key
        if not session_key:
            return

        session_marker = "_active_session_touched_at"
        last_touched = request.session.get(session_marker)
        now = timezone.now()
        if last_touched:
            try:
                if now - timezone.datetime.fromisoformat(last_touched) < _UPDATE_INTERVAL:
                    return
            except ValueError:
                pass

        from .models import ActiveSession

        ActiveSession.objects.filter(session_key=session_key).update(last_seen_at=now)
        request.session[session_marker] = now.isoformat()
