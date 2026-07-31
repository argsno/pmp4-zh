"""The terminology table, read out of TRANSLATION_STANDARDS.md.

The engine only ever reads the standards file: translation tasks run
concurrently and would clobber each other if any of them wrote to it.
"""
import os
import re

STANDARDS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "TRANSLATION_STANDARDS.md")

_ROW_RE = re.compile(r"^\|([^|]+)\|([^|]+)\|\s*$")
_SEPARATOR_RE = re.compile(r"^[\s:|-]+$")
_HEADERS = {"英文", "中文", "english", "chinese"}
_MIN_TERM_LENGTH = 4

_cache = {}


def load_glossary(path=STANDARDS_PATH):
    """English term -> mandated Chinese rendering, as written in the table."""
    if path not in _cache:
        _cache[path] = _parse(path)
    return _cache[path]


def _parse(path):
    glossary = {}
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            match = _ROW_RE.match(line.strip())
            if not match:
                continue
            english, chinese = (cell.strip() for cell in match.groups())
            if not english or _SEPARATOR_RE.match(english):
                continue
            if english.lower() in _HEADERS:
                continue
            glossary[english] = chinese
    return glossary


def offending_terms(english, chinese, glossary):
    """Glossary terms used in the source whose mandated rendering is missing.

    A translation satisfies a term when it carries the mandated Chinese, or
    when it keeps the English word — which covers both API names and the
    "线程束（warp）" form used at a term's first appearance.
    """
    offenders = []
    for entry_english, entry_chinese in glossary.items():
        renderings = _renderings(entry_chinese)
        if not renderings:
            continue
        for term in _terms(entry_english):
            if not _mentions(english, term):
                continue
            if any(rendering in chinese for rendering in renderings):
                break
            if _mentions(chinese, term):
                break
            offenders.append(term)
            break
    return offenders


def _terms(entry_english):
    for term in entry_english.split("/"):
        term = re.sub(r"[（(].*?[）)]", "", term).strip().strip("`")
        if len(term) >= _MIN_TERM_LENGTH and re.fullmatch(r"[\w' -]+", term):
            yield term


def _renderings(entry_chinese):
    """Accepted Chinese forms, or none when the term stays in English."""
    if "保留" in entry_chinese:
        return []
    forms = set()
    for form in re.split(r"[/、]", entry_chinese):
        form = form.strip()
        if not form:
            continue
        forms.add(form)
        forms.add(re.sub(r"[（(].*?[）)]", "", form).strip())
    return [form for form in forms if form]


def _mentions(text, term):
    return re.search(r"(?<![A-Za-z])%ss?(?![A-Za-z])" % re.escape(term),
                     text, re.IGNORECASE) is not None
