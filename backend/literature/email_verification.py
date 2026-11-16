import secrets
from datetime import timedelta
from hashlib import sha256
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.crypto import constant_time_compare, salted_hmac
from rest_framework.exceptions import APIException, Throttled, ValidationError

from .models import AccountEmail, EmailChallenge

MAX_ATTEMPTS = 5
CODE_MINUTES = 10
RESEND_SECONDS = 60


class EmailUnavailable(APIException):
    status_code = 503
    default_detail = "Email delivery is unavailable. Please try again later or contact the site operator."


def available():
    if settings.EMAIL_BACKEND == "django.core.mail.backends.smtp.EmailBackend":
        return bool(settings.EMAIL_HOST and settings.DEFAULT_FROM_EMAIL)
    return bool(settings.DEFAULT_FROM_EMAIL)


def check_address(address, user=None):
    address = address.strip().lower()
    accounts = get_user_model().objects.filter(email__iexact=address)
    reservations = AccountEmail.objects.filter(address=address)
    if user:
        accounts = accounts.exclude(pk=user.pk)
        reservations = reservations.exclude(user=user)
    if accounts.exists() or reservations.exists():
        raise ValidationError({"email": "This email is already associated with an account."})
    return address


def challenge_key(address, purpose, user_id=None):
    return sha256(f"{purpose}|{user_id or ''}|{address}".encode()).hexdigest()


def digest(key, nonce, code):
    return salted_hmac("medresearch.email-verification", f"{key}|{nonce}|{code}", algorithm="sha256").hexdigest()


def send_code(address, purpose, user=None):
    if not available():
        raise EmailUnavailable()
    address = check_address(address, user)
    key = challenge_key(address, purpose, user.pk if user else None)
    now = timezone.now()
    nonce = secrets.token_hex(16)
    code = f"{secrets.randbelow(1000000):06d}"
    with transaction.atomic():
        row, created = EmailChallenge.objects.select_for_update().get_or_create(
            key=key,
            defaults={"sent_at": now, "expires_at": now, "nonce": "", "digest": ""},
        )
        if not created and (now - row.sent_at).total_seconds() < RESEND_SECONDS:
            raise Throttled(RESEND_SECONDS, "Wait a minute before requesting another code.")
        row.nonce = nonce
        row.digest = digest(key, nonce, code)
        row.sent_at = now
        row.expires_at = now + timedelta(minutes=CODE_MINUTES)
        row.attempts = 0
        row.delivered = False
        row.save()
    try:
        sent = send_mail(
            "Your MedResearch verification code",
            f"Your MedResearch code is {code}.\n\nIt expires in {CODE_MINUTES} minutes. "
            "Enter it on the MedResearch page where you requested it. "
            "If you did not request this code, you can ignore this email.",
            settings.DEFAULT_FROM_EMAIL,
            [address],
            fail_silently=False,
        )
        if sent != 1:
            raise EmailUnavailable()
    except (SMTPException, OSError, EmailUnavailable) as exc:
        # Keep the cooldown even when delivery fails; an older code stays invalid.
        raise EmailUnavailable() from exc
    EmailChallenge.objects.filter(key=key, nonce=nonce).update(delivered=True)


def verify_code(address, code, purpose, user=None):
    """Count every attempt outside the later account-creation transaction."""
    key = challenge_key(address, purpose, user.pk if user else None)
    now = timezone.now()
    candidates = EmailChallenge.objects.filter(
        key=key, delivered=True, expires_at__gt=now, attempts__lt=MAX_ATTEMPTS,
    )
    if not candidates.update(attempts=F("attempts") + 1):
        raise ValidationError({"code": "Request a new code. The previous code expired or reached its attempt limit."})
    row = EmailChallenge.objects.get(key=key)
    if not constant_time_compare(row.digest, digest(key, row.nonce, code)):
        raise ValidationError({"code": "The verification code is incorrect."})
    return row


def consume_code(row):
    """Call inside the same transaction as the associated account change."""
    claimed = EmailChallenge.objects.filter(
        key=row.key, nonce=row.nonce, delivered=True, expires_at__gt=timezone.now(),
    ).update(delivered=False)
    if claimed != 1:
        raise ValidationError({"code": "This code has already been used or replaced. Request a new code."})
