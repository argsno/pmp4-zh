"""The localized landing page.

The landing page is not a chapter and has no translation shards.  Everything on
it is the navigation seen twice — once as the dropdown every page carries, once
as the table of contents below it — so it is rendered from `nav.json`, and a
label translated for the menu is translated here for free.

Its own two sentences are the exception.  `build_site.py` invents them rather
than taking them from the book, so like the Prev/Next labels in `nav.py` they
are kept here as renderer chrome: there is no node for a translator to fill,
and inventing one would mean shipping a translation file with two entries in it.
"""
from .document import Document, splice
from .markup import set_attr
from .nav import label, localize_header

ZH_LANG = "zh-CN"
ZH_CLASS = "zh-trans"

LANDING_FILE = "index.html"
# A landing page sits at a site root, one level above the chapters, so its
# switch reaches the other sites as siblings rather than through `../../`.
LANDING_PREFIX = {"en": "../", "zh": "../zh/", "bilingual": "../bilingual/"}

# Keyed by the exact inner HTML `build_site.build_index()` emits.  A wording
# change there simply leaves the sentence in English rather than breaking.
LANDING_TEXT = {
    "Wen-mei W. Hwu, David B. Kirk, Izzat El Hajj &mdash; A Hands-on Approach "
    "(4th Edition)":
        "Wen-mei W. Hwu、David B. Kirk、Izzat El Hajj &mdash; 动手实践方法"
        "（第 4 版）",
    "Use the dropdown in the top navigation bar to jump to any chapter or "
    "section. Browse the full table of contents below.":
        "使用顶栏的下拉菜单可跳转到任意章节，下方是全书目录。",
}


def render_landing(index_html, nav, mode):
    """Localize the English landing page for the zh or bilingual site.

    Link targets are never touched.  Every one of them is relative to the site
    root, so it already points inside whichever site the page was written into;
    rewriting one could only break it.
    """
    doc = Document(index_html)
    header = doc.header()
    inside_header = set()
    if header is not None:
        inside_header = {id(el) for el in header.descendants()} | {id(header)}

    replacements = []
    for el in doc:
        if id(el) in inside_header:
            continue
        swap = _localized(doc, el, nav, mode)
        if swap is not None:
            replacements.append(swap)

    if header is not None:
        replacements.append((header.start, header.end,
                             localize_header(doc, header, nav, mode,
                                             LANDING_FILE, LANDING_PREFIX)))
    if mode == "zh":
        replacements += _declare_chinese(doc)
    return splice(doc.src, 0, len(doc.src), replacements)


def _localized(doc, el, nav, mode):
    """The replacement for one element's content, or None to leave it be."""
    if el.tag in ("title", "h1") or _is_group(el) or _is_entry(el):
        return _swap(doc, el, label(doc.inner(el), nav, mode))
    if el.tag == "p":
        return _swap(doc, el, _sentence(doc.inner(el), mode))
    return None


def _is_group(el):
    return el.tag == "div" and "grp" in el.classes


def _is_entry(el):
    return (el.tag == "a" and el.parent is not None
            and "subitem" in el.parent.classes)


def _sentence(inner, mode):
    chinese = LANDING_TEXT.get(inner.strip())
    if chinese is None:
        return inner
    if mode == "zh":
        return chinese
    return ('%s<br/><span class="%s" lang="%s">%s</span>'
            % (inner, ZH_CLASS, ZH_LANG, chinese))


def _swap(doc, el, text):
    if text == doc.inner(el):
        return None
    return (el.content_start, el.content_end, text)


def _declare_chinese(doc):
    root = doc.find("html")
    if root is None:
        return []
    tag = doc.open_tag(root)
    for name in ("lang", "xml:lang"):
        if name in root.attrs:
            tag = set_attr(tag, name, ZH_LANG)
    return [(root.start, root.content_start, tag)]
