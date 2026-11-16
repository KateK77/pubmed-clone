"""Run separately with python tests/live_smoke.py from the project root."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "medresearch.settings")

import django

django.setup()

from literature import ncbi
from literature.citations import citation
from literature.query import search_options


def main():
    pmid = "31452104"
    result = ncbi.search(search_options({"q": pmid, "size": "10"}))
    assert result["count"] == 1 and result["results"][0]["pmid"] == pmid
    article = ncbi.detail(pmid)
    assert article["title"] and article["journal"]
    assert article["authors"][-1]["suffix"] == "Jr"
    assert "Jr" in citation(article, "apa")
    assert "Jr" in citation(article, "ris")
    links = ncbi.related(pmid)
    assert links and links[0]["pmid"] != pmid
    print(f"PubMed PMID {pmid}: {article['title']} ({len(links)} related records)")
    filtered = ncbi.search(search_options({"q": "asthma", "type": "Review", "years": "5", "size": "10"}))
    assert filtered["count"] > 0 and filtered["results"]
    print(f"Live filtered asthma search: {filtered['count']} matches")


if __name__ == "__main__":
    main()
