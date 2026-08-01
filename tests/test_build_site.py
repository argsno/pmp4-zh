"""Ticket 09: the site builder and the i18n renderer as one command.

These tests drive `build_site.main()` — the command a maintainer actually runs —
against a fake EPUB tree in a temp directory, and assert on what lands on disk
and on the exit status.  The one-way dependency is also pinned: the builder may
import `build_i18n`, never the other way round.
"""
import json
import os

import pytest

import build_i18n.cli
import build_site
from build_i18n.cli import main as i18n_main
from support import ROOT, make_page

NAV_XHTML = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head><title>Table of Contents</title></head>
<body>
<nav id="toc"><ol>
<li><a href="Ch001.xhtml">Chapter 1. Introduction</a></li>
<li><a href="Ch002.xhtml">Chapter 2. Threads</a></li>
</ol></nav>
</body>
</html>
"""

CHAPTERS = {
    "Ch001.xhtml": "<h1>Introduction</h1><p>Parallel programming is a skill.</p>",
    "Ch002.xhtml": "<p>Threads run together.</p>",
}

# Same strings as test_cli.py, which already pass the real glossary.
CHINESE = {
    "Introduction": "引言",
    "Parallel programming is a skill.": "并行编程是一项技能。",
    "Threads run together.": "线程一起运行。",
}


@pytest.fixture
def fake_epub(tmp_path, monkeypatch):
    """A minimal EPUB tree plus monkeypatched build_site globals."""
    oebps = tmp_path / "epub_extract" / "OEBPS"
    xhtml = oebps / "xhtml"
    xhtml.mkdir(parents=True)
    (xhtml / "nav.xhtml").write_text(NAV_XHTML, encoding="utf-8")
    for name, body in CHAPTERS.items():
        (xhtml / name).write_text(make_page(body, header=False), encoding="utf-8")
    (oebps / "override_v1.css").write_text("body {}", encoding="utf-8")
    (oebps / "styles").mkdir()
    (oebps / "styles" / "Elsevier_eBook.css").write_text("body {}", encoding="utf-8")
    (oebps / "images").mkdir()
    (oebps / "images" / "x.png").write_text("x", encoding="utf-8")

    web = tmp_path / "web"
    translations = tmp_path / "translations"
    monkeypatch.setattr(build_site, "SRC", str(oebps))
    monkeypatch.setattr(build_site, "XHTML_DIR", str(xhtml))
    monkeypatch.setattr(build_site, "OUT", str(web))
    monkeypatch.setattr(build_site, "TRANSLATIONS", str(translations))
    return web, translations


def translate(web, translations, pages):
    """Fill zh in the given pages' shards, via the engine's own skeleton."""
    assert i18n_main(["extract", "--web", str(web),
                      "--translations", str(translations)]) == 0
    for page in pages:
        for part in sorted((translations / page).glob("part-*.json")):
            data = json.loads(part.read_text(encoding="utf-8"))
            for node in data["nodes"]:
                node["zh"] = CHINESE[node["en"]]
            part.write_text(json.dumps(data, ensure_ascii=False),
                            encoding="utf-8")


def test_build_site_regenerates_all_three_sites_in_one_pass(fake_epub):
    web, translations = fake_epub

    # First pass: the English site builds; nothing is translated yet, so every
    # i18n page is reported and skipped and no zh/bilingual tree appears.
    assert build_site.main() == 1
    assert (web / "chapters" / "Ch001.html").exists()
    assert not (web / "zh").exists()

    translate(web, translations, ["Ch001", "Ch002"])

    # Second pass: one command, three sites.
    assert build_site.main() == 0
    assert (web / "chapters" / "Ch001.html").exists()
    assert (web / "zh" / "chapters" / "Ch001.html").exists()
    assert (web / "bilingual" / "chapters" / "Ch001.html").exists()

    zh = (web / "zh" / "chapters" / "Ch001.html").read_text(encoding="utf-8")
    assert "并行编程是一项技能。" in zh
    assert "Parallel programming is a skill." not in zh

    bilingual = (web / "bilingual" / "chapters" / "Ch001.html").read_text(
        encoding="utf-8")
    assert "Parallel programming is a skill." in bilingual
    assert "zh-trans" in bilingual


def test_a_failing_page_is_reported_and_skipped(fake_epub, capsys):
    web, translations = fake_epub
    build_site.main()                       # build the English site
    translate(web, translations, ["Ch001"])  # Ch002 stays untranslated

    assert build_site.main() == 1

    # The good page renders in both languages; the failing one is skipped
    # rather than emitted broken.
    assert (web / "zh" / "chapters" / "Ch001.html").exists()
    assert (web / "bilingual" / "chapters" / "Ch001.html").exists()
    assert not (web / "zh" / "chapters" / "Ch002.html").exists()
    assert not (web / "bilingual" / "chapters" / "Ch002.html").exists()

    assert "Ch002" in capsys.readouterr().err


def test_the_builder_imports_build_i18n():
    # `import build_i18n.cli` binds the package on the module, so the render
    # pipeline is reachable from the builder exactly as `main()` uses it.
    assert hasattr(build_site, "build_i18n")
    assert hasattr(build_site.build_i18n, "cli")


def test_every_chapter_page_carries_the_viewport_meta(fake_epub):
    web, translations = fake_epub
    meta = '<meta name="viewport" content="width=device-width, initial-scale=1"/>'

    # The tag must come from the build step, never from the EPUB source.
    for name in CHAPTERS:
        src = (web.parent / "epub_extract" / "OEBPS" / "xhtml" / name)
        assert meta not in src.read_text(encoding="utf-8")

    assert build_site.main() == 1   # English site only; nothing translated yet
    for name in CHAPTERS:
        page = (web / "chapters" / (name[:-6] + ".html")).read_text(
            encoding="utf-8")
        assert meta in page

    translate(web, translations, ["Ch001", "Ch002"])
    assert build_site.main() == 0
    for site in ("zh", "bilingual"):
        for name in CHAPTERS:
            page = (web / site / "chapters" / (name[:-6] + ".html")).read_text(
                encoding="utf-8")
            assert meta in page, (site, name)


def _media_body(css, width):
    """The full text of one top-level `@media (max-width: {width}px)` block."""
    start = css.index("@media (max-width: %spx) {" % width)
    depth = 0
    for i in range(start, len(css)):
        if css[i] == "{":
            depth += 1
        elif css[i] == "}":
            depth -= 1
            if depth == 0:
                return css[start:i + 1]
    raise AssertionError("unterminated %spx media block" % width)


def test_topnav_css_reorders_into_mobile_rows(fake_epub):
    web, translations = fake_epub
    assert build_site.main() == 1
    css = (web / "topnav.css").read_text(encoding="utf-8")

    # ≤640px: three deliberate rows.  The book title and the language switch
    # share row 1 (order 1), the chapter selector takes row 2 full-width, and
    # the Home / Prev / Next buttons sit on row 3.  The title truncates with
    # an ellipsis whenever its row runs out of room.
    m640 = _media_body(css, 640)
    assert m640.count("order: 1;") == 2     # .book-title + .langswitch
    assert "order: 2;" in m640              # .nav-select
    assert "order: 3;" in m640              # .nav-buttons
    assert "flex: 1 1 100%;" in m640        # the selector spans its row
    assert "max-width: 100%;" in m640
    assert "text-overflow: ellipsis;" in m640

    # ≤480px: the title shrinks, and nav / language buttons plus the select
    # all reach a ~40px touch height.
    m480 = _media_body(css, 480)
    assert "font-size: 12px;" in m480       # title shrinks
    assert "padding: 12px 14px;" in m480    # nav + language buttons
    assert "min-height: 40px;" in m480      # the chapter select

    # Desktop widths (above 640px) are untouched: no mobile override may leak
    # into the base rules outside the media blocks.  `border:` shares the
    # substring, so match the indented property token.
    base = css.split("@media", 1)[0]
    assert "  order:" not in base
    assert "text-overflow:" not in base
    assert "min-height: 40px" not in base
    assert "flex: 1 1 100%;" not in base


def test_topnav_css_trims_the_content_column_on_mobile(fake_epub):
    web, translations = fake_epub
    assert build_site.main() == 1
    css = (web / "topnav.css").read_text(encoding="utf-8")

    # ≤768px: the EPUB's 2em block indent is halved to 1em a side, so nested
    # content blocks stop eating the reading width on a phone.  Wide tables
    # and code blocks scroll inside their own box instead of forcing the page
    # to scroll.
    m768 = _media_body(css, 768)
    assert "#book-content #sbo-rt-content div" in m768
    assert "margin-left: 1em;" in m768
    assert "margin-right: 1em;" in m768
    assert "overflow-x: auto;" in m768     # tables + pre
    assert "max-width: 100%;" in m768
    # Long URLs, long inline-code tokens, and bare runs of text all wrap
    # instead of pushing the page sideways.  The rule sits on the content
    # column itself because `overflow-wrap` is inherited: it must reach
    # `a`, `code`, the EPUB's `span.inlinecode`, and plain text nodes alike
    # (a bare `1/(5%+0.95%)=…` run in Ch019 overflowed the zh column until
    # the wrap was granted at the container).
    assert "#book-content #sbo-rt-content {" in m768
    assert "overflow-wrap: break-word;" in m768

    # ≤480px: the indent drops to ~0.6em, the content base font rises to 17px,
    # and the reading column widens to ~96% of the viewport, centered.  The
    # body's default 8px margin is dropped so 96% is 96% of the phone screen.
    m480 = _media_body(css, 480)
    assert "margin-left: 0.6em;" in m480
    assert "margin-right: 0.6em;" in m480
    assert "font-size: 17px;" in m480
    assert "#book-content #sbo-rt-content {" in m480
    assert "width: 96%;" in m480
    assert "margin-left: auto;" in m480
    assert "margin-right: auto;" in m480
    assert "body {" in m480
    assert "margin: 0;" in m480

    # Desktop widths (≥769px) are untouched: no content-column override may
    # leak into the base rules outside the media blocks.
    base = css.split("@media", 1)[0]
    assert "font-size: 17px" not in base
    assert "width: 96%" not in base
    assert "margin-left: 1em" not in base
    assert "margin-left: 0.6em" not in base
    assert "overflow-x: auto" not in base

    # The trim lives in the one shared stylesheet that every English chapter
    # page links, so the English site's mobile experience matches the Chinese
    # sites' — it is not a Chinese-only rule.
    en = (web / "chapters" / "Ch001.html").read_text(encoding="utf-8")
    assert 'href="../topnav.css"' in en


def test_topnav_css_keeps_the_part_title_div_in_the_column(fake_epub):
    web, translations = fake_epub
    assert build_site.main() == 1
    css = (web / "topnav.css").read_text(encoding="utf-8")

    # The part-title div `<div id="PN">` is `width: 100%` (content-box) in the
    # EPUB stylesheet.  At ≤480px the content-column trim gives every block
    # div 0.6em side margins; combined with that 100% width the box would
    # shove its right edge past the phone screen (the Part divider pages
    # scrolled sideways).  `width: auto` lets a block div fill its container
    # after the margins are taken, instead of on top of them.
    m480 = _media_body(css, 480)
    assert "#book-content #sbo-rt-content #PN" in m480
    assert "width: auto;" in m480

    # The override lives only in the ≤480px block: at wider widths the EPUB's
    # 100% width fits fine and the desktop layout must stay untouched.
    m768 = _media_body(css, 768)
    assert "#PN" not in m768
    base = css.split("@media", 1)[0]
    assert "#PN" not in base


def test_build_i18n_never_imports_the_builder():
    package = os.path.join(ROOT, "build_i18n")
    for name in sorted(os.listdir(package)):
        if not name.endswith(".py"):
            continue
        with open(os.path.join(package, name), encoding="utf-8") as fh:
            source = fh.read()
        assert "import build_site" not in source, name
        assert "from build_site" not in source, name
