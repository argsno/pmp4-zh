# 05 — Chinese typeset CSS + `EN / 中 / 对照` switch + bilingual nav styling

**What to build:** The presentation layer for the two new sites — a Chinese typesetting stylesheet (CJK font stack, line height, the `.zh-trans` visual treatment) and the three-way language switch plus bilingual nav display that the renderer emits. This is a distinct front-end concern from the engine's logic, but it consumes the markup and classes the engine produces.

**Blocked by:** 03 — the engine emits the nav / switch markup and the `zh-trans` class this ticket styles.

**Status:** done

- [x] Chinese body text uses a CJK-friendly font stack and comfortable line height across both the zh and bilingual pages.
- [x] Bilingual Chinese blocks are visually distinct (left rule + faint background) and remain readable on mobile.
- [x] Every page carries a working `EN / 中 / 对照` switch that stays on the same chapter; the zh nav shows Chinese labels, the bilingual nav shows English + Chinese titles; option `value` attributes are never changed.

**Notes:**
- English-site switch deferred to ticket 09 (per user decision).
- CJK font: sans-serif stack (PingFang SC / Microsoft YaHei / Noto Sans CJK SC), Latin faces first.
- `web/chinese.css` imported via `@import` from `topnav.css` (renderer cannot touch `<head>`).
- All rules scoped to `[lang="zh-CN"]` or `.zh-trans` — zero visual impact on English pages.
- `!important` used throughout to out-specify override_v1.css's `#book-content #sbo-rt-content p { font-family ... !important }`.
