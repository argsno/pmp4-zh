# 04 — Pytest test suite (single seam)

**What to build:** A test harness that proves external behavior only through `render(page_html, translations)`, establishing the repo's testing precedent (the repo currently has no pytest / pyproject / tests directory). A real chapter page is the large fixture for the identity round-trip; small hand-written HTML fragments back each single-point behavior. No test reaches into extraction or injection internals, so those pieces can be refactored freely.

**Blocked by:** 03 — the engine must exist to be driven.

**Status:** ready-for-agent

- [ ] Flagship identity test: rendering a real chapter with `zh == en` yields output byte-identical to the English page except the top navigation and the `lang` attribute — proving extraction covered everything and injection lost nothing.
- [ ] Single-point tests cover: placeholder moved / inserted / deleted / re-numbered / unclosed each producing a violation and no page; `pre` / `math` / bibliography absent from translatable nodes yet preserved; zero-width element counts unchanged; bilingual block doubling with `zh-trans` present and `pre` / references not doubled; CJK space normalization (`使用CUDA编程` → `使用 CUDA 编程`, no space around Chinese punctuation); empty / English-only `zh` flagged; nav option `value` unchanged while display text is localized.
- [ ] All tests run via a single interface (pytest) and assert on produced HTML or violation contents, never on internal helpers.
