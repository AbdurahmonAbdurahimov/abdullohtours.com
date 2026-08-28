"""Local development settings."""

from .base import *  # noqa: F401,F403

DEBUG = True

# Permissive for local dev only — prod.py reads a real allowlist from env.
ALLOWED_HOSTS = ["*"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
