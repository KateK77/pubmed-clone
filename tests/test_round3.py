import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize("password", ["abcdefgh", "12345678", "password", "x" * 128])
def test_simple_passwords_register_and_login(settings, password):
    settings.EMAIL_VERIFICATION_REQUIRED = False
    client = APIClient()
    response = client.post("/api/auth/register/", {
        "username": "simple", "password": password, "password_confirmation": password,
    }, format="json")
    assert response.status_code == 200
    user = get_user_model().objects.get(username="simple")
    assert user.check_password(password) and user.password != password
    assert not user.first_name and not user.last_name
    client.logout()
    assert client.post("/api/auth/login/", {"username": "simple", "password": password}, format="json").status_code == 200


@pytest.mark.parametrize("password,confirmation,field", [
    ("abcdefg", "abcdefg", "password"),
    ("x" * 129, "x" * 129, "password"),
    ("abcdefgh", None, "password_confirmation"),
    ("abcdefgh", "", "password_confirmation"),
    ("abcdefgh", "abcdefgi", "password_confirmation"),
])
def test_invalid_registration_creates_no_account(settings, password, confirmation, field):
    settings.EMAIL_VERIFICATION_REQUIRED = False
    data = {"username": "invalid", "password": password}
    if confirmation is not None:
        data["password_confirmation"] = confirmation
    response = APIClient().post("/api/auth/register/", data, format="json")
    assert response.status_code == 400 and field in response.json()
    assert not get_user_model().objects.filter(username="invalid").exists()


def test_password_change_confirmation_and_existing_login():
    user = get_user_model().objects.create_user("existing", password="Old-password!9376", first_name="Preserved")
    client = APIClient()
    client.force_login(user)
    body = {"current_password": "Old-password!9376", "password": "abcdefgh"}
    for confirmation in (None, "different"):
        data = body if confirmation is None else {**body, "password_confirmation": confirmation}
        response = client.patch("/api/profile/", data, format="json")
        assert response.status_code == 400 and "password_confirmation" in response.json()
        user.refresh_from_db()
        assert user.check_password("Old-password!9376")
    response = client.patch("/api/profile/", {**body, "password_confirmation": "abcdefgh"}, format="json")
    assert response.status_code == 200
    assert client.get("/api/session/").json()["user"]["id"] == user.pk
    user.refresh_from_db()
    assert user.first_name == "Preserved" and user.check_password("abcdefgh")
    client.logout()
    assert client.post("/api/auth/login/", {"username": "existing", "password": "abcdefgh"}, format="json").status_code == 200


def test_account_throttle_remains_twenty_per_minute():
    client = APIClient()
    for _ in range(20):
        assert client.post("/api/auth/login/", {"username": "missing", "password": "abcdefgh"}, format="json").status_code == 400
    assert client.post("/api/auth/login/", {"username": "missing", "password": "abcdefgh"}, format="json").status_code == 429
