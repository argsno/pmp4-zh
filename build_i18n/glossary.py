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

# Phrases in which a glossary word is being used as ordinary English rather
# than as the term the table mandates.  These are a denylist, not an
# allowlist: only the collocations listed here are excused, so a bare
# technical `reduction` is still held to 归约.  Excusing the word wholesale
# would silently stop enforcing terminology in the chapters that use it most.
#
# Extend this when a page reports a false positive.  An ordinary phrase that
# is missing from the list produces a loud violation, which is the safe way
# to fail — the translator must report it rather than reach for the
# keep-the-English escape, which passes the gate by writing a bogus
# 首现 gloss (成本的迅速下降（reduction）) into the Chinese.
_ORDINARY_USAGE = tuple(re.compile(pattern, re.IGNORECASE) for pattern in (
    r"building blocks?",
    r"processing blocks?",
    r"wiring\s+blocks?",
    r"routing\s+blocks?",
    r"used\s+blocks?",
    r"a\s+block\s+is\s+occupied\b",
    r"each\s+block\s+can\s+potentially\b",
    r"from\s+block\b.{0,15}?to\s+block\b",
    r"small tiles?",
    r"bank\s+account",
    r"hosts?\s+(?:a\s+maximum|up\s+to)",
    r"\bto\s+host\s+(?:the|a|an)\b",
    r"CUDA\s+aware\s+message\s+passing\s+interface",
    r"\bin\s*-?\s*core\b",
    r"device\s+feature\s+size",
    r"(?:cost|price|area|power|energy|size)\s+reductions?",
    r"reductions?\s+in\s+(?:area|power|cost|price|energy|size)",
    r"reductions?\s+in\s+(?:the\s+)?(?:number|amount|level|degree)\s+of\b",
    r"reductions?\s+in\s+hardware\s+manufacturing\s+cost\b",
    r"reductions?\s+in\s+(?:occupancy|parallelism|performance|latency|time|overhead|computation)s?\b",
    r"reductions?\s+in\s+(?:the\s+)?execution\s+time\b",
    r"reductions?\s+in\s+application\b",
    r"speed\s+reductions?",
    r"reductions?\s+of\s+(?:memory\s+)?usages?\b",
    r"reductions?\s+(?:in|of)\s+(?:global\s+)?memory\s+(?:accesses|traffic|bandwidth)s?\b",
    r"memory\s+bandwidth\s+reductions?\b",
    r"reductions?\s+of\s+(?:the\s+)?(?:accesses|traffic)s?\s+to\s+(?:the\s+)?(?:global\s+)?memory\b",
    r"reductions?\s+of\s+(?:the\s+)?(?:number|amount|level|degree)\s+of\b",
    r"reductions?\s+of\s+(?:control\s+divergence|padding\s+overhead|overhead|divergence)s?\b",
    r"reductions?\s+from\b",
    r"siz(?:e|able)\s+reductions?\b",
    r"reductions?\s+is\s+(?:by|a)\b",
    r"barriers?\s+to\b",
))

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

    A shorter term whose occurrence is contained within a longer matched term
    is suppressed: the bare ``bank`` inside ``filter bank`` is not the
    shared-memory ``bank`` the glossary mandates, so it must not force 存储体
    onto a node that correctly says 滤波器组.

    An occurrence inside one of the ``_ORDINARY_USAGE`` collocations is
    suppressed for the same reason: ``cost reductions`` is everyday English,
    not the 归约 parallel pattern.
    """
    ordinary = [match.span() for pattern in _ORDINARY_USAGE
                for match in pattern.finditer(english)]
    matches = []  # (term, start, end, satisfied)
    for entry_english, entry_chinese in glossary.items():
        renderings = _renderings(entry_chinese)
        if not renderings:
            continue
        for term in _terms(entry_english):
            for match in _term_re(term).finditer(english):
                satisfied = (any(rendering in chinese for rendering in renderings)
                             or _mentions(chinese, term))
                matches.append((term, match.start(), match.end(), satisfied))
    offenders = []
    for term, start, end, satisfied in matches:
        if satisfied:
            continue
        if any(start_ <= start and end <= end_ and other != term
               for other, start_, end_, _ in matches):
            continue
        if any(start_ <= start and end <= end_ for start_, end_ in ordinary):
            continue
        offenders.append(term)
    return list(dict.fromkeys(offenders))


def _terms(entry_english):
    for term in entry_english.split("/"):
        term = re.sub(r"[（(].*?[）)]", "", term).strip().strip("`")
        if len(term) >= _MIN_TERM_LENGTH and re.fullmatch(r"[\w' -]+", term):
            yield term


def _term_re(term):
    """Match a glossary term as a whole word, singular or plural."""
    return re.compile(r"(?<![A-Za-z])%ss?(?![A-Za-z])" % re.escape(term),
                      re.IGNORECASE)


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
    return _term_re(term).search(text) is not None
