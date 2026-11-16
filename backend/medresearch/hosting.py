import dj_database_url
from django.core.exceptions import ImproperlyConfigured


def postgres_url(value):
    try:
        result = dj_database_url.parse(value, conn_max_age=60, conn_health_checks=True)
        if result.get("ENGINE") != "django.db.backends.postgresql" or not result.get("HOST") or not result.get("NAME"):
            raise ValueError()
    except (ValueError, KeyError):
        raise ImproperlyConfigured("DATABASE_URL must be a valid PostgreSQL connection URL.") from None
    result.setdefault("OPTIONS", {}).setdefault("sslmode", "require")
    return result
