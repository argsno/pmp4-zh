"""Behavioural tests for the build_i18n rendering engine.

Every test drives the single public seam, render(page_html, translations), and
asserts on the produced HTML or on the reported violations.
"""
import re

import pytest

from build_i18n import render
from support import (CHAPTER_PATH, count, canonical, english_text, make_page,
                     translations_for)

NO_GLOSSARY = {}


def rendered(body, zh_by_en=None, **kw):
    page = make_page(body)
    kw.setdefault("glossary", NO_GLOSSARY)
    return page, render(page, translations_for(page, zh_by_en), **kw)


# ---------------------------------------------------------------------------
# Flagship: extraction covered everything and injection lost nothing
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def chapter():
    with open(CHAPTER_PATH, encoding="utf-8") as fh:
        return fh.read()


def test_identity_roundtrip_reproduces_the_english_page(chapter):
    result = render(chapter, translations_for(chapter),
                    glossary=NO_GLOSSARY, require_translated=False)

    assert result.violations == []
    assert canonical(result.zh_html) == canonical(chapter)


def test_identity_roundtrip_covers_a_meaningful_amount_of_prose(chapter):
    # Guards the test above: it would also pass if nothing were extracted.
    nodes = english_text(chapter)
    assert len(nodes) > 50
    assert sum(len(n) for n in nodes) > 40000


# ---------------------------------------------------------------------------
# Placeholders
# ---------------------------------------------------------------------------
INLINE_BODY = ('<p id="p1">Use <em>shared memory</em> to speed up '
               '<a href="#s0010">matrix multiplication</a>.</p>')


def markers(text):
    """(open, close) of the first paired placeholder, whatever it is numbered."""
    return re.search(r"(【\d+】).*?(【/\d+】)", text).groups()


def test_paired_placeholders_may_move_to_the_chinese_word():
    page = make_page(INLINE_BODY)
    en = english_text(page)[0]
    first_open, first_close = markers(en)
    second_open, second_close = markers(en[en.index(first_close) + len(first_close):])
    zh = (f"为了加速{second_open}矩阵乘法{second_close}，"
          f"请使用{first_open}共享内存{first_close}。")

    result = render(page, translations_for(page, {en: zh}), glossary=NO_GLOSSARY)

    assert result.violations == []
    assert "<em>共享内存</em>" in result.zh_html
    assert '<a href="#s0010">矩阵乘法</a>' in result.zh_html
    assert "shared memory" not in result.zh_html


def test_nested_inline_markup_is_rebuilt():
    page = make_page('<p id="p1">See <cite><em>ACM Queue</em></cite> today.</p>')
    en = english_text(page)[0]
    outer_open, _ = markers(en)
    inner = re.search(r"【\d+】(【\d+】).*?(【/\d+】)(【/\d+】)", en)
    zh = f"今天请参阅{outer_open}{inner.group(1)}ACM 队列{inner.group(2)}{inner.group(3)}。"

    result = render(page, translations_for(page, {en: zh}), glossary=NO_GLOSSARY)

    assert result.violations == []
    assert "<cite><em>ACM 队列</em></cite>" in result.zh_html


@pytest.mark.parametrize("mangle", [
    pytest.param(lambda en, o, c: "共享内存加速矩阵乘法。", id="deleted"),
    pytest.param(lambda en, o, c: f"{o}共享内存{c}加速{o}矩阵乘法{c}。", id="duplicated"),
    pytest.param(lambda en, o, c: f"{o}共享内存{c}加速【9】矩阵乘法【/9】。", id="renumbered"),
    pytest.param(lambda en, o, c: f"{o}共享内存加速矩阵乘法。", id="unclosed"),
    pytest.param(lambda en, o, c: f"{c}共享内存{o}加速矩阵乘法。", id="inverted"),
    pytest.param(lambda en, o, c: f"{o}共享内存{c}加速【M7】矩阵乘法。", id="invented-atom"),
])
def test_broken_placeholders_are_a_violation_and_no_page_is_written(mangle):
    page = make_page(INLINE_BODY)
    en = english_text(page)[0]
    open_m, close_m = markers(en)

    result = render(page, translations_for(page, {en: mangle(en, open_m, close_m)}),
                    glossary=NO_GLOSSARY)

    assert [v.rule for v in result.violations] == ["placeholder-mismatch"]
    assert result.violations[0].node_id == "p1"
    assert result.zh_html is None
    assert result.bilingual_html is None


