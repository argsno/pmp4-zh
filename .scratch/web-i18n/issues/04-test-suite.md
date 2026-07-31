# 04 — Pytest test suite (single seam)

**What to build:** A test harness that proves external behavior only through `render(page_html, translations)`, establishing the repo's testing precedent (the repo currently has no pytest / pyproject / tests directory). A real chapter page is the large fixture for the identity round-trip; small hand-written HTML fragments back each single-point behavior. No test reaches into extraction or injection internals, so those pieces can be refactored freely.

**Blocked by:** 03 — the engine must exist to be driven.

**Status:** done

- [x] Flagship identity test: rendering a real chapter with `zh == en` yields output byte-identical to the English page except the top navigation and the `lang` attribute — proving extraction covered everything and injection lost nothing. `tests/test_render.py::test_identity_roundtrip_reproduces_the_english_page` (+ a guard that the chapter really has >50 prose nodes).
- [x] Single-point tests cover: placeholder inserted / deleted / re-numbered / unclosed (each a `placeholder-mismatch` violation, no page emitted) in `tests/test_render.py::test_broken_placeholders_are_a_violation_and_no_page_is_written`; `pre` / `math` / bibliography absent from translatable nodes yet preserved; zero-width element counts unchanged; bilingual block doubling with `zh-trans` present and `pre` / references not doubled; CJK space normalization (`使用CUDA编程` → `使用 CUDA 编程`, no space around Chinese punctuation); empty / English-only `zh` flagged; nav option `value` unchanged while display text is localized.
- [x] All tests run via a single interface (pytest) and assert on produced HTML or violation contents, never on internal helpers. `pyproject.toml` now pins `testpaths`/`pythonpath` so `pytest` is the one entrypoint; `conftest.py` keeps `build_i18n` importable.

Note on "placeholder **moved**": the engine validates placeholder *sets*, not
order, so reordering a placeholder to Chinese word order is intentionally
*allowed* (`tests/test_render.py::test_paired_placeholders_may_move_to_the_chinese_word`,
a passing test). A "moved → violation" case would contradict that, so malformed
moves are instead covered by the `inverted` / `unclosed` cases. The spec's
"moved … producing a violation" is therefore interpreted as malformed
re-positioning, not legitimate reordering.
