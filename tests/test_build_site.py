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


def test_build_i18n_never_imports_the_builder():
    package = os.path.join(ROOT, "build_i18n")
    for name in sorted(os.listdir(package)):
        if not name.endswith(".py"):
            continue
        with open(os.path.join(package, name), encoding="utf-8") as fh:
            source = fh.read()
        assert "import build_site" not in source, name
        assert "from build_site" not in source, name
