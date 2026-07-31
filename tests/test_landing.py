"""The localized landing page, driven through render_landing().

The landing page is not a chapter.  It carries no prose of its own — only the
navigation's labels, repeated below the fold as a table of contents — so it is
rendered from `translations/nav.json` rather than from a page's shards, and it
gets its own seam beside `render()`.

These tests assert on the produced HTML, never on how it was produced.
"""
import os
import re

import pytest

from build_i18n import render_landing
from support import ROOT

LANDING = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>Programming Massively Parallel Processors, 4th Edition</title>
<link rel="stylesheet" href="topnav.css"/>
</head>
<body>
<header class="topnav">
  <div class="topnav-inner">
    <span class="book-title">Programming Massively Parallel Processors, 4th Edition</span>
    <select id="nav-select" class="nav-select" title="Choose a chapter">
    <optgroup label="Front Matter">
      <option value="chapters/Cover.html">Cover image</option>
    </optgroup>
    <optgroup label="Chapter 1. Introduction">
      <option value="chapters/Ch001.html">Chapter 1. Introduction</option>
      <option value="chapters/Ch001.html#st0010">1.1 Heterogeneous parallel computing</option>
    </optgroup>
    </select>
    <div class="nav-buttons">
      <a class="navbtn" href="index.html">Home</a>
    </div>
  </div>
</header>
<div class="landing">
<h1>Programming Massively Parallel Processors, 4th Edition</h1>
<p class="sub">Wen-mei W. Hwu, David B. Kirk, Izzat El Hajj &mdash; A Hands-on Approach (4th Edition)</p>
<p>Use the dropdown in the top navigation bar to jump to any chapter or section. Browse the full table of contents below.</p>
<div class="grp">Front Matter</div>
<ul>
<li class="subitem"><a href="chapters/Cover.html">Cover image</a></li>
</ul>
<div class="grp">Chapter 1. Introduction</div>
<ul>
<li class="subitem"><a href="chapters/Ch001.html">Chapter 1. Introduction</a></li>
<li class="subitem"><a href="chapters/Ch001.html#st0010">1.1 Heterogeneous parallel computing</a></li>
</ul>
</div>
<script src="topnav.js"></script>
</body>
</html>
"""

NAV = {
    "Programming Massively Parallel Processors, 4th Edition":
        "大规模并行处理器编程（第 4 版）",
    "Front Matter": "前言部分",
    "Cover image": "封面",
    "Chapter 1. Introduction": "第 1 章　绪论",
    "1.1 Heterogeneous parallel computing": "1.1 异构并行计算",
}


def links(html):
    return re.findall(r'href="([^"]*)"', html)


def group_labels(html):
    return re.findall(r'<div class="grp">(.*?)</div>', html)


def toc_entries(html):
    return re.findall(r'<li class="subitem"><a href="[^"]*">(.*?)</a></li>',
                      html)


# ---------------------------------------------------------------------------
# The ticket's acceptance criterion
# ---------------------------------------------------------------------------
def test_the_chinese_landing_lists_the_chapters_in_chinese():
    html = render_landing(LANDING, NAV, "zh")

    assert group_labels(html) == ["前言部分", "第 1 章　绪论"]
    assert toc_entries(html) == ["封面", "第 1 章　绪论", "1.1 异构并行计算"]


def test_the_chinese_landing_titles_itself_in_chinese():
    html = render_landing(LANDING, NAV, "zh")

    assert "<h1>大规模并行处理器编程（第 4 版）</h1>" in html
    assert "<title>大规模并行处理器编程（第 4 版）</title>" in html


def test_the_chinese_landing_declares_chinese():
    assert 'lang="zh-CN"' in render_landing(LANDING, NAV, "zh")


def test_the_chinese_landing_translates_its_own_prose():
    html = render_landing(LANDING, NAV, "zh")

    assert "Use the dropdown" not in html
    assert "下拉" in html


# ---------------------------------------------------------------------------
# What must survive untouched
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("mode", ["zh", "bilingual"])
def test_the_landing_never_rewrites_a_link(mode):
    """Every chapter link is relative to the site root, so it already points
    inside whichever site the page was copied into.  Rewriting one could only
    break it.  The switch is the sole new set of links on the page."""
    html = render_landing(LANDING, NAV, mode)
    switch = re.search(r'<div class="langswitch">.*?</div>', html, re.S).group()

    assert links(html.replace(switch, "")) == links(LANDING)


@pytest.mark.parametrize("mode", ["zh", "bilingual"])
def test_the_landing_keeps_every_option_value(mode):
    html = render_landing(LANDING, NAV, mode)

    assert (re.findall(r'<option value="([^"]*)"', LANDING)
            == re.findall(r'<option value="([^"]*)"', html))


@pytest.mark.parametrize("mode", ["zh", "bilingual"])
def test_the_landing_keeps_its_shape(mode):
    html = render_landing(LANDING, NAV, mode)

    for tag in ("li", "ul", "optgroup", "option", "h1"):
        assert html.count("<%s" % tag) == LANDING.count("<%s" % tag), tag


def test_a_label_nobody_translated_stays_english():
    html = render_landing(LANDING, {"Front Matter": "前言部分"}, "zh")

    assert "Cover image" in html
    assert "前言部分" in html


# ---------------------------------------------------------------------------
# The language switch
# ---------------------------------------------------------------------------
def test_the_landing_switch_points_at_the_other_landings_not_at_chapters():
    html = render_landing(LANDING, NAV, "zh")
    switch = re.search(r'<div class="langswitch">.*?</div>', html, re.S).group()

    assert 'href="../index.html"' in switch
    assert 'href="../bilingual/index.html"' in switch
    assert "chapters/" not in switch


@pytest.mark.parametrize("mode,active", [("zh", "中"), ("bilingual", "对照")])
def test_the_landing_marks_the_site_it_is_on(mode, active):
    html = render_landing(LANDING, NAV, mode)

    assert '<span class="langbtn active">%s</span>' % active in html


# ---------------------------------------------------------------------------
# Bilingual
# ---------------------------------------------------------------------------
def test_the_bilingual_landing_lists_both_languages():
    html = render_landing(LANDING, NAV, "bilingual")

    assert group_labels(html) == ["Front Matter / 前言部分",
                                  "Chapter 1. Introduction / 第 1 章　绪论"]
    assert "Cover image / 封面" in toc_entries(html)


def test_the_bilingual_landing_leaves_the_document_language_alone():
    """Its chapter pages keep `lang="en"` on `<html>` too — the page is not in
    one language, only its translated runs are."""
    html = render_landing(LANDING, NAV, "bilingual")

    assert re.search(r"<html[^>]*>", html).group() == '<html lang="en">'


# ---------------------------------------------------------------------------
# The real artefact
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("mode", ["zh", "bilingual"])
def test_the_real_landing_page_renders_with_its_links_intact(mode):
    """The fixture above is a miniature; this is the 288-entry page we ship."""
    with open(os.path.join(ROOT, "web", "index.html"), encoding="utf-8") as fh:
        english = fh.read()

    html = render_landing(english, NAV, mode)

    assert re.findall(r'<option value="([^"]*)"', english) \
        == re.findall(r'<option value="([^"]*)"', html)
    assert len(toc_entries(html)) == len(toc_entries(english))
    assert "大规模并行处理器编程（第 4 版）" in html
