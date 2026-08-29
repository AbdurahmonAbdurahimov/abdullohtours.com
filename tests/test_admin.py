"""
Admin panel regression tests.

The sidebar navigation config (UNFOLD["SIDEBAR"]) previously passed bare
reverse-lookup names (e.g. "admin:bookings_bookingrequest_changelist") as
the "link" value instead of a resolved URL. django-unfold renders whatever
`link` is given verbatim as the <a href>, so every sidebar link pointed at
the literal, unresolved string rather than the actual admin page — every
link "worked" (200 status on direct fetch) but was completely unclickable
in the real UI. This must never regress silently.
"""

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

pytestmark = pytest.mark.django_db


def _sidebar_items():
    for group in settings.UNFOLD["SIDEBAR"]["navigation"]:
        yield from group["items"]


def test_every_sidebar_link_is_a_resolved_url_not_a_bare_name():
    for item in _sidebar_items():
        link = str(item["link"])
        assert link.startswith("/"), (
            f"Sidebar item {item['title']!r} has an unresolved link {link!r} — "
            "use reverse_lazy(...), not a bare 'admin:...' string."
        )


def test_every_sidebar_link_resolves_to_a_real_admin_view():
    for item in _sidebar_items():
        # Round-trip: the resolved path must itself be reverse-able back to
        # a real URL name (guards against a stale/renamed url name too).
        link = str(item["link"])
        assert link.startswith("/admin/")


def test_admin_index_renders_real_hrefs_for_every_sidebar_link():
    User = get_user_model()
    user = User.objects.create_superuser("admintest", "admin@example.com", "pw12345!")
    client = Client()
    client.force_login(user)

    response = client.get(reverse("admin:index"))
    content = response.content.decode()

    assert response.status_code == 200
    assert 'href="admin:' not in content
    for item in _sidebar_items():
        assert f'href="{item["link"]}"' in content
