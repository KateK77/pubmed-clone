import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")
DEBUG = os.getenv("DJANGO_DEBUG", "1") == "1"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY") or (
    "local-only-medresearch-development-key" if DEBUG else ""
)
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
INSTALLED_APPS = [
    "django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions",
    "rest_framework", "drf_spectacular", "literature",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
]
ROOT_URLCONF = "medresearch.urls"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True
TIME_ZONE = "UTC"
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
if os.getenv("POSTGRES_DB"):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["POSTGRES_DB"],
        "USER": os.environ["POSTGRES_USER"],
        "PASSWORD": os.environ["POSTGRES_PASSWORD"],
        "HOST": os.getenv("POSTGRES_HOST", "localhost"),
        "PORT": os.getenv("POSTGRES_PORT", "5432"),
    }
CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
if os.getenv("DJANGO_CACHE_TABLE"):
    CACHES["default"] = {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": os.environ["DJANGO_CACHE_TABLE"],
    }
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if os.getenv("DJANGO_TRUST_PROXY") == "1" else None
AUTH_PASSWORD_VALIDATORS = [{"NAME": "django.contrib.auth.password_validation." + name} for name in (
    "UserAttributeSimilarityValidator", "MinimumLengthValidator",
    "CommonPasswordValidator", "NumericPasswordValidator",
)]
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.SessionAuthentication"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
}
SPECTACULAR_SETTINGS = {"TITLE": "MedResearch API", "VERSION": "0.1.0"}
NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")
NCBI_EMAIL = os.getenv("NCBI_EMAIL", "")
NCBI_CACHE_SECONDS = int(os.getenv("NCBI_CACHE_SECONDS", "900"))
