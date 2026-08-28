"""
Production settings — Hostinger VPS (Ubuntu 24.04, 2vCPU/4GB), served behind
Caddy which terminates TLS and reverse-proxies to gunicorn. Canonical host is
https://abdullohtours.com (no www — Caddyfile 301-redirects www -> apex).
"""

from .base import *  # noqa: F401,F403
from .base import env  # noqa: F401

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["abdullohtours.com", "www.abdullohtours.com"])

# Caddy terminates TLS and forwards to gunicorn over plain HTTP on the
# internal docker network, setting X-Forwarded-Proto.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

CSRF_TRUSTED_ORIGINS = [CANONICAL_HOST]  # noqa: F405
