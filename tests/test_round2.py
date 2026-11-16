import re
from datetime import timedelta
from unittest.mock import Mock

import pytest
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils import timezone
from rest_framework.test import APIClient

from literature import email_verification, ncbi
from literature.citations import FORMATS, citation
from literature.models import AccountEmail, Bookmark, EmailChallenge, Publication

pytestmark = pytest.mark.django_db


@pytest.fixture
def client(settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    settings.DEFAULT_FROM_EMAIL = "research@example.org"
    settings.EMAIL_VERIFICATION_REQUIRED = True
    return APIClient()


def code_from_email():
    return re.search(r"code is (\d{6})", mail.outbox[-1].body).group(1)


def test_profile_empty_password_fields_and_persistence(client):
    user = get_user_model().objects.create_user("profile-test", password="UnusualDemo!987")
    client.force_login(user)
    response = client.patch("/api/profile/", {
        "first_name": "Test", "last_name": "Researcher", "email": "",
        "password": "", "current_password": "",
    }, format="json")
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == "Test" and user.last_name == "Researcher"
    assert user.check_password("UnusualDemo!987")
    client.logout()
    assert client.login(username=user.username, password="UnusualDemo!987")
    assert client.get("/api/session/").json()["user"]["first_name"] == "Test"


def test_failed_profile_changes_are_atomic(client):
    user = get_user_model().objects.create_user("atomic", password="UnusualDemo!987", first_name="Before")
    client.force_login(user)
    response = client.patch("/api/profile/", {
        "first_name": "After", "current_password": "wrong", "password": "ReplacementPass!987",
    }, format="json")
    assert response.status_code == 400 and "current_password" in response.json()
    user.refresh_from_db()
    assert user.first_name == "Before" and user.check_password("UnusualDemo!987")


def test_session_isolation_and_expiry(settings):
    client = APIClient(enforce_csrf_checks=True)
    user = get_user_model().objects.create_user("cookies", password="UnusualDemo!987")
    client.force_login(user)
    client.get("/api/session/")
    client.cookies["sessionid"] = "another-local-application"
    client.cookies["csrftoken"] = "another-local-application"
    response = client.patch("/api/profile/", {"first_name": "Works"}, format="json",
                            HTTP_X_CSRFTOKEN=client.cookies[settings.CSRF_COOKIE_NAME].value)
    assert response.status_code == 200
    client.cookies[settings.SESSION_COOKIE_NAME] = "expired"
    response = client.patch("/api/profile/", {"first_name": "Lost"}, format="json")
    assert response.status_code == 403
    assert response.json()["code"] == "authentication_required"
    assert "no-store" in client.get("/api/session/")["Cache-Control"]


def test_verified_registration_resend_and_single_use(client):
    email = "new@example.org"
    assert client.post("/api/auth/email-code/", {"email": email, "purpose": "register"}, format="json").status_code == 200
    assert len(mail.outbox) == 1
    code = code_from_email()
    assert code not in EmailChallenge.objects.get().digest
    assert client.post("/api/auth/email-code/", {"email": email, "purpose": "register"}, format="json").status_code == 429
    body = {"username": "verified", "password": "UnusualDemo!987", "email": email.upper(), "code": code}
    response = client.post("/api/auth/register/", body, format="json")
    assert response.status_code == 200 and response.json()["user"]["email_verified"]
    assert AccountEmail.objects.get().address == email
    assert not EmailChallenge.objects.get().delivered
    client.post("/api/auth/logout/")
    with pytest.raises(Exception, match="Request a new code"):
        email_verification.verify_code(email, code, "register")
    assert client.post("/api/auth/register/", {**body, "username": "duplicate"}, format="json").status_code == 400


def test_wrong_codes_expiry_and_resend_replaces_code(client):
    email = "attempts@example.org"
    email_verification.send_code(email, "register")
    old = code_from_email()
    wrong = "000000" if old != "000000" else "111111"
    body = {"username": "attempts", "password": "UnusualDemo!987", "email": email, "code": wrong}
    for _ in range(5):
        assert client.post("/api/auth/register/", body, format="json").status_code == 400
    assert EmailChallenge.objects.get().attempts == 5
    assert client.post("/api/auth/register/", {**body, "code": old}, format="json").status_code == 400
    EmailChallenge.objects.update(sent_at=timezone.now() - timedelta(minutes=1))
    email_verification.send_code(email, "register")
    assert EmailChallenge.objects.get().attempts == 0
    EmailChallenge.objects.update(expires_at=timezone.now() - timedelta(seconds=1))
    assert client.post("/api/auth/register/", {**body, "code": code_from_email()}, format="json").status_code == 400
    assert not get_user_model().objects.filter(username="attempts").exists()


def test_email_change_requires_code_for_current_user(client):
    user = get_user_model().objects.create_user("email-change", password="UnusualDemo!987", email="old@example.org")
    client.force_login(user)
    email = "replacement@example.org"
    body = {"email": email, "first_name": "Changed"}
    assert client.patch("/api/profile/", body, format="json").status_code == 400
    assert client.post("/api/auth/email-code/", {"email": email, "purpose": "profile"}, format="json").status_code == 200
    code = code_from_email()
    response = client.patch("/api/profile/", {**body, "code": code}, format="json")
    assert response.status_code == 200 and response.json()["user"]["email_verified"]
    user.refresh_from_db()
    assert user.email == email and user.first_name == "Changed"


def test_email_delivery_failure_and_missing_configuration(client, monkeypatch, settings):
    monkeypatch.setattr(email_verification, "send_mail", Mock(side_effect=OSError("SMTP unavailable")))
    response = client.post("/api/auth/email-code/", {"email": "failed@example.org", "purpose": "register"}, format="json")
    assert response.status_code == 503 and not EmailChallenge.objects.get().delivered
    assert "SMTP unavailable" not in str(response.json())
    settings.EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    settings.EMAIL_HOST = ""
    assert client.get("/api/session/").json()["email_delivery_available"] is False


def test_email_code_endpoint_csrf(settings):
    client = APIClient(enforce_csrf_checks=True)
    assert client.post("/api/auth/email-code/", {"email": "csrf@example.org", "purpose": "register"}, format="json").status_code == 403


def test_author_suffix_and_legacy_bookmark_export(client, monkeypatch, article):
    xml = b'''<PubmedArticle><MedlineCitation><PMID>31452104</PMID><Article>
    <ArticleTitle>Fixture title</ArticleTitle><AuthorList><Author><LastName>de Azevedo</LastName>
    <ForeName>Walter Filgueira</ForeName><Initials>WF</Initials><Suffix>Jr</Suffix></Author></AuthorList>
    </Article></MedlineCitation></PubmedArticle>'''
    normalized = ncbi.normalize(ncbi.ElementTree.fromstring(xml))
    assert normalized["authors"][0]["name"] == "Walter Filgueira de Azevedo Jr"
    assert normalized["authors"][0]["suffix"] == "Jr"
    for style in FORMATS:
        assert "Jr" in citation(normalized, style)
    assert "de Azevedo, Jr, Walter Filgueira" in citation(normalized, "bibtex")
    old = {**article, "metadata_version": 1, "authors": [{"name": "Walter Filgueira de Azevedo"}]}
    saved = Publication.objects.create(pmid=article["pmid"], title=article["title"], metadata=old)
    user = get_user_model().objects.create_user("legacy")
    Bookmark.objects.create(user=user, publication=saved)
    client.force_login(user)
    fetch = Mock(return_value=[normalized])
    monkeypatch.setattr(ncbi, "fetch", fetch)
    result = client.get("/api/bookmarks/").json()["results"][0]
    assert result["authors"][0]["suffix"] == "Jr"
    saved.refresh_from_db()
    assert saved.metadata["metadata_version"] == 2
    assert "Jr" in client.post("/api/citations/", {"format": "ris", "bookmarks": True}, format="json").content.decode()
    assert fetch.call_count == 1
