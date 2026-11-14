from unittest.mock import Mock

import pytest
import requests

from literature import ncbi
from literature.query import search_options

XML = b"""<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>31452104</PMID>
<Article><ArticleTitle>Title <i>with markup</i></ArticleTitle><Journal><Title>Journal</Title>
<JournalIssue><PubDate><MedlineDate>2019 Sep-Oct</MedlineDate></PubDate></JournalIssue></Journal>
<AuthorList><Author><LastName>Example</LastName><ForeName>Ada</ForeName><Initials>A</Initials>
<AffiliationInfo><Affiliation>Institute</Affiliation></AffiliationInfo></Author></AuthorList>
</Article></MedlineCitation></PubmedArticle></PubmedArticleSet>"""


def mock_response(payload=None, content=b""):
    result = Mock(content=content)
    result.json.return_value = payload
    return result


def test_batch_order_partial_and_count(monkeypatch):
    post = Mock(side_effect=[
        mock_response({"esearchresult": {"count": "12745", "idlist": ["31452104", "123"]}}),
        mock_response(content=XML),
    ])
    monkeypatch.setattr(ncbi.requests, "post", post)
    result = ncbi.search(search_options({"q": "asthma", "page": "2", "size": "50"}))
    assert result["count"] == 12745 and result["accessible_count"] == 10000
    assert result["partial"] is True
    item = result["results"][0]
    assert item["pmid"] == "31452104"
    assert item["title"] == "Title with markup" and item["year"] == "2019"
    assert item["authors"][0]["affiliations"] == ["Institute"]
    assert not item["doi"] and not item["abstract"]
    assert post.call_args_list[0].kwargs["data"]["retstart"] == 50
    assert post.call_args_list[1].kwargs["data"]["id"] == "31452104,123"


def test_empty_search(monkeypatch):
    post = Mock(return_value=mock_response({"esearchresult": {"count": "0", "idlist": []}}))
    monkeypatch.setattr(ncbi.requests, "post", post)
    assert ncbi.search(search_options({"q": "asthma"}))["results"] == []
    assert post.call_count == 1


def test_related_relationship(monkeypatch):
    post = Mock(side_effect=[
        mock_response(content=b"<eLinkResult><LinkSet><LinkSetDb><LinkName>pubmed_pubmed</LinkName><Link><Id>123</Id></Link></LinkSetDb></LinkSet></eLinkResult>"),
        mock_response({"result": {"123": {"title": "Another title", "pubdate": "2021", "fulljournalname": "Journal"}}}),
    ])
    monkeypatch.setattr(ncbi.requests, "post", post)
    assert ncbi.related("31452104")[0]["pmid"] == "123"
    assert "esummary" in post.call_args.args[0]


def test_timeout_retry_then_cache(monkeypatch):
    monkeypatch.setattr(ncbi.time, "sleep", Mock())
    post = Mock(side_effect=[requests.Timeout(), mock_response(content=XML)])
    monkeypatch.setattr(ncbi.requests, "post", post)
    assert ncbi.detail("31452104") == ncbi.detail("31452104")
    assert post.call_count == 2


def test_rate_limit(monkeypatch):
    monkeypatch.setattr(ncbi.time, "sleep", Mock())
    response = requests.Response()
    response.status_code = 429
    response.headers["Retry-After"] = "1"
    post = Mock(side_effect=requests.HTTPError(response=response))
    monkeypatch.setattr(ncbi.requests, "post", post)
    with pytest.raises(ncbi.UpstreamError, match="rate limiting"):
        ncbi.detail("31452104")
    assert post.call_count == 3


def test_invalid_response_not_cached(monkeypatch):
    post = Mock(side_effect=[mock_response(content=b"broken"), mock_response(content=XML)])
    monkeypatch.setattr(ncbi.requests, "post", post)
    with pytest.raises(ncbi.UpstreamError, match="unreadable"):
        ncbi.detail("31452104")
    assert ncbi.detail("31452104")["pmid"] == "31452104"
