"""The hard gates.

A page that fails any of these is not written at all: a missing page is a
problem someone will fix, a subtly broken page is one nobody will notice.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from lxml import html as lxml_html

from .document import Document
from .glossary import offending_terms
from .markup import BLOCK_TAGS, PLACEHOLDER_RE, strip_ids_from
from .spacing import has_cjk

VERBATIM_TAGS = ("pre", "math")
_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'’-]{2,}")


@dataclass(frozen=True)
class Violation:
    rule: str
    message: str
    node_id: str = ""
    page: str = ""

    def __str__(self):
        where = "/".join(part for part in (self.page, self.node_id) if part)
        return "%s [%s] %s" % (where, self.rule, self.message)


def check_node(node_id, markup, chinese, glossary, require_translated, page):
    """First failing gate for one node, or None.

    Only the first is reported: a node whose placeholders are broken has
    nothing useful to say about its terminology.
    """
    def fail(rule, message):
        return Violation(rule=rule, message=message, node_id=node_id, page=page)

    if chinese is None:
        return fail("missing-translation", "no translation supplied")

    problem = _placeholder_problem(markup, chinese)
    if problem:
        return fail("placeholder-mismatch", problem)

    if not chinese.strip():
        return fail("untranslated", "translation is empty")

    if require_translated and _is_prose(markup.text) and not has_cjk(chinese):
        return fail("untranslated", "no Chinese in the translation of prose: %r"
                    % _clip(markup.text))

    if require_translated:
        offenders = offending_terms(markup.text, chinese, glossary)
        if offenders:
            return fail("glossary", "term(s) not rendered as the glossary "
                        "requires: %s" % ", ".join(offenders))
    return None


def check_page(english, chinese_html, page):
    """The Chinese page: the English page's structure, in Chinese.

    Same blocks in the same order, and the code and formulae between them
    untouched down to the byte.
    """
    rendered = Document(chinese_html)
    violations = _check_sound(english, rendered, chinese_html, page, "Chinese")

    expected, actual = _block_count(english), _block_count(rendered)
    if expected != actual:
        violations.append(Violation(
            rule="block-count", page=page,
            message="rendered page has %d block-level nodes, the English page "
                    "has %d" % (actual, expected)))

    if _verbatim(english) != _verbatim(rendered):
        violations.append(Violation(
            rule="verbatim-drift", page=page,
            message="code or formulae differ from the English page"))
    return violations


def check_bilingual(english, bilingual_html, page):
    """The bilingual page deliberately has twice the blocks, so it is not held
    to the English block count.  What still holds is that every piece of code
    or formula on it is one of the English page's, byte for byte — an inline
    formula inside a doubled sentence appears twice, but never altered, and
    nothing goes missing.
    """
    rendered = Document(bilingual_html)
    violations = _check_sound(english, rendered, bilingual_html, page,
                              "bilingual")

    # A doubled block loses its ids so the page cannot carry an anchor twice;
    # everything else about it must still be the English page's bytes.
    ours = {strip_ids_from(source) for source in _verbatim(rendered)}
    theirs = {strip_ids_from(source) for source in _verbatim(english)}
    if ours != theirs:
        violations.append(Violation(
            rule="verbatim-drift", page=page,
            message="%d code or formula block(s) missing and %d invented"
                    % (len(theirs - ours), len(ours - theirs))))
    return violations


def check_parses(html, page, what):
    try:
        lxml_html.fromstring(html.encode("utf-8"))
    except Exception as error:                      # pragma: no cover - lenient
        return [Violation(rule="unparsable", page=page,
                          message="%s page does not parse: %s" % (what, error))]
    return []


def content_elements(doc):
    """Everything outside the renderer-generated navigation."""
    header = doc.header()
    for el in doc:
        if header is not None and (el is header or header in set(el.ancestors())):
            continue
        yield el


def _check_sound(english, rendered, html, page, what):
    """Both gates that ask "is this still a page": tag balance and a parser."""
    violations = []
    stray = len(rendered.stray_end_tags) - len(english.stray_end_tags)
    unclosed = len(rendered.unclosed_tags) - len(english.unclosed_tags)
    if stray > 0 or unclosed > 0:
        violations.append(Violation(
            rule="unparsable", page=page,
            message="%s page has %d stray and %d unclosed tags more than the "
                    "source" % (what, max(stray, 0), max(unclosed, 0))))
    return violations + check_parses(html, page, what)


def _block_count(doc):
    return sum(1 for el in content_elements(doc) if el.tag in BLOCK_TAGS)


def _verbatim(doc):
    return [doc.source(el) for el in content_elements(doc)
            if el.tag in VERBATIM_TAGS]


def _is_prose(text):
    """Text a reader reads, as opposed to a label or a symbol.

    Identifiers and acronyms — `threadIdx.x`, `CUDA`, `GB/s` — stay in English
    on a fully translated page, so they cannot be held to "must contain
    Chinese".  A single ordinary word can: a heading reading `Introduction` is
    an untranslated heading, not a label.
    """
    words = _WORD_RE.findall(PLACEHOLDER_RE.sub(" ", text))
    return any(word == word.lower() or word == word.capitalize()
               for word in words)


def _clip(text, limit=60):
    return text if len(text) <= limit else text[:limit] + "…"


def _placeholder_problem(markup, chinese):
    expected_pairs = sorted(markup.pairs)
    expected_atoms = sorted(markup.atom_source)
    pairs, atoms, errors = _scan_placeholders(chinese)
    if errors:
        return "; ".join(errors)
    if sorted(pairs) != expected_pairs:
        return _difference("paired", expected_pairs, pairs)
    if sorted(atoms) != expected_atoms:
        return _difference("atomic", expected_atoms, atoms)
    return None


def _scan_placeholders(text):
    pairs, atoms, errors, stack = [], [], [], []
    for match in PLACEHOLDER_RE.finditer(text):
        closing, kind, number = match.group(1), match.group(2), int(match.group(3))
        if kind == "Z":
            errors.append("【Z%d】 is not a valid placeholder" % number)
        elif kind == "M":
            atoms.append(number)
        elif closing:
            if not stack or stack[-1] != number:
                errors.append("【/%d】 does not close the open placeholder" % number)
            else:
                stack.pop()
        else:
            pairs.append(number)
            stack.append(number)
    errors.extend("【%d】 is never closed" % number for number in stack)
    return pairs, atoms, errors


def _difference(kind, expected, actual):
    missing = sorted(set(expected) - set(actual))
    added = sorted(set(actual) - set(expected))
    repeated = sorted({n for n in actual if actual.count(n) > 1})
    parts = []
    if missing:
        parts.append("missing %s" % _names(kind, missing))
    if added:
        parts.append("unexpected %s" % _names(kind, added))
    if repeated:
        parts.append("repeated %s" % _names(kind, repeated))
    return "%s placeholders differ from the source: %s" % (kind, "; ".join(parts))


def _names(kind, numbers):
    pattern = "【M%d】" if kind == "atomic" else "【%d】"
    return ", ".join(pattern % number for number in numbers)
