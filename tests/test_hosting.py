import pytest
from django.core.exceptions import ImproperlyConfigured
from medresearch.hosting import postgres_url


def test_hosted_database_url_preserves_credentials_and_tls():
    config = postgres_url("postgresql://research:p%40ss%2Fword@db.example.org:5432/medresearch?sslmode=verify-full&channel_binding=require")
    assert config["ENGINE"] == "django.db.backends.postgresql"
    assert config["PASSWORD"] == "p@ss/word" and config["NAME"] == "medresearch"
    assert config["OPTIONS"] == {"sslmode": "verify-full", "channel_binding": "require"}
    assert config["CONN_HEALTH_CHECKS"] is True
    assert postgres_url("postgres://a:b@db.example.org/research")["OPTIONS"]["sslmode"] == "require"


@pytest.mark.parametrize("url", ["sqlite:///db.sqlite3", "postgresql://user:secret@host:bad/db", "postgresql://user:secret@host/", "invalid://user:secret@host/db"])
def test_bad_hosting_url_never_discloses_secret(url):
    with pytest.raises(ImproperlyConfigured) as error:
        postgres_url(url)
    assert "secret" not in str(error.value)