# ---------------------------------------------------------------------------
# Untranslatable content
# ---------------------------------------------------------------------------
UNTRANSLATABLE_BODY = (
    '<p id="p1">Declare the pointer.</p>'
    '<pre id="pre1">float *A_d</pre>'
    '<p class="hiddenClass" id="m1"><math><mi>y</mi><mo>=</mo><mi>x</mi></math></p>'
    '<p class="reflist3" role="doc-biblioentry" epub:type="biblioentry footnote"'
    ' id="bib1"><a href="#BIB_1">Kirk, 2010</a> Kirk D. Programming Massively'
    ' Parallel Processors.</p>'
)


def test_code_math_and_bibliography_are_never_offered_for_translation():
    page = make_page(UNTRANSLATABLE_BODY)

    offered = " ".join(english_text(page))

    assert "float *A_d" not in offered
    assert "Kirk D. Programming" not in offered
    assert "<mi>" not in offered and "mi>y" not in offered
    assert "Declare the pointer." in offered


def test_code_math_and_bibliography_survive_verbatim():
    _, result = rendered(UNTRANSLATABLE_BODY, {"Declare the pointer.": "声明该指针。"})

    assert result.violations == []
    assert '<pre id="pre1">float *A_d</pre>' in result.zh_html
    assert "<math><mi>y</mi><mo>=</mo><mi>x</mi></math>" in result.zh_html
    assert "Kirk D. Programming Massively Parallel Processors." in result.zh_html


def test_inline_math_stays_put_when_the_sentence_is_translated():
    body = ('<p id="p1">The classifier is <span class="hiddenClass"><math>'
            '<mi>y</mi></math></span> in practice.</p>')
    page = make_page(body)
    en = english_text(page)[0]
    atom = re.search(r"【M\d+】", en).group(0)

    result = render(page, translations_for(page, {en: f"分类器在实践中为{atom}。"}),
                    glossary=NO_GLOSSARY)

    assert result.violations == []
    assert ('<span class="hiddenClass"><math><mi>y</mi></math></span>'
            in result.zh_html)


# ---------------------------------------------------------------------------
# Zero-width elements
# ---------------------------------------------------------------------------
ZERO_WIDTH_BODY = (
    '<p id="p1">Data <span id="page_5" epub:type="pagebreak" role="doc-pagebreak">'
    '</span>parallelism is <a id="P2"></a>everywhere.</p>')


def test_zero_width_anchors_are_hidden_from_the_translator():
    page = make_page(ZERO_WIDTH_BODY)

    en = english_text(page)[0]

    assert en == "Data parallelism is everywhere."


def test_zero_width_anchors_survive_translation():
    _, result = rendered(ZERO_WIDTH_BODY,
                         {"Data parallelism is everywhere.": "数据并行无处不在。"})

    assert result.violations == []
    assert count(result.zh_html, r'id="page_5"') == 1
    assert count(result.zh_html, r'id="P2"') == 1


def test_zero_width_counts_are_preserved_across_the_whole_chapter(chapter):
    result = render(chapter, translations_for(chapter),
                    glossary=NO_GLOSSARY, require_translated=False)

    assert count(result.zh_html, r'epub:type="pagebreak"') == \
        count(chapter, r'epub:type="pagebreak"')
    assert count(result.zh_html, r"<a id=") == count(chapter, r"<a id=")


# ---------------------------------------------------------------------------
# Bilingual interleaving
# ---------------------------------------------------------------------------
def test_bilingual_doubles_prose_but_not_code_or_references():
    _, result = rendered(UNTRANSLATABLE_BODY, {"Declare the pointer.": "声明该指针。"})
    bilingual = result.bilingual_html

    assert "Declare the pointer." in bilingual
    assert "声明该指针。" in bilingual
    assert count(bilingual, "zh-trans") == 1
    assert count(bilingual, r"float \*A_d") == 1
    assert count(bilingual, "Kirk D. Programming") == 1
    assert count(bilingual, "<math>") == 1


