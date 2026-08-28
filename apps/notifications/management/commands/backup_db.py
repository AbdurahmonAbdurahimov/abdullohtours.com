import subprocess
import time
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from apps.notifications.models import Notification

BACKUP_DIR = (
    Path(settings.BASE_DIR) / "db_backups" if hasattr(settings, "BASE_DIR") else Path("db_backups")
)
RETENTION_DAYS = 14


class Command(BaseCommand):
    help = (
        "pg_dump the database to db_backups/, prune dumps older than "
        f"{RETENTION_DAYS} days, and send the fresh dump to Telegram admins as a "
        "document so backups live off-server too. Run daily via cron (04:00)."
    )

    def handle(self, *args, **options):
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)

        db = settings.DATABASES["default"]
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        dump_path = BACKUP_DIR / f"abdullohtours-{timestamp}.dump"

        cmd = [
            "pg_dump",
            "-Fc",  # custom format, compressed, restorable with pg_restore
            "-h",
            db["HOST"] or "localhost",
            "-p",
            str(db["PORT"] or "5432"),
            "-U",
            db["USER"],
            "-d",
            db["NAME"],
            "-f",
            str(dump_path),
        ]
        env = {"PGPASSWORD": db["PASSWORD"]} if db.get("PASSWORD") else None

        try:
            subprocess.run(cmd, check=True, env=env)
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            self.stderr.write(self.style.ERROR(f"pg_dump failed: {exc}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Backup written to {dump_path}"))

        self._prune_old_backups()
        self._queue_telegram_delivery(dump_path)

    def _prune_old_backups(self) -> None:
        cutoff = time.time() - RETENTION_DAYS * 86400
        for f in BACKUP_DIR.glob("abdullohtours-*.dump"):
            if f.stat().st_mtime < cutoff:
                f.unlink()
                self.stdout.write(f"Pruned old backup: {f.name}")

    def _queue_telegram_delivery(self, dump_path: Path) -> None:
        # Reuse the standard Notification -> senders.send_notification pipeline
        # (the same machinery every other Telegram message goes through) rather
        # than duplicating Bot API calls here.
        Notification.objects.create(
            kind=Notification.Kind.DB_BACKUP,
            payload={
                "audience": "bookings",  # any active admin; backups aren't booking-specific
                "document_path": str(dump_path),
                "caption": f"📦 DB backup — {dump_path.name}",
            },
        )
        self.stdout.write(
            "Queued backup for Telegram delivery (send_pending_notifications will pick it up)."
        )
