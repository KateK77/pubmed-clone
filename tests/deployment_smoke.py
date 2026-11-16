"""Exercise the actual production WSGI app after building frontend/dist."""
import os
import re
import secrets
import sys
import tempfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "backend"))


def main():
    with tempfile.TemporaryDirectory(prefix="medresearch-wsgi-") as temporary:
        os.environ.update({
            "DJANGO_SETTINGS_MODULE": "medresearch.settings", "DJANGO_DEBUG": "0",
            "DJANGO_SECRET_KEY": secrets.token_urlsafe(48), "DJANGO_ALLOWED_HOSTS": "research.example.org",
            "DJANGO_TRUST_PROXY": "0", "DJANGO_HSTS_SECONDS": "3600", "POSTGRES_DB": "",
            "DATABASE_URL": "",
            "DJANGO_SQLITE_PATH": str(Path(temporary) / "production-smoke.sqlite3"),
        })
        import django
        django.setup()
        from django.core.management import call_command
        from django.db import connections
        from django.test import RequestFactory
        from medresearch.wsgi import application

        call_command("migrate", verbosity=0, interactive=False)
        factory = RequestFactory()

        def get(path, secure=True):
            captured = {}

            def start_response(status, headers):
                captured.update(status=int(status.split()[0]), headers=headers)

            request = factory.get(path, secure=secure, HTTP_HOST="research.example.org")
            response = application(request.environ, start_response)
            try:
                body = b"".join(response)
            finally:
                if hasattr(response, "close"):
                    response.close()
            return captured["status"], captured["headers"], body

        status, headers, body = get("/profile")
        assert status == 200 and b'id="root"' in body
        assert dict(headers)["X-Frame-Options"] == "DENY"
        assert "no-store" in dict(headers)["Cache-Control"]
        asset = re.search(rb'src="(/assets/[^\"]+\.js)"', body).group(1).decode()
        assert get(asset)[0] == 200
        assert get("/article/31452104")[0] == 200
        assert get("/api/health/")[0] == 200
        assert get("/api/missing/")[0] == 404
        assert get("/assets/missing.js")[0] == 404
        status, headers, body = get("/api/session/")
        cookies = [value for key, value in headers if key.lower() == "set-cookie"]
        assert status == 200 and b'"user":null' in body
        assert any("medresearch_csrftoken=" in value and "Secure" in value for value in cookies)
        assert get("/profile", secure=False)[0] == 301
        # Unknown frontend routes must never expose files outside the built distribution.
        assert b"DJANGO_SECRET_KEY" not in get("/.env")[2]
        connections.close_all()
        print("Production WSGI passed: SPA routes, assets, API, HTTPS redirect and secure CSRF cookie.")


if __name__ == "__main__":
    main()
