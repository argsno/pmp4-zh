"""The rendering seam: one English page plus its translations, two pages out.

Extraction, the placeholder grammar, injection, bilingual interleaving, spacing
and every hard validation live behind `render()`.  Nothing above this line
knows how a node is taken apart, which is what lets the pieces be rewritten
without rewriting the tests.

The renderer deliberately leaves `<head>` alone.  The zh and bilingual site
roots carry their own copies of the stylesheets the pages already link to
relatively, so an untranslated node is byte-identical to the English one.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .document import Document, splice
from .glossary import load_glossary
from .markup import (ATOMIC_TAGS, CANDIDATE_TAGS, CELL_TAGS, add_class, build,
                     extract_markup, set_attr, strip_ids_from)
from .nav import localize_header
from .validate import Violation, check_node, check_page, check_parses

ZH_LANG = "zh-CN"
ZH_CLASS = "zh-trans"


@dataclass
class RenderResult:
    """`None` for a page that failed a gate — broken pages are never emitted."""
    zh_html: str | None
    bilingual_html: str | None
    violations: list = field(default_factory=list)


def extract(page_html, page=""):
    """An empty translation skeleton for one page."""
    plan = _plan(page_html)
    return {
        "page": page,
        "nodes": [{"id": node.id, "path": node.path, "en": node.markup.text,
                   "zh": ""} for node in plan.nodes],
    }


def render(page_html, translations, *, glossary=None, require_translated=True):
    """Render one English page into its Chinese and bilingual versions.

    `require_translated` gates the two semantic checks (the translation must
    contain Chinese, and must honour the glossary).  The structural gates
    always run; turning this off is what lets the round-trip identity test feed
    English back in as its own translation.
    """
    glossary = load_glossary() if glossary is None else glossary
    page = translations.get("page", "")
    nav = translations.get("nav") or {}
    plan = _plan(page_html)
    chinese_by_id = {node["id"]: node.get("zh")
                     for node in translations.get("nodes", [])}

    violations = _check_nodes(plan, chinese_by_id, glossary, require_translated,
                              page)
    if violations:
        return RenderResult(None, None, violations)

    page_file = _page_file(translations, plan)
    zh_html = _render_zh(plan, chinese_by_id, nav, page_file)
    bilingual_html = _render_bilingual(plan, chinese_by_id, nav, page_file)

    violations = check_page(plan.doc, zh_html, page)
    violations += check_parses(bilingual_html, page, "bilingual")
    if violations:
        return RenderResult(None, None, violations)
    return RenderResult(zh_html, bilingual_html, [])


# ---------------------------------------------------------------------------
# Planning: which nodes are translatable, and how they nest
# ---------------------------------------------------------------------------
@dataclass(eq=False)
class _Node:
    el: object
    id: str
    path: str
    markup: object
    owner: object = None


@dataclass
class _Plan:
    doc: object
    header: object
    nodes: list
    children_of: dict


def _plan(page_html):
    doc = Document(page_html)
    header = doc.find("header", "topnav")

    def translatable(el):
        return _is_translatable(doc, el, header)

    taken = {el.attrs["id"] for el in doc if el.attrs.get("id")}
    nodes = []
    by_element = {}
    for el in doc:
        if not translatable(el):
            continue
        markup = extract_markup(doc, el, translatable)
        node = _Node(el=el, id=_node_id(el, taken, len(nodes)),
                     path=_path(doc, el), markup=markup)
        nodes.append(node)
        by_element[id(el)] = node

    children_of = {None: []}
    for node in nodes:
        owner = next((by_element[id(a)] for a in node.el.ancestors()
                      if id(a) in by_element), None)
        node.owner = owner
        children_of.setdefault(owner, []).append(node)
    return _Plan(doc=doc, header=header, nodes=nodes, children_of=children_of)


def _is_translatable(doc, el, header):
    if el.tag not in CANDIDATE_TAGS:
        return False
    if header is not None and (el is header or any(a is header
                                                   for a in el.ancestors())):
        return False
    if _is_bibliography(el):
        return False
    for ancestor in el.ancestors():
        if ancestor.tag in ATOMIC_TAGS or _is_bibliography(ancestor):
            return False
    return bool(_own_text(doc, el).strip())


def _is_bibliography(el):
    return (el.attrs.get("role") == "doc-biblioentry"
            or "biblioentry" in el.epub_type())


def _own_text(doc, el):
    """Text belonging to this node, ignoring nested blocks and code."""
    out = []

    def walk(node):
        position = node.content_start
        for child in node.children:
            out.append(doc.src[position:child.start])
            if child.tag not in ATOMIC_TAGS and child.tag not in CANDIDATE_TAGS:
                walk(child)
            position = child.end
        out.append(doc.src[position:node.content_end])

    walk(el)
    return "".join(out)


def _node_id(el, taken, index):
    own = el.attrs.get("id")
    if own:
        return own
    candidate = "n%04d" % index
    while candidate in taken:
        index += 1
        candidate = "n%04d" % index
    taken.add(candidate)
    return candidate


def _path(doc, el):
    parts = []
    node = el
    while node is not None:
        siblings = node.parent.children if node.parent is not None else doc.roots
        position = next(i for i, s in enumerate(siblings) if s is node)
        index = 1 + sum(1 for s in siblings[:position] if s.tag == node.tag)
        parts.append("%s[%d]" % (node.tag, index))
        node = node.parent
    return "/" + "/".join(reversed(parts))


# ---------------------------------------------------------------------------
# Checking
# ---------------------------------------------------------------------------
def _check_nodes(plan, chinese_by_id, glossary, require_translated, page):
    violations = []
    for node in plan.nodes:
        violation = check_node(node.id, node.markup, chinese_by_id.get(node.id),
                               glossary, require_translated, page)
        if violation is not None:
            violations.append(violation)
    known = {node.id for node in plan.nodes}
    for node_id in chinese_by_id:
        if node_id not in known:
            violations.append(Violation(
                rule="unknown-node", page=page, node_id=node_id,
                message="translation refers to a node this page does not have"))
    return violations


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------
def _render_inner(plan, chinese_by_id, *, keep_zero_width, strip_ids):
    """Chinese inner HTML for every node, innermost first."""
    inner = {}
    for node in reversed(plan.nodes):
        atom_html = {}
        for number, atom in node.markup.atom_elements.items():
            nested = [child for child in plan.children_of.get(node, [])
                      if atom.start <= child.el.start and child.el.end <= atom.end]
            if nested:
                atom_html[number] = splice(
                    plan.doc.src, atom.start, atom.end,
                    [(child.el.content_start, child.el.content_end, inner[child.id])
                     for child in nested])
        inner[node.id] = build(node.markup, chinese_by_id[node.id],
                               keep_zero_width=keep_zero_width,
                               strip_ids=strip_ids, atom_html=atom_html)
    return inner


def _render_zh(plan, chinese_by_id, nav, page_file):
    inner = _render_inner(plan, chinese_by_id, keep_zero_width=True,
                          strip_ids=False)
    doc = plan.doc
    replacements = [(node.el.content_start, node.el.content_end, inner[node.id])
                    for node in plan.children_of[None]]
    replacements += _header_replacement(plan, nav, "zh", page_file)

    root = doc.find("html")
    if root is not None:
        tag = doc.open_tag(root)
        for name in ("lang", "xml:lang"):
            if name in root.attrs:
                tag = set_attr(tag, name, ZH_LANG)
        replacements.append((root.start, root.content_start, tag))
    return splice(doc.src, 0, len(doc.src), replacements)


def _render_bilingual(plan, chinese_by_id, nav, page_file):
    inner = _render_inner(plan, chinese_by_id, keep_zero_width=False,
                          strip_ids=True)
    doc = plan.doc
    replacements = []
    for node in plan.children_of[None]:
        el = node.el
        chinese = inner[node.id]
        if el.tag in CELL_TAGS:
            # A second cell would break the row, so the languages share one.
            replacements.append((
                el.content_start, el.content_end,
                '%s<br/><span class="%s" lang="%s">%s</span>'
                % (doc.inner(el), ZH_CLASS, ZH_LANG, chinese)))
        else:
            open_tag = set_attr(add_class(strip_ids_from(doc.open_tag(el)),
                                          ZH_CLASS), "lang", ZH_LANG)
            replacements.append((
                el.start, el.end,
                doc.source(el) + open_tag + chinese + doc.close_tag(el)))
    replacements += _header_replacement(plan, nav, "bilingual", page_file)
    return splice(doc.src, 0, len(doc.src), replacements)


def _header_replacement(plan, nav, mode, page_file):
    if plan.header is None:
        return []
    header = plan.header
    return [(header.start, header.end,
             localize_header(plan.doc, header, nav, mode, page_file))]


def _page_file(translations, plan):
    stem = translations.get("page") or ""
    if stem:
        return stem if stem.endswith(".html") else stem + ".html"
    for el in plan.doc:
        if el.tag == "option" and "selected" in el.attrs:
            return el.attrs.get("value", "").split("#")[0]
    return ""
