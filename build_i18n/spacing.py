"""Mechanical CJK / Latin spacing.

Consistency here cannot depend on every translator remembering the rule, so the
renderer applies it and translators are free to ignore it.  Pure-ASCII text is
never touched, which is what keeps the round-trip identity exact.
"""
import re

CJK = "\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3040-\u30ff"
_CJK_RE = re.compile("[%s]" % CJK)
_LATIN_RE = re.compile(r"[0-9A-Za-z]")

# Only codepoints that never appear in the English source, so that normalizing
# an untranslated node is a no-op.
_CLOSING_PUNCT = "，。、；：！？）》"
_OPENING_PUNCT = "（《"

_MARKER_RE = re.compile(r"(【/?[MZ]?\d+】)")
_OPENER_RE = re.compile(r"^【[MZ]?\d+】$")


def has_cjk(text):
    return bool(_CJK_RE.search(text))


def _needs_space(left, right):
    return ((_CJK_RE.match(left) and _LATIN_RE.match(right)) or
            (_LATIN_RE.match(left) and _CJK_RE.match(right)))


def normalize(text):
    """Insert half-width spaces at CJK/Latin boundaries, skipping placeholders.

    A space lands outside the inline markup rather than inside it: 使用【1】CUDA
    becomes 使用 【1】CUDA, so the emitted tag wraps the word and not the space.
    """
    out = []
    markers = []
    previous = ""
    for piece in _MARKER_RE.split(text):
        if not piece:
            continue
        if _MARKER_RE.fullmatch(piece):
            markers.append(piece)
            continue
        for char in piece:
            if previous and _needs_space(previous, char):
                cut = next((i for i, m in enumerate(markers)
                            if _OPENER_RE.match(m)), len(markers))
                out.extend(markers[:cut])
                out.append(" ")
                out.extend(markers[cut:])
            else:
                out.extend(markers)
            markers = []
            out.append(char)
            previous = char
    out.extend(markers)
    result = "".join(out)
    result = re.sub(r"[ \t]+([%s])" % _CLOSING_PUNCT, r"\1", result)
    result = re.sub(r"([%s])[ \t]+" % _OPENING_PUNCT, r"\1", result)
    return result
