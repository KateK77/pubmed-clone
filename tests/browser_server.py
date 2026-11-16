"""Isolated Django backend for browser tests. All data is disposable."""
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
state = Path(os.environ["MEDRESEARCH_TEST_STATE"])
state.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(root / "backend"))
os.environ.update({
    "DJANGO_SETTINGS_MODULE": "medresearch.settings",
    "DJANGO_DEBUG": "1",
    "DJANGO_ALLOWED_HOSTS": "localhost,127.0.0.1",
    "DJANGO_SQLITE_PATH": str(state / "browser.sqlite3"),
    "POSTGRES_DB": "",
    "EMAIL_VERIFICATION_REQUIRED": "1",
    "EMAIL_BACKEND": "django.core.mail.backends.filebased.EmailBackend",
    "EMAIL_FILE_PATH": str(state / "mail"),
    "DEFAULT_FROM_EMAIL": "tests@example.org",
})

import django
from django.core.management import call_command

django.setup()
call_command("migrate", interactive=False, verbosity=0)
call_command("runserver", "127.0.0.1:8025", use_reloader=False)
