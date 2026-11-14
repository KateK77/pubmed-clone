import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from literature import ncbi
from literature.citations import FORMATS, citation

pytestmark = pytest.mark.django_db


def test_session_csrf_registration_and_login():
    client = APIClient(enforce_csrf_checks=True)
    body = {"username": "researcher", "password": "UnusualDemo!987"}
    assert client.post("/api/auth/register/", body, format="json").status_code == 403
    client.get("/api/session/")
    token = client.cookies["csrftoken"].value
    response = client.post("/api/auth/register/", body, format="json", HTTP_X_CSRFTOKEN=token)
    assert response.status_code == 200
    assert get_user_model().objects.get(username="researcher").check_password(body["password"])
    token = client.cookies["csrftoken"].value
    assert client.post("/api/auth/logout/", HTTP_X_CSRFTOKEN=token).status_code == 200
    assert client.get("/api/session/").json()["user"] is None
    token = client.cookies["csrftoken"].value
    assert client.post("/api/auth/login/", body, format="json", HTTP_X_CSRFTOKEN=token).status_code == 200


def test_library_and_history_isolation(monkeypatch, article):
    monkeypatch.setattr(ncbi, "detail", lambda pmid: article)
    monkeypatch.setattr(ncbi, "search", lambda options: {"count": 100, "results": []})
    first = get_user_model().objects.create_user("first")
    second = get_user_model().objects.create_user("second")
    client = APIClient()
    client.force_login(first)
    data = {"pmid": article["pmid"]}
    assert client.post("/api/bookmarks/", data, format="json").status_code == 201
    assert client.post("/api/bookmarks/", data, format="json").status_code == 200
    assert len(client.get("/api/bookmarks/").json()["results"]) == 1
    collection = client.post("/api/collections/", {"name": "Trials"}, format="json").json()
    path = f"/api/collections/{collection['id']}/"
    assert client.post(path + "articles/", data, format="json").status_code == 201
    assert client.patch(path, {"name": "Clinical trials"}, format="json").status_code == 200
    assert client.post("/api/search/record/", {"q": "asthma", "years": "5"}, format="json").status_code == 201
    assert client.get("/api/history/").json()[0]["filters"] == {"years": "5"}
    assert client.post("/api/saved-searches/", {"q": "asthma"}, format="json").status_code == 201
    client.force_login(second)
    assert client.get(path).status_code == 404
    assert client.post(path + "articles/", data, format="json").status_code == 404
    assert client.post("/api/citations/", {"format": "ris", "collection": collection["id"]}, format="json").status_code == 404
    assert client.get("/api/bookmarks/").json()["results"] == []
    assert client.get("/api/history/").json() == []
    assert client.get("/api/saved-searches/").json() == []
    client.force_login(first)
    assert client.delete("/api/bookmarks/" + article["pmid"] + "/").status_code == 204
    assert client.delete(path + "articles/" + article["pmid"] + "/").status_code == 204
    assert client.delete(path).status_code == 204
    assert client.delete("/api/history/").status_code == 204


@pytest.mark.parametrize("style", FORMATS)
def test_citation_export(style, monkeypatch, article):
    article.update(title="Lung & airway", authors=[{"name": "Ada Silva", "family": "Silva", "given": "Ada", "initials": "A"}])
    monkeypatch.setattr(ncbi, "fetch", lambda ids: [article])
    expected = citation(article, style)
    assert "Lung" in expected and "Silva" in expected
    assert "doi" not in expected.lower()
    response = APIClient().post("/api/citations/", {"ids": [article["pmid"]], "format": style}, format="json")
    assert response.status_code == 200
    assert response.content.decode().strip() == expected.strip()
    assert response["Content-Disposition"].endswith(FORMATS[style] + '"')


def test_invalid_pmid_and_no_query():
    client = APIClient()
    assert client.get("/api/publications/bad/").status_code == 400
    assert client.get("/api/search/").status_code == 400
