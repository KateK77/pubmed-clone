import hashlib
import time
from threading import Lock

import requests
from defusedxml import ElementTree
from defusedxml.common import DefusedXmlException
from django.conf import settings
from django.core.cache import cache
from rest_framework.exceptions import APIException, NotFound

from .query import SORTS

BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
_lock = Lock()
_next_request = 0.0


class UpstreamError(APIException):
    status_code = 503
    default_detail = "PubMed is temporarily unavailable. Try again shortly."


def throttle():
    global _next_request
    with _lock:
        now = time.monotonic()
        time.sleep(max(0, _next_request - now))
        _next_request = time.monotonic() + (0.105 if settings.NCBI_API_KEY else 0.35)


def request(endpoint, params, xml=False):
    params = {"db": "pubmed", "tool": "medresearch", "retmode": "xml" if xml else "json", **params}
    key = "ncbi:" + hashlib.sha256(repr((endpoint, sorted(params.items()))).encode()).hexdigest()
    stored = cache.get(key)
    if stored is not None:
        return ElementTree.fromstring(stored) if xml else stored
    if settings.NCBI_EMAIL:
        params["email"] = settings.NCBI_EMAIL
    if settings.NCBI_API_KEY:
        params["api_key"] = settings.NCBI_API_KEY
    for attempt in range(3):
        throttle()
        try:
            response = requests.post(BASE + endpoint + ".fcgi", data=params, timeout=(5, 15))
            response.raise_for_status()
        except requests.RequestException as exc:
            status = exc.response.status_code if exc.response is not None else None
            if status is not None and status < 500 and status != 429:
                raise UpstreamError() from exc
            if attempt == 2:
                detail = "PubMed is rate limiting requests. Try again shortly." if status == 429 else None
                raise UpstreamError(detail) from exc
            retry = exc.response.headers.get("Retry-After", "") if exc.response is not None else ""
            time.sleep(min(10, int(retry)) if retry.isdecimal() else 2**attempt)
            continue
        try:
            data = ElementTree.fromstring(response.content) if xml else response.json()
            if xml:
                if data.tag not in {"PubmedArticleSet", "eLinkResult"} or data.find(".//ERROR") is not None:
                    raise ValueError()
            elif not isinstance(data, dict) or data.get("error") or not data.get({"esearch": "esearchresult", "esummary": "result"}[endpoint]):
                raise ValueError()
        except (ValueError, ElementTree.ParseError, DefusedXmlException) as exc:
            raise UpstreamError("PubMed returned an unreadable response.") from exc
        cache.set(key, response.content if xml else data, settings.NCBI_CACHE_SECONDS)
        return data


def content(node):
    return "".join(node.itertext()).strip() if node is not None else ""


