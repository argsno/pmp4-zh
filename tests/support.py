"""Helpers for driving the render() seam from tests.

Tests assert on rendered HTML and on violations.  They use extract() only to
discover node ids when building an input translation set, never to assert on
extraction internals.
"""
import os
import re

from build_i18n import extract

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTER_PATH = os.path.join(
    ROOT, "docs", "chapters", "Ch001_1-19_B9780323912310000069.html")

HEADER = """\
<header class="topnav">
  <div class="topnav-inner">
    <span class="book-title">Programming Massively Parallel Processors, 4th Edition</span>
    <select id="nav-select" class="nav-select" title="Choose a chapter">
    <optgroup label="Chapter 1. Introduction">
      <option value="Ch001.html" selected>Chapter 1. Introduction</option>
      <option value="Ch001.html#st0010">Abstract</option>
    </optgroup>
    </select>
    <div class="nav-buttons">
      <a class="navbtn" href="../index.html">Home</a>
      <a class="navbtn" href="Ch000.html">&#8249; Prev</a>
      <a class="navbtn" href="Ch002.html">Next &#8250;</a>
    </div>
    <div class="langswitch"><span class="langbtn active">EN</span><a class="langbtn" href="../zh/chapters/Ch001.html">中</a><a class="langbtn" href="../bilingual/chapters/Ch001.html">对照</a></div>
    <nav class="bottom-pager" aria-label="Chapter navigation">
      <a class="navbtn" href="Ch000.html">&#8249; Prev</a>
      <a class="navbtn" href="Ch002.html">Next &#8250;</a>
    </nav>
  </div>
</header>"""


def make_page(body, header=True):
    """A minimal page shaped like the ones build_site.py emits."""
    return (
        '<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE html>'
        '<html xml:lang="en" lang="en" xmlns="http://www.w3.org/1999/xhtml"'
        ' xmlns:epub="http://www.idpf.org/2007/ops">'
        '<head><title>Programming Massively Parallel Processors, 4th Edition</title></head>'
        '<body>\n' + (HEADER + "\n" if header else "") + body + '\n</body></html>'
    )


def translations_for(page_html, zh_by_en=None, page="Ch001", **extra):
    """Build a translation set, translating nodes by their English text.

    Nodes whose English text is not in `zh_by_en` keep the English as their
    translation, which is what the identity round-trip needs.
    """
    zh_by_en = zh_by_en or {}
    data = extract(page_html, page=page)
    for node in data["nodes"]:
        node["zh"] = zh_by_en.get(node["en"], node["en"])
    data.update(extra)
    return data


def english_text(page_html):
    """The translator-facing English of every translatable node."""
    return [node["en"] for node in extract(page_html, page="x")["nodes"]]


def canonical(html):
    """Blank out the two parts the identity round-trip is allowed to change."""
    html = re.sub(r'<header class="topnav">.*?</header>', "<!--nav-->", html,
                  flags=re.S)
    html = re.sub(r'(xml:)?lang="[^"]*"', 'lang="?"', html)
    return html


def count(html, pattern):
    return len(re.findall(pattern, html))
