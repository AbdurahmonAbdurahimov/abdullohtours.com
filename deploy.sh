#!/usr/bin/env bash
# Deploy script for the Hostinger VPS target (CLAUDE.md deployment section).
# Run from the project root on the server, e.g.: `./deploy.sh`

set -euo pipefail

COMPOSE="docker compose -f docker-compose.yml -f docker-compose.prod.yml"

echo "==> Pulling latest code"
git pull

echo "==> Building images"
$COMPOSE build

echo "==> Starting db + caddy (web restarts after migrate below)"
$COMPOSE up -d db caddy

echo "==> Running migrations"
$COMPOSE run --rm web python manage.py migrate --noinput

echo "==> Collecting static files"
$COMPOSE run --rm web python manage.py collectstatic --noinput

echo "==> Starting/restarting web"
$COMPOSE up -d web

echo "==> Reloading caddy config (in case Caddyfile changed)"
$COMPOSE exec caddy caddy reload --config /etc/caddy/Caddyfile

echo "==> Done."
