"""Static URLs for assets that change often during active development
(the Tailwind build, hand-written JS) — {% static %} alone reuses the same
URL across rebuilds, so a browser's heuristic freshness caching can keep
serving a stale file for hours after a rebuild without even revalidating.
Appending the file's mtime as a query string busts that cache on every
rebuild.
"""

from __future__ import annotations

import os

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def static_v(path: str) -> str:
    url = static(path)
    file_path = finders.find(path) or os.path.join(settings.STATIC_ROOT, path)
    try:
        version = int(os.path.getmtime(file_path))
    except OSError:
        return url
    return f"{url}?v={version}"