def test_bilingual_headings_come_out_as_two_lines():
    _, result = rendered('<h1 id="t1">Introduction</h1>', {"Introduction": "引言"})

    assert re.search(r'<h1 id="t1">Introduction</h1>\s*<h1[^>]*zh-trans[^>]*>引言</h1>',
                     result.bilingual_html)


def test_bilingual_table_cells_separate_the_languages_inside_the_cell():
    body = ('<table><tr><td id="c1">Number of images</td>'
            '<td id="c2">Batch size</td></tr></table>')
    _, result = rendered(body, {"Number of images": "图像数量",
                                "Batch size": "批大小"})

    assert count(result.bilingual_html, "<td") == 2
    assert re.search(r'<td id="c1">Number of images<br/>'
                     r'<span[^>]*zh-trans[^>]*>图像数量</span></td>',
                     result.bilingual_html)


def test_bilingual_copy_does_not_repeat_ids():
    _, result = rendered(ZERO_WIDTH_BODY,
                         {"Data parallelism is everywhere.": "数据并行无处不在。"})

    assert count(result.bilingual_html, r'id="page_5"') == 1
    assert count(result.bilingual_html, r'id="P2"') == 1
    assert count(result.bilingual_html, r'id="p1"') == 1


def test_bilingual_doubles_every_translated_block_of_a_real_chapter(chapter):
    result = render(chapter, translations_for(chapter),
                    glossary=NO_GLOSSARY, require_translated=False)

    assert count(result.bilingual_html, "zh-trans") == len(english_text(chapter))
    assert count(result.bilingual_html, "<pre") == count(chapter, "<pre")
    assert count(result.bilingual_html, r'role="doc-biblioentry"') == \
        count(chapter, r'role="doc-biblioentry"')


# ---------------------------------------------------------------------------
# Spacing
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("zh,expected", [
    ("使用CUDA编程", "使用 CUDA 编程"),
    ("共有256个线程", "共有 256 个线程"),
    ("使用 CUDA 编程", "使用 CUDA 编程"),
    ("这是CUDA，很快。", "这是 CUDA，很快。"),
    ("先归约（reduction），再扫描。", "先归约（reduction），再扫描。"),
])
def test_spaces_between_chinese_and_latin_are_mechanical(zh, expected):
    _, result = rendered('<p id="p1">Some prose here.</p>',
                         {"Some prose here.": zh})

    assert f'<p id="p1">{expected}</p>' in result.zh_html


def test_spacing_reaches_across_inline_markup():
    page = make_page('<p id="p1">Use <em>CUDA</em> now.</p>')
    en = english_text(page)[0]
    open_m, close_m = markers(en)

    result = render(page, translations_for(page, {en: f"现在使用{open_m}CUDA{close_m}编程"}),
                    glossary=NO_GLOSSARY)

    assert "现在使用 <em>CUDA</em> 编程" in result.zh_html


# ---------------------------------------------------------------------------
# Untranslated / copied-through text
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("zh", ["", "   ", "Some prose here."])
def test_missing_or_copied_translations_are_a_violation(zh):
    _, result = rendered('<p id="p1">Some prose here.</p>',
                         {"Some prose here.": zh})

    assert [v.rule for v in result.violations] == ["untranslated"]
    assert result.zh_html is None


def test_short_labels_may_legitimately_stay_in_english():
    body = '<table><tr><th id="h1">N</th><th id="h2">GB/s</th></tr></table>'
    _, result = rendered(body)

    assert result.violations == []
    assert '<th id="h1">N</th>' in result.zh_html


def test_a_node_with_no_translation_at_all_is_reported():
    page = make_page('<p id="p1">Some prose here.</p>')
    data = translations_for(page, {"Some prose here.": "这里有一些正文。"})
    data["nodes"] = []

    result = render(page, data, glossary=NO_GLOSSARY)

    assert [v.rule for v in result.violations] == ["missing-translation"]
    assert result.violations[0].node_id == "p1"


