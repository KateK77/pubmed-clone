import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def article():
    return {
        "pmid": "31452104", "title": "Fixture title", "journal": "Fixture journal",
        "journal_abbr": "", "date": "2019 Aug 29", "year": "2019", "pmcid": "", "doi": "",
        "volume": "", "issue": "", "pages": "", "abstract": [], "authors": [],
    }
