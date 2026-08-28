# syntax=docker/dockerfile:1

# ---------------------------------------------------------------------------
# Stage 1: build Tailwind CSS from static_src/ with the Tailwind CLI
# (CLAUDE.md §2 — no cdn.tailwindcss.com in production).
# ---------------------------------------------------------------------------
FROM node:20-alpine AS css-builder
WORKDIR /app
COPY package.json ./
RUN npm install
COPY static_src/ static_src/
COPY templates/ templates/
COPY apps/ apps/
RUN npm run build:css

# ---------------------------------------------------------------------------
# Stage 2: Python/Django app image
# ---------------------------------------------------------------------------
FROM python:3.12-slim AS app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.prod

# postgresql-client provides pg_dump for the backup_db management command;
# gettext provides msgfmt for `manage.py compilemessages` below (CLAUDE.md
# §12 i18n) — .po sources are committed, but the .mo catalogs Django
# actually loads at runtime are generated here rather than committed as
# binaries, the same way static_src/css/main.css is built rather than
# committed.
RUN apt-get update \
    && apt-get install -y --no-install-recommends postgresql-client libpq-dev gcc gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Built CSS from stage 1 overlays static_src's own (uncompiled) source —
# STATICFILES_DIRS only points at static_src/, so the compiled CSS must land
# inside it (not a top-level static/) or collectstatic never finds it.
COPY --from=css-builder /app/static_src/css/main.css static_src/css/main.css

RUN python manage.py compilemessages

RUN addgroup --system django && adduser --system --ingroup django django \
    && mkdir -p /app/media /app/staticfiles /app/db_backups \
    && chown -R django:django /app
USER django

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
