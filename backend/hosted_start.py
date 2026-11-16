"""Start the single-instance public showcase with durable database storage."""
import os
from pathlib import Path


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medresearch.settings")
    import django
    django.setup()
    from django.conf import settings
    from django.core.management import call_command

    if settings.DEBUG:
        raise SystemExit("Hosted startup requires DJANGO_DEBUG=0.")
    if settings.DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
        raise SystemExit("Hosted startup requires PostgreSQL. Configure DATABASE_URL before deploying.")
    if not (settings.FRONTEND_DIR / "index.html").is_file():
        raise SystemExit("Build the frontend before deploying.")
    try:
        port = int(os.getenv("PORT", "8000"))
        if not 1 <= port <= 65535:
            raise ValueError()
    except ValueError:
        raise SystemExit("PORT must be a number between 1 and 65535.") from None
    call_command("migrate", interactive=False)
    if os.getenv("DJANGO_CACHE_TABLE"):
        call_command("createcachetable")
    os.chdir(Path(__file__).resolve().parent)
    os.execvp("gunicorn", ["gunicorn", "medresearch.wsgi:application", "--bind", f"0.0.0.0:{port}",
                          "--workers", "1", "--threads", "4", "--timeout", "120", "--access-logfile", "-"])


if __name__ == "__main__":
    main()
