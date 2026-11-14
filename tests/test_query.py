import pytest
from rest_framework.exceptions import ValidationError

from literature.query import build_query, search_options


@pytest.mark.parametrize(("query", "term"), [
    ("asthma", "asthma"), ("31452104", "31452104[uid]"),
    ("Smith J[au]", "Smith J[au]"), ("Nature[ta]", "Nature[ta]"),
    ("10.1000/a-b", '"10.1000/a-b"[aid]'),
])
def test_search_terms(query, term):
    assert search_options({"q": query})["term"] == term


@pytest.mark.parametrize("query", ["", " (asthma", 'cancer AND', "OR cancer", "a NOT OR b", "10.1000/"])
def test_invalid(query):
    with pytest.raises(ValidationError):
        search_options({"q": query})


def test_filters_and_reset():
    options = search_options({"q": "asthma", "years": "5", "type": "Review,Case Report",
                              "text": "free", "subset": "medline,no-preprints"})
    assert '"Review"[pt]' in options["term"]
    assert '"Case Report"[pt] OR "Review"[pt]' in options["term"]
    assert '[dp]' in options["term"] and '[filter]' in options["term"]
    assert "AND (medline[sb])" in options["term"]
    assert options["term"].endswith("NOT (preprint[pt])")
    assert search_options({"q": "asthma"})["filters"] == {}


def test_range_and_paging_limits():
    with pytest.raises(ValidationError):
        search_options({"q": "asthma", "from": "2026-10-01", "to": "2025-10-01"})
    with pytest.raises(ValidationError):
        search_options({"q": "asthma", "page": "201", "size": "50"})


def test_grouped_boolean_query():
    result = build_query([
        {"term": '"large language models" OR LLM'},
        {"term": "health records", "field": "title", "operator": "AND"},
        {"term": "preprint", "field": "all", "operator": "NOT"},
        {"term": "Nature", "field": "journal", "operator": "OR"},
    ])
    assert result == '(((("large language models" OR LLM) AND ("health records"[ti])) NOT (preprint)) OR ("Nature"[ta]))'
