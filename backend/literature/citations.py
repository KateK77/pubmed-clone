import re

FORMATS = {"apa": "txt", "mla": "txt", "vancouver": "txt", "bibtex": "bib", "ris": "ris"}


def names(article, style):
    values = []
    for author in article["authors"]:
        family, initials = author.get("family"), author.get("initials", "")
        suffix = author.get("suffix", "")
        if not family:
            values.append(author["name"])
        elif style == "apa":
            name = f"{family}, {' '.join(letter + '.' for letter in initials)}".rstrip(", ")
            values.append(name + (f", {suffix}" if suffix else ""))
        elif style == "vancouver":
            values.append(" ".join(filter(None, (family, initials, suffix))))
        elif style == "bibtex":
            values.append(", ".join(filter(None, (family, suffix, author.get("given")))))
        else:
            values.append(", ".join(filter(None, (family, author.get("given"), suffix))))
    return values


def sentence(value):
    return value if not value or value[-1] in ".?!" else value + "."


def citation(article, style):
    authors = names(article, style)
    title, journal, year = (article[key] for key in ("title", "journal", "year"))
    volume, issue, pages, doi = (article[key] for key in ("volume", "issue", "pages", "doi"))
    doi_url = f"https://doi.org/{doi}" if doi else ""
    if style == "apa":
        if len(authors) > 20:
            author_text = ", ".join(authors[:19]) + ", … " + authors[-1]
        else:
            author_text = ", ".join(authors[:-1]) + ", & " + authors[-1] if len(authors) > 1 else "".join(authors)
        periodical = ", ".join(filter(None, (journal, volume + (f"({issue})" if issue else ""), pages)))
        return " ".join(filter(None, (sentence(author_text), f"({year or 'n.d.'}).", sentence(title), sentence(periodical), doi_url)))
    if style == "mla":
        author_text = authors[0] + ", et al." if len(authors) > 2 else " and ".join(authors)
        source = ", ".join(filter(None, (journal, f"vol. {volume}" if volume else "", f"no. {issue}" if issue else "", year, f"pp. {pages}" if pages else "", doi_url)))
        return " ".join(filter(None, (sentence(author_text), f'“{sentence(title)}”', sentence(source))))
    if style == "vancouver":
        author_text = ", ".join(authors[:6]) + (", et al." if len(authors) > 6 else "")
        issue_text = volume + (f"({issue})" if issue else "")
        source = year + (";" + issue_text if issue_text else "") + (":" + pages if pages else "")
        return " ".join(filter(None, (sentence(author_text), sentence(title), sentence(article.get("journal_abbr") or journal), sentence(source), f"doi: {doi}" if doi else "")))
    if style == "bibtex":
        mapping = {"title": title, "author": " and ".join(authors), "journal": journal, "year": year,
                   "volume": volume, "number": issue, "pages": pages, "doi": doi}
        replacements = {char: "\\" + char for char in "&%$#_{}"}
        replacements.update({"\\": r"\textbackslash{}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"})
        def escape(value):
            return "".join(replacements.get(char, char) for char in value)
        fields = ",\n".join(f"  {key} = {{{escape(value)}}}" for key, value in mapping.items() if value)
        return f"@article{{pmid{article['pmid']},\n{fields}\n}}"
    parts = re.split(r"[-–]", pages, maxsplit=1)
    start, end = (parts + [""])[:2]
    rows = [("TY", "JOUR"), ("TI", title), *[("AU", name) for name in authors], ("JO", journal),
            ("PY", year), ("VL", volume), ("IS", issue), ("SP", start), ("EP", end),
            ("DO", doi), ("AN", article["pmid"])]
    return "\n".join(f"{tag}  - {' '.join(value.split())}" for tag, value in rows if value) + "\nER  - "
