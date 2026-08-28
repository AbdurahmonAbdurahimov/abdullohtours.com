# Abdulloh Tours — abdullohtours.com

Production website for Abdulloh Tours, a private tour operator in
Uzbekistan. Full spec: `CLAUDE.md`.

Stack: Python 3.12 + Django 5, PostgreSQL 16, Tailwind CSS (CLI, not CDN),
Alpine.js/HTMX, django-unfold, django-modeltranslation, Gunicorn + Caddy,
Docker Compose, cron (no Celery/Redis).

## Local development

```bash
# 1. Python env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

# 2. Frontend build (Tailwind CLI)
npm install
npm run build:css        # or: npm run watch:css

# 3. Environment
cp .env.example .env     # edit values as needed

# 4. Database (Postgres 16 via Docker — no sqlite fallback, see CLAUDE.md §2)
docker compose up -d db

# 5. Django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 6. Tests
pytest
```

Local dev uses `config.settings.dev` (the `manage.py` default). Admin is at
`/admin/` (django-unfold theme). Site pages are language-prefixed, e.g.
`/en/`, `/ru/`.

### Running the pricing tests only

```bash
pytest tests/test_pricing.py -v
```

This suite is the one CLAUDE.md calls out as non-negotiable — the pricing
engine (`apps/catalog/pricing.py`) is pure/DB-free so these tests run fast
and don't need Postgres.

## Deployment (Hostinger VPS)

Target: a single Hostinger VPS (Ubuntu 24.04, 2vCPU/4GB) in Germany.
Canonical host is `https://abdullohtours.com` — **no www** (Caddy 301s
`www.abdullohtours.com` to the apex, see `Caddyfile`). Point DNS at the VPS
*before* the first deploy so Caddy can obtain its Let's Encrypt certificate.

```bash
# On the server, first time:
cp .env.example .env   # fill in real SECRET_KEY, POSTGRES_*, TELEGRAM_*, etc.
git clone <repo> abdullohtours.com && cd abdullohtours.com

# Every deploy:
./deploy.sh
```

`deploy.sh` pulls, builds the Docker images (multi-stage: Tailwind CLI build
→ Python/gunicorn), runs migrations, collects static files, and restarts
services via `docker-compose.yml` + `docker-compose.prod.yml`.

Services: `web` (gunicorn, 3 workers), `db` (postgres:16-alpine, internal
network only — no published port), `caddy` (ports 80/443, automatic HTTPS,
www→apex redirect). Postgres data, media, static files, and Caddy's
TLS state all live in named Docker volumes (`postgres_data`, `media_data`,
`static_data`, `caddy_data`, `caddy_config`) — never bind-mounted from the
project directory.

Cron jobs (see CLAUDE.md §9) run `python manage.py <command>` inside the
`web` container, e.g.:

```cron
* * * * *    cd /path/to/abdullohtours.com && docker compose exec -T web python manage.py send_pending_notifications
*/15 * * * * cd /path/to/abdullohtours.com && docker compose exec -T web python manage.py check_unanswered_requests
0 3 * * *    cd /path/to/abdullohtours.com && docker compose exec -T web python manage.py update_exchange_rates
0 4 * * *    cd /path/to/abdullohtours.com && docker compose exec -T web python manage.py backup_db
```

## Repo structure

See `CLAUDE.md` for the full spec. Short version:

- `config/` — Django project (settings split base/dev/prod, root urlconf)
- `apps/core` — SiteSettings, SEOMixin, sitemaps, home/about/contact/faq
- `apps/catalog` — Destinations, Packages, Activities, Vehicles, `pricing.py`
- `apps/bookings` — BookingRequest/BookingItem/BuilderSession, forms, availability
- `apps/blog` — BlogPost
- `apps/notifications` — Notification, TelegramAdmin, bot webhook, cron commands
- `templates/` — server-rendered Django templates (no SPA — SEO-first)
- `static_src/` — Tailwind CLI source (config, input.css, self-hosted fonts)
- `tests/` — pytest suite (`test_pricing.py` is the priority one)

## Status

This is a Phase 1 scaffold: models, admin, pricing engine + tests, URL
routing, minimal SEO-aware templates, Telegram bot/notification plumbing,
and the Docker/Caddy deployment setup are in place. Real content, seed
data (`fixtures/README.md`), self-hosted font binaries
(`static_src/fonts/README.md`), and the Tour Builder UI (Phase 2, per
CLAUDE.md §13) are explicitly follow-up work — look for `TODO: content
needed` markers.
