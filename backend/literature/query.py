import re
from datetime import date

from rest_framework.exceptions import ValidationError

TYPES = ("Clinical Trial", "Randomized Controlled Trial", "Review", "Systematic Review", "Meta-Analysis", "Case Report")
LANGUAGES = ("English", "Chinese", "French", "German", "Japanese", "Spanish", "Portuguese")
FILTERS = {
    "type": {value: f'"{value}"[pt]' for value in TYPES},
    "language": {value: f"{value}[la]" for value in LANGUAGES},
    "text": {"abstract": "hasabstract", "free": '"free full text"[filter]', "full": '"full text"[filter]'},
    "species": {"humans": "humans[filter]", "animals": '"other animals"[filter]'},
    "subset": {"medline": "medline[sb]", "no-preprints": "NOT preprint[pt]"},
}
SORTS = {"best": "relevance", "recent": "", "publication": "pub_date"}
FIELDS = {"all": "", "title": "ti", "author": "au", "journal": "ta", "abstract": "ab", "mesh": "mh", "date": "dp"}
PMID = re.compile(r"[1-9][0-9]{0,11}")


def validate_query(value, literal=False):
    if not isinstance(value, str) or not value.strip() or len(value) > 2500:
        raise ValidationError("Enter a search query of 1–2500 characters.")
    value = value.strip()
    if literal:
        if chr(34) in value.strip(chr(34)):
            raise ValidationError("Use one quoted phrase for a specific field.")
        return value
    stack = []
    quoted = False
    for char in value:
        if char == '"':
            quoted = not quoted
        elif not quoted and char in "([":
            stack.append(char)
        elif not quoted and char in ")]":
            if not stack or stack.pop() != {")": "(", "]": "["}[char]:
                raise ValidationError("Check matching parentheses and field brackets.")
    if stack or quoted:
        raise ValidationError("Close all quotes, parentheses, and field brackets.")
    syntax = re.sub(r'"[^"]*"|\[[^\]]*\]', "TERM", value)
    if re.search(r"(?:^|\()\s*(?:AND|OR|NOT)\b|\b(?:AND|OR|NOT)\s*(?:$|\)|(?:AND|OR|NOT)\b)|\(\s*\)", syntax):
        raise ValidationError("Supply a term on both sides of each Boolean operator.")
    return value


def integer(value, default, allowed=None):
    try:
        value = int(value if value is not None else default)
    except (TypeError, ValueError):
        raise ValidationError("Invalid pagination value.")
    if value < 1 or (allowed and value not in allowed):
        raise ValidationError("Invalid pagination value.")
    return value


def search_options(params):
    query = validate_query(params.get("q"))
    sort = params.get("sort", "best")
    if not isinstance(sort, str) or sort not in SORTS:
        raise ValidationError("Unknown sorting method.")
    filters = {}
    clauses = []
    exclusions = []
    for key, choices in FILTERS.items():
        raw = params.get(key, "")
        if not isinstance(raw, str):
            raise ValidationError(f"Invalid {key} filter.")
        values = sorted(set(filter(None, raw.split(","))))
        if any(value not in choices for value in values):
            raise ValidationError(f"Invalid {key} filter.")
        if values:
            filters[key] = ",".join(values)
            expressions = [choices[value] for value in values]
            exclusions.extend(item[4:] for item in expressions if item.startswith("NOT "))
            positive = [item for item in expressions if not item.startswith("NOT ")]
            if positive:
                clauses.append("(" + " OR ".join(positive) + ")")
    preset = params.get("years")
    start, end = params.get("from"), params.get("to")
    if any(value is not None and not isinstance(value, str) for value in (preset, start, end)):
        raise ValidationError("Enter a valid date filter.")
    if preset:
        if preset not in {"1", "5", "10"} or start or end:
            raise ValidationError("Choose one publication date filter.")
        today = date.today()
        start = today.replace(year=today.year - int(preset), day=min(today.day, 28) if today.month == 2 else today.day).isoformat()
        end = today.isoformat()
        filters["years"] = preset
    elif start or end:
        filters.update({"from": start or "", "to": end or ""})
    if start or end:
        try:
            lower = date.fromisoformat(start) if start else date(1000, 1, 1)
            upper = date.fromisoformat(end) if end else date(9999, 12, 31)
            if lower > upper:
                raise ValueError()
        except ValueError:
            raise ValidationError("Enter a valid date range.")
        clauses.append(f'({lower.isoformat().replace("-", "/")}:{upper.isoformat().replace("-", "/")}[dp])')
    term = query
    if PMID.fullmatch(query):
        term = f"{query}[uid]"
    elif query.startswith("10.") or query.startswith("https://doi.org/"):
        doi = query.removeprefix("https://doi.org/")
        if not re.fullmatch(r'10\.\d{4,9}/[^\s"\[\]]+', doi):
            raise ValidationError("Enter a valid DOI.")
        term = f'"{doi}"[aid]'
    if clauses or exclusions:
        term = " AND ".join([f"({term})", *clauses])
        term += "".join(f" NOT ({item})" for item in exclusions)
    size = integer(params.get("size"), 20, (10, 20, 50))
    page = integer(params.get("page"), 1)
    if (page - 1) * size >= 10000:
        raise ValidationError("PubMed exposes the first 10,000 matches. Refine your search.")
    return {"query": query, "filters": filters, "sort": sort, "term": term, "size": size, "page": page}


def build_query(rows):
    if not isinstance(rows, list) or not 1 <= len(rows) <= 20:
        raise ValidationError("Add 1–20 search conditions.")
    expression = ""
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValidationError("Invalid search condition.")
        field = row.get("field", "all")
        op = row.get("operator", "AND")
        if not isinstance(field, str) or field not in FIELDS or not isinstance(op, str) or op not in {"AND", "OR", "NOT"}:
            raise ValidationError("Choose a valid search field and operator.")
        term = validate_query(row.get("term"), literal=field != "all")
        if field == "date":
            if not re.fullmatch(r"\d{4}(?:/\d{2}(?:/\d{2})?)?(?::\d{4}(?:/\d{2}(?:/\d{2})?)?)?", term):
                raise ValidationError("Use YYYY, YYYY/MM/DD, or a colon-separated date range.")
            term = f"{term}[dp]"
        elif field != "all":
            term = f'"{term.strip(chr(34))}"[{FIELDS[field]}]'
        expression = f"({expression} {op} ({term}))" if index else f"({term})"
    return validate_query(expression)
