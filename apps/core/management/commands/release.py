"""Release-phase tasks, run once per deploy before new code takes traffic (ADR-0014).

Platforms call it differently: Heroku `release:`, Render `preDeployCommand`, Fly.io
`release_command`, compose `migrate` one-shot, Kamal/Coolify via RELEASE_ON_START. A PostgreSQL
advisory lock makes concurrent invocations safe (Django's migrate is not), so several
containers starting at once still apply each migration exactly once.
"""

from typing import Any

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection

RELEASE_LOCK_KEY = 7_400_001  # arbitrary, constant, unique to this application


class Command(BaseCommand):
    help = "Run release-phase tasks (database migrations) safely under concurrency."

    def handle(self, *args: Any, **options: Any) -> None:
        with connection.cursor() as cursor:
            self.stdout.write("release: waiting for the release lock")
            cursor.execute("SELECT pg_advisory_lock(%s)", [RELEASE_LOCK_KEY])
            try:
                call_command("migrate", interactive=False, verbosity=options["verbosity"])
            finally:
                cursor.execute("SELECT pg_advisory_unlock(%s)", [RELEASE_LOCK_KEY])
        self.stdout.write(self.style.SUCCESS("release: done"))
