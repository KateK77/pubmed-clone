"""Configuration-only overlay for the isolated final evaluation."""
import os
from pathlib import Path

runtime = Path(os.environ['EVALUATION_CASE_DIR']).resolve()
source = Path(os.environ['EVALUATION_SOURCE_DIR']).resolve()
if not runtime.is_dir() or not source.is_dir():
    raise RuntimeError('Initialize an evaluation case first.')
if (source / '.env').exists():
    raise RuntimeError('An evaluation source snapshot must not contain .env.')

from medresearch.settings import *  # noqa: E402,F403

DEBUG = True
SECRET_KEY = (runtime / 'django-secret.txt').read_text().strip()
ALLOWED_HOSTS = ['127.0.0.1', 'localhost']
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3',
    'NAME': str(runtime / 'evaluation.sqlite3'),
    'OPTIONS': {'transaction_mode': 'IMMEDIATE', 'timeout': 20}}}
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}}
# Preserve both application cookie names. Isolation is provided by a new browser context.
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SECURE_HSTS_SECONDS = 0
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8124']
EMAIL_VERIFICATION_REQUIRED = os.environ['EVALUATION_MODE'] in ('mail', 'smtp', 'unavailable')
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = str(runtime / 'mail')
DEFAULT_FROM_EMAIL = 'evaluation@example.test'
EMAIL_HOST = EMAIL_HOST_USER = EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = EMAIL_USE_SSL = False
if os.environ['EVALUATION_MODE'] == 'unavailable':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    DEFAULT_FROM_EMAIL = ''
elif os.environ['EVALUATION_MODE'] == 'smtp':
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = '127.0.0.1'
    EMAIL_PORT = 8127
FRONTEND_DIR = source / 'frontend' / 'dist'
NCBI_API_KEY = ''
NCBI_EMAIL = ''
