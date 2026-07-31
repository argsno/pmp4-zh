"""Source-preserving HTML scanning.

The engine never re-serializes a page.  Every output is the original source
string with a handful of byte ranges replaced, which is what lets an
untranslated node come out of the pipeline exactly as it went in — attribute
order, entities, self-closing forms, the XML declaration and all.

This module supplies the element tree carrying the source offsets those splices
need.  Tag and attribute names are lowercased for matching, but nothing is ever
emitted from them: output always comes from slices of the original string.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser

VOID_TAGS = frozenset(
    "area base br col embed hr img input link meta param source track wbr".split())


@dataclass(eq=False)
class Element:
    tag: str
    attrs: dict
    start: int           # offset of the "<" of the open tag
    content_start: int   # offset just past the open tag's ">"
    content_end: int     # offset of the "<" of the close tag
    end: int             # offset just past the close tag's ">"
    parent: "Element | None" = None
    children: list = field(default_factory=list)

    @property
    def classes(self):
        return self.attrs.get("class", "").split()

    def epub_type(self):
        return self.attrs.get("epub:type", "")

    def ancestors(self):
        node = self.parent
        while node is not None:
            yield node
            node = node.parent

    def descendants(self):
        for child in self.children:
            yield child
            yield from child.descendants()


class Document:
    """An HTML source string plus the element tree that indexes into it."""

    def __init__(self, src):
        self.src = src
        scanner = _Scanner(src)
        self.roots, self.stray_end_tags, self.unclosed_tags = scanner.scan()

    def __iter__(self):
        for root in self.roots:
            yield root
            yield from root.descendants()

    def find(self, tag, cls=None):
        for el in self:
            if el.tag == tag and (cls is None or cls in el.classes):
                return el
        return None

    def source(self, el):
        return self.src[el.start:el.end]

    def inner(self, el):
        return self.src[el.content_start:el.content_end]

    def open_tag(self, el):
        return self.src[el.start:el.content_start]

    def close_tag(self, el):
        return self.src[el.content_end:el.end]

    def text(self, el):
        """Every character of the element's rendered text, markup removed."""
        out = []
        pos = el.content_start
        for child in el.children:
            out.append(self.src[pos:child.start])
            out.append(self.text(child))
            pos = child.end
        out.append(self.src[pos:el.content_end])
        return "".join(out)


def splice(src, start, end, replacements):
    """Rebuild src[start:end] with non-overlapping (from, to, text) swaps."""
    out = []
    pos = start
    for begin, finish, text in sorted(replacements):
        if begin < pos:
            raise ValueError("overlapping replacements")
        out.append(src[pos:begin])
        out.append(text)
        pos = finish
    out.append(src[pos:end])
    return "".join(out)


class _Scanner(HTMLParser):
    """Records the source offsets of every tag.

    HTMLParser reports where a token *starts*, never where it ends, so each
    offset a node needs is filled in when the following token arrives.
    """

    def __init__(self, src):
        super().__init__(convert_charrefs=False)
        self._src = src
        self._line_starts = [0]
        for line in src.splitlines(keepends=True):
            self._line_starts.append(self._line_starts[-1] + len(line))
        self.roots = []
        self.stray_end_tags = []
        self.unclosed_tags = []
        self._open = []
        self._pending = []

    def scan(self):
        self.feed(self._src)
        self.close()
        self._flush(len(self._src))
        for el in reversed(self._open):
            self.unclosed_tags.append(el.tag)
            el.content_end = el.end = len(self._src)
        return self.roots, self.stray_end_tags, self.unclosed_tags

    def _offset(self):
        line, column = self.getpos()
        return self._line_starts[line - 1] + column

    def _flush(self, offset):
        pending, self._pending = self._pending, []
        for fill in pending:
            fill(offset)

    def _start(self, tag, attrs, void):
        offset = self._offset()
        self._flush(offset)
        parent = self._open[-1] if self._open else None
        el = Element(tag=tag, attrs={k: (v or "") for k, v in attrs},
                     start=offset, content_start=offset, content_end=offset,
                     end=offset, parent=parent)
        (parent.children if parent is not None else self.roots).append(el)
        if void:
            def close_void(off, el=el):
                el.content_start = el.content_end = el.end = off
            self._pending.append(close_void)
        else:
            def open_content(off, el=el):
                el.content_start = off
            self._pending.append(open_content)
            self._open.append(el)

    def handle_starttag(self, tag, attrs):
        self._start(tag, attrs, tag in VOID_TAGS)

    def handle_startendtag(self, tag, attrs):
        self._start(tag, attrs, True)

    def handle_endtag(self, tag):
        offset = self._offset()
        self._flush(offset)
        for index in range(len(self._open) - 1, -1, -1):
            if self._open[index].tag != tag:
                continue
            for unclosed in self._open[index + 1:]:
                self.unclosed_tags.append(unclosed.tag)
                unclosed.content_end = unclosed.end = offset
            el = self._open[index]
            del self._open[index:]
            el.content_end = offset

            def close_element(off, el=el):
                el.end = off
            self._pending.append(close_element)
            return
        self.stray_end_tags.append(tag)

    def _token(self, *_args):
        self._flush(self._offset())

    handle_data = _token
    handle_comment = _token
    handle_decl = _token
    handle_pi = _token
    handle_entityref = _token
    handle_charref = _token
    unknown_decl = _token