# ---------------------------------------------------------------------------
# Glossary
# ---------------------------------------------------------------------------
GLOSSARY = {"shared memory": "共享内存", "warp": "线程束", "GPU": "GPU（保留不译）"}


def test_a_term_translated_against_the_glossary_is_a_violation():
    page = make_page('<p id="p1">A warp reads shared memory.</p>')
    data = translations_for(page, {"A warp reads shared memory.": "一个波前读取共享内存。"})

    result = render(page, data, glossary=GLOSSARY)

    assert [v.rule for v in result.violations] == ["glossary"]
    assert "warp" in result.violations[0].message


def test_the_glossary_accepts_the_bilingual_first_use_form():
    page = make_page('<p id="p1">A warp reads shared memory.</p>')
    data = translations_for(page,
                            {"A warp reads shared memory.": "一个线程束（warp）读取共享内存。"})

    result = render(page, data, glossary=GLOSSARY)

    assert result.violations == []


def test_terms_the_glossary_keeps_in_english_are_not_enforced():
    page = make_page('<p id="p1">The GPU runs the kernel.</p>')
    data = translations_for(page, {"The GPU runs the kernel.": "GPU 运行该核函数。"})

    result = render(page, data, glossary=GLOSSARY)

    assert result.violations == []


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------
NAV = {"Chapter 1. Introduction": "第 1 章 引言", "Abstract": "摘要",
       "Programming Massively Parallel Processors, 4th Edition": "大规模并行处理器编程（第 4 版）"}


def test_nav_display_text_is_localized_but_values_are_untouched():
    page = make_page('<p id="p1">Some prose here.</p>')
    data = translations_for(page, {"Some prose here.": "这里有一些正文。"}, nav=NAV)

    result = render(page, data, glossary=NO_GLOSSARY)

    assert '<option value="Ch001.html" selected>第 1 章 引言</option>' in result.zh_html
    assert '<option value="Ch001.html#st0010">摘要</option>' in result.zh_html
    assert '<optgroup label="第 1 章 引言">' in result.zh_html
    assert "Chapter 1. Introduction" not in result.zh_html


def test_nav_buttons_are_localized():
    page = make_page('<p id="p1">Some prose here.</p>')
    data = translations_for(page, {"Some prose here.": "这里有一些正文。"}, nav=NAV)

    result = render(page, data, glossary=NO_GLOSSARY)

    assert "首页" in result.zh_html
    assert "上一页" in result.zh_html and "下一页" in result.zh_html
    assert ">Home<" not in result.zh_html


def test_every_page_carries_a_language_switch_to_the_same_chapter():
    page = make_page('<p id="p1">Some prose here.</p>')
    data = translations_for(page, {"Some prose here.": "这里有一些正文。"},
                            page="Ch001", nav=NAV)

    result = render(page, data, glossary=NO_GLOSSARY)

    assert '<a class="langbtn" href="../../chapters/Ch001.html">EN</a>' in result.zh_html
    assert '<a class="langbtn" href="../../bilingual/chapters/Ch001.html">对照</a>' \
        in result.zh_html
    assert '<a class="langbtn" href="../../zh/chapters/Ch001.html">中</a>' \
        in result.bilingual_html


def test_the_bilingual_nav_shows_both_languages():
    page = make_page('<p id="p1">Some prose here.</p>')
    data = translations_for(page, {"Some prose here.": "这里有一些正文。"}, nav=NAV)

    result = render(page, data, glossary=NO_GLOSSARY)

    assert ('<option value="Ch001.html" selected>Chapter 1. Introduction / 第 1 章 引言'
            '</option>') in result.bilingual_html


def test_the_chinese_page_declares_chinese():
    page = make_page('<p id="p1">Some prose here.</p>')
    data = translations_for(page, {"Some prose here.": "这里有一些正文。"})

    result = render(page, data, glossary=NO_GLOSSARY)

    assert 'lang="zh-CN"' in result.zh_html.split("<body")[0]
    assert 'lang="en"' not in result.zh_html.split("<body")[0]
