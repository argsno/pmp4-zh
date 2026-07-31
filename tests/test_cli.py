"""The command line, driven the way a maintainer drives it: through main().

These tests stay at the surface — files on disk and exit codes — so the shell
around the engine can be rearranged without rewriting them.
"""
import json

import pytest

from build_i18n.cli import main
from support import make_page

PAGES = {
    "Ch001.html": "<h1>Introduction</h1>"
                  "<p>Parallel programming is a skill.</p>",
    "Ch002.html": "<p>Threads run together.</p>",
}
CHINESE = {
    "Introduction": "引言",
    "Parallel programming is a skill.": "并行编程是一项技能。",
    "Threads run together.": "线程一起运行。",
}


@pytest.fixture
def site(tmp_path):
    web = tmp_path / "web"
    (web / "chapters").mkdir(parents=True)
    (web / "styles").mkdir()
    (web / "topnav.css").write_text("nav {}", encoding="utf-8")
    (web / "index.html").write_text("<html></html>", encoding="utf-8")
    for name, body in PAGES.items():
        (web / "chapters" / name).write_text(make_page(body), encoding="utf-8")
    return web, tmp_path / "translations"


def run(command, site, *extra):
    web, translations = site
    return main([command, "--web", str(web),
                 "--translations", str(translations), *extra])


def translate(site, *pages):
    """Fill in the Chinese for whole pages, the way a translator would."""
    _, translations = site
    for page in pages:
        for part in sorted((translations / page).glob("part-*.json")):
            data = json.loads(part.read_text(encoding="utf-8"))
            for node in data["nodes"]:
                node["zh"] = CHINESE[node["en"]]
            part.write_text(json.dumps(data, ensure_ascii=False),
                            encoding="utf-8")


def read(path):
    return path.read_text(encoding="utf-8")


def test_extract_writes_an_empty_skeleton_per_page(site):
    web, translations = site
    assert run("extract", site) == 0

    nodes = json.loads(read(translations / "Ch001" / "part-00.json"))["nodes"]
    assert [node["en"] for node in nodes] == ["Introduction",
                                              "Parallel programming is a skill."]
    assert [node["zh"] for node in nodes] == ["", ""]


def test_extract_lists_the_navigation_labels_once_for_the_whole_site(site):
    web, translations = site
    assert run("extract", site) == 0

    nav = json.loads(read(translations / "nav.json"))
    assert nav["Chapter 1. Introduction"] == ""
    assert nav["Abstract"] == ""


def test_extract_never_overwrites_work_in_progress(site):
    run("extract", site)
    translate(site, "Ch001")

    assert run("extract", site) == 0

    _, translations = site
    nodes = json.loads(read(translations / "Ch001" / "part-00.json"))["nodes"]
    assert nodes[0]["zh"] == "引言"


def test_forced_re_extraction_keeps_the_translations_it_can_still_place(site):
    run("extract", site)
    translate(site, "Ch001")

    assert run("extract", site, "--force") == 0

    _, translations = site
    nodes = json.loads(read(translations / "Ch001" / "part-00.json"))["nodes"]
    assert nodes[0]["zh"] == "引言"


def test_forced_re_extraction_drops_a_translation_whose_english_moved_on(site):
    """Ids are positional for nodes the page does not name, so a translation is
    only carried over when its English text still matches — otherwise an edit
    to the page would re-attach a paragraph's Chinese to its neighbour."""
    run("extract", site)
    translate(site, "Ch001")
    _, translations = site
    part = translations / "Ch001" / "part-00.json"
    data = json.loads(read(part))
    data["nodes"][0]["en"] = "A different heading"
    part.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    assert run("extract", site, "--force") == 0

    nodes = json.loads(read(part))["nodes"]
    assert nodes[0]["en"] == "Introduction"
    assert nodes[0]["zh"] == ""
    assert nodes[1]["zh"] == "并行编程是一项技能。"


def test_shards_hold_a_page_a_translator_can_answer_in_one_go(site):
    _, translations = site

    assert run("extract", site, "--only", "Ch001", "--shard-nodes", "1") == 0

    assert sorted(p.name for p in (translations / "Ch001").glob("part-*.json")) \
        == ["part-00.json", "part-01.json"]


def test_a_broken_translation_file_says_which_file_is_broken(site, capsys):
    _, translations = site
    run("extract", site)
    (translations / "Ch001" / "part-00.json").write_text("{oops",
                                                         encoding="utf-8")

    assert run("render", site) == 2
    assert "part-00.json is not valid JSON" in capsys.readouterr().err


def test_render_writes_both_sites(site):
    web, _ = site
    run("extract", site)
    translate(site, "Ch001", "Ch002")

    assert run("render", site) == 0

    chinese = read(web / "zh" / "chapters" / "Ch001.html")
    assert "并行编程是一项技能。" in chinese
    assert 'lang="zh-CN"' in chinese
    assert "Parallel programming is a skill." not in chinese

    bilingual = read(web / "bilingual" / "chapters" / "Ch001.html")
    assert "Parallel programming is a skill." in bilingual
    assert "并行编程是一项技能。" in bilingual
    assert "zh-trans" in bilingual


def test_render_shares_the_english_assets_rather_than_copying_them(site):
    web, _ = site
    run("extract", site)
    translate(site, "Ch001", "Ch002")
    run("render", site)

    for name in ("styles", "topnav.css", "index.html"):
        assert (web / "zh" / name).is_symlink()
        assert (web / "zh" / name).resolve() == (web / name).resolve()


def test_render_leaves_a_real_file_in_the_site_root_alone(site):
    web, _ = site
    (web / "zh").mkdir()
    (web / "zh" / "topnav.css").write_text("nav { font-family: serif }",
                                           encoding="utf-8")
    run("extract", site)
    translate(site, "Ch001", "Ch002")

    assert run("render", site) == 0
    assert read(web / "zh" / "topnav.css") == "nav { font-family: serif }"


def test_a_failing_page_is_skipped_and_never_emitted(site):
    web, _ = site
    run("extract", site)
    translate(site, "Ch001")           # Ch002 is left untranslated

    assert run("render", site) == 1

    assert (web / "zh" / "chapters" / "Ch001.html").exists()
    assert not (web / "zh" / "chapters" / "Ch002.html").exists()
    assert not (web / "bilingual" / "chapters" / "Ch002.html").exists()


def test_a_run_where_every_page_fails_leaves_no_empty_site_behind(site):
    web, _ = site
    run("extract", site)               # nothing translated yet

    assert run("render", site) == 1
    assert not (web / "zh").exists()


def test_validate_reports_the_same_failure_without_writing_anything(site):
    web, _ = site
    run("extract", site)
    translate(site, "Ch001")

    assert run("validate", site) == 1
    assert not (web / "zh").exists()


def test_untranslated_pages_can_be_rendered_as_an_english_draft(site):
    web, _ = site
    run("extract", site)

    assert run("render", site, "--allow-untranslated") == 0
    assert "Threads run together." in read(web / "zh" / "chapters" / "Ch002.html")


def test_only_selects_the_pages_to_work_on(site):
    web, translations = site

    assert run("extract", site, "--only", "Ch001") == 0

    assert (translations / "Ch001").exists()
    assert not (translations / "Ch002").exists()
