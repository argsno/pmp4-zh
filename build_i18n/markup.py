"""The placeholder grammar.

A translatable node is handed to the translator as near-plain text: inline
markup becomes 【N】…【/N】, indivisible content (math, code, images, nested
blocks) becomes 【MN】, and zero-width elements (page anchors, pagebreaks)
disappear entirely.  Translators therefore never touch a tag or an attribute,
and the placeholder set can be checked for strict equality.

Zero-width elements are tracked internally as 【ZN】 at their original position.
They are restored there when the node is untranslated and moved to the head of
the node otherwise — invisible either way, but it keeps the round-trip exact.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .spacing import normalize

CANDIDATE_TAGS = frozenset("p li h1 h2 h3 h4 figcaption td th caption".split())
CELL_TAGS = frozenset("td th caption".split())
ATOMIC_TAGS = frozenset("math pre img svg".split())
BLOCK_TAGS = frozenset(
    "address article aside blockquote caption div dl dd dt figcaption figure "
    "footer form h1 h2 h3 h4 h5 h6 header hr li math nav ol p pre section "
    "table tbody td tfoot th thead tr ul".split())
VISIBLE_VOID = frozenset("br hr img input".split())

PLACEHOLDER_RE = re.compile(r"【(/?)([MZ]?)(\d+)】")
_BARE_AMP_RE = re.compile(r"&(?![A-Za-z][A-Za-z0-9]*;|#\d+;|#[xX][0-9A-Fa-f]+;)")
_ID_ATTR_RE = re.compile(r'(<[^<>]*?)\s+id="[^"]*"')


@dataclass
class NodeMarkup:
    """One node's content, as text for the translator and parts to rebuild it."""
    text: str                              # what the translator sees
    source_text: str                       # the same, plus 【ZN】 anchors
    pairs: dict = field(default_factory=dict)         # n -> (open tag, close tag)
    atom_source: dict = field(default_factory=dict)   # n -> original HTML
    atom_elements: dict = field(default_factory=dict)  # n -> Element
    zero_width: dict = field(default_factory=dict)     # n -> original HTML


def extract_markup(doc, el, is_node=None):
    """Reduce one node to translator-facing text plus the parts to rebuild it."""
    extractor = _Extractor(doc, is_node or (lambda _el: False))
    extractor.walk(el)
    return NodeMarkup(
        text="".join(extractor.text),
        source_text="".join(extractor.source),
        pairs=extractor.pairs,
        atom_source=extractor.atom_source,
        atom_elements=extractor.atom_elements,
        zero_width=extractor.zero_width,
    )


def build(markup, translated, *, keep_zero_width=True, strip_ids=False,
          atom_html=None):
    """Rebuild a node's inner HTML from its translation."""
    atom_html = atom_html or {}
    if translated == markup.text:
        work = markup.source_text
    else:
        work = normalize(translated)
        if keep_zero_width and markup.zero_width:
            work = "".join("【Z%d】" % n
                           for n in sorted(markup.zero_width)) + work

    out = []
    position = 0
    for match in PLACEHOLDER_RE.finditer(work):
        out.append(escape(work[position:match.start()]))
        position = match.end()
        closing, kind, number = match.group(1), match.group(2), int(match.group(3))
        if kind == "Z":
            out.append(markup.zero_width[number] if keep_zero_width else "")
        elif kind == "M":
            html = atom_html.get(number, markup.atom_source[number])
            out.append(strip_ids_from(html) if strip_ids else html)
        else:
            tag = markup.pairs[number][1 if closing else 0]
            out.append(strip_ids_from(tag) if strip_ids else tag)
    out.append(escape(work[position:]))
    return "".join(out)


def escape(text):
    """Escape what a translator might type without touching source entities."""
    return _BARE_AMP_RE.sub("&amp;", text).replace("<", "&lt;")


def strip_ids_from(html):
    """Drop id attributes so a duplicated block cannot duplicate an anchor."""
    return _ID_ATTR_RE.sub(r"\1", html)


def add_class(open_tag, name):
    if re.search(r'\sclass="', open_tag):
        return re.sub(r'(\sclass="[^"]*)"', r"\1 " + name + '"', open_tag, count=1)
    return re.sub(r"(/?>)$", ' class="%s"\\1' % name, open_tag, count=1)


def set_attr(open_tag, name, value):
    pattern = r"(\s%s=\")[^\"]*\"" % re.escape(name)
    if re.search(pattern, open_tag):
        return re.sub(pattern, lambda m: m.group(1) + value + '"', open_tag, count=1)
    return re.sub(r"(/?>)$", ' %s="%s"\\1' % (name, value), open_tag, count=1)


class _Extractor:
    def __init__(self, doc, is_node):
        self.doc = doc
        self.is_node = is_node
        self.text = []
        self.source = []
        self.pairs = {}
        self.atom_source = {}
        self.atom_elements = {}
        self.zero_width = {}
        self._placeholders = 0
        self._anchors = 0

    def _emit(self, text):
        self.text.append(text)
        self.source.append(text)

    def walk(self, el):
        position = el.content_start
        for child in el.children:
            self._emit(self.doc.src[position:child.start])
            self._visit(child)
            position = child.end
        self._emit(self.doc.src[position:el.content_end])

    def _visit(self, el):
        kind = classify(self.doc, el, self.is_node)
        if kind == "zero":
            self._anchors += 1
            self.zero_width[self._anchors] = self.doc.source(el)
            self.source.append("【Z%d】" % self._anchors)
            return
        self._placeholders += 1
        number = self._placeholders
        if kind == "atom":
            self.atom_source[number] = self.doc.source(el)
            self.atom_elements[number] = el
            self._emit("【M%d】" % number)
            return
        self.pairs[number] = (self.doc.open_tag(el), self.doc.close_tag(el))
        self._emit("【%d】" % number)
        self.walk(el)
        self._emit("【/%d】" % number)


def classify(doc, el, is_node):
    """How a child element is presented to the translator."""
    if (el.tag not in VISIBLE_VOID and el.tag not in ATOMIC_TAGS
            and not el.children and doc.inner(el) == ""):
        return "zero"
    if el.tag in ATOMIC_TAGS or el.tag in BLOCK_TAGS or is_node(el):
        return "atom"
    if any(is_node(descendant) for descendant in el.descendants()):
        return "atom"
    if not _translatable_text(doc, el).strip():
        # A wrapper around nothing but a formula or an image is indivisible too.
        return "atom"
    return "pair"


def _translatable_text(doc, el):
    out = []

    def walk(node):
        position = node.content_start
        for child in node.children:
            out.append(doc.src[position:child.start])
            if child.tag not in ATOMIC_TAGS:
                walk(child)
            position = child.end
        out.append(doc.src[position:node.content_end])

    walk(el)
    return "".join(out)