def normalize(record):
    medline = record.find("MedlineCitation")
    book = record.find("BookDocument")
    if medline is None and book is None:
        return None
    article = medline.find("Article") if medline is not None else book
    citation = medline if medline is not None else book
    if article is None:
        return None
    pmid = citation.findtext("PMID", "")
    title = content(article.find("ArticleTitle")) or content(article.find("Book/BookTitle"))
    if not pmid or not title:
        return None
    ids = {
        node.get("IdType"): content(node)
        for node in record.findall(".//PubmedData/ArticleIdList/ArticleId")
        + record.findall(".//PubmedBookData/ArticleIdList/ArticleId")
    }
    authors = []
    for author in article.findall("AuthorList/Author"):
        family = author.findtext("LastName", "")
        given = author.findtext("ForeName") or author.findtext("Initials", "")
        collective = author.findtext("CollectiveName", "")
        suffix = author.findtext("Suffix", "")
        name = collective or " ".join(filter(None, (given, family, suffix)))
        if name:
            authors.append({"name": name, "family": family, "given": given,
                            "suffix": suffix,
                            "initials": author.findtext("Initials", ""),
                            "affiliations": [content(item) for item in author.findall("AffiliationInfo/Affiliation")]})
    issue = article.find("Journal/JournalIssue")
    date = article.find("ArticleDate")
    if date is None:
        date = article.find("Journal/JournalIssue/PubDate")
    if date is None:
        date = article.find("Book/PubDate")
    year = date.findtext("Year", "") if date is not None else ""
    date_text = ""
    if date is not None:
        date_text = date.findtext("MedlineDate") or " ".join(date.findtext(field, "") for field in ("Year", "Month", "Day")).strip()
    if not year and date_text[:4].isdigit():
        year = date_text[:4]
    abstract = []
    for section in article.findall("Abstract/AbstractText"):
        value = content(section)
        if value:
            abstract.append({"label": section.get("Label", ""), "text": value})
    references = [
        {"citation": content(item.find("Citation")), "pmid": item.findtext("ArticleIdList/ArticleId[@IdType='pubmed']", "")}
        for item in record.findall(".//Reference")
    ]
    return {
        "metadata_version": 2,
        "pmid": pmid, "pmcid": ids.get("pmc", ""), "doi": ids.get("doi") or article.findtext("ELocationID[@EIdType='doi']", ""),
        "title": title, "authors": authors, "abstract": abstract,
        "journal": article.findtext("Journal/Title") or content(article.find("Book/BookTitle")),
        "journal_abbr": article.findtext("Journal/ISOAbbreviation", ""),
        "date": date_text, "year": year,
        "volume": issue.findtext("Volume", "") if issue is not None else "",
        "issue": issue.findtext("Issue", "") if issue is not None else "",
        "pages": article.findtext("Pagination/MedlinePgn", ""),
        "types": [content(item) for item in article.findall("PublicationTypeList/PublicationType")],
        "keywords": [content(item) for item in citation.findall("KeywordList/Keyword")],
        "mesh": [content(item) for item in citation.findall("MeshHeadingList/MeshHeading/DescriptorName")],
        "references": references,
    }


def fetch(ids):
    if not ids:
        return []
    root = request("efetch", {"id": ",".join(ids)}, xml=True)
    parsed = [item for node in root for item in [normalize(node)] if item]
    records = {item["pmid"]: item for item in parsed}
    return [records[pmid] for pmid in ids if pmid in records]


def detail(pmid):
    records = fetch([pmid])
    if not records:
        raise NotFound("Publication not found.")
    return records[0]


def search(options):
    sort = SORTS[options["sort"]]
    payload = request("esearch", {
        "term": options["term"], **({"sort": sort} if sort else {}),
        "retstart": (options["page"] - 1) * options["size"], "retmax": options["size"],
    })["esearchresult"]
    if payload.get("errorlist") or payload.get("ERROR"):
        from rest_framework.exceptions import ValidationError
        raise ValidationError("PubMed could not interpret the query. Check the terms and field tags.")
    try:
        count, ids = int(payload["count"]), payload["idlist"]
        if count < 0 or not isinstance(ids, list) or any(not isinstance(pmid, str) or not pmid.isdecimal() for pmid in ids):
            raise ValueError()
    except (KeyError, TypeError, ValueError) as exc:
        raise UpstreamError("PubMed returned an incomplete search response.") from exc
    results = fetch(ids)
    offset = (options["page"] - 1) * options["size"]
    expected = max(0, min(options["size"], min(count, 10000) - offset))
    return {"count": count, "accessible_count": min(count, 10000), "results": results,
            "partial": len(results) != expected, "translation": payload.get("querytranslation", "")}


def related(pmid, cited=False):
    name = "pubmed_pubmed_citedin" if cited else "pubmed_pubmed"
    root = request("elink", {"dbfrom": "pubmed", "id": pmid, "linkname": name}, xml=True)
    ids = [
        node.findtext("Id") for group in root.findall("LinkSet/LinkSetDb")
        if group.findtext("LinkName") == name for node in group.findall("Link")
    ]
    ids = list(dict.fromkeys(item for item in ids if item and item != pmid))[:8]
    if not ids:
        return []
    result = request("esummary", {"id": ",".join(ids)})["result"]
    return [{
        "pmid": uid, "title": result[uid]["title"], "journal": result[uid].get("fulljournalname", ""),
        "year": result[uid].get("pubdate", "")[:4],
        "authors": [{"name": a["name"]} for a in result[uid].get("authors", []) if a.get("name")],
    } for uid in ids if isinstance(result.get(uid), dict) and result[uid].get("title")]
