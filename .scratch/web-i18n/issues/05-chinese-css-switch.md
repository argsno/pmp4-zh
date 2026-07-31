# 05 — Chinese typeset CSS + `EN / 中 / 对照` switch + bilingual nav styling

**What to build:** The presentation layer for the two new sites — a Chinese typesetting stylesheet (CJK font stack, line height, the `.zh-trans` visual treatment) and the three-way language switch plus bilingual nav display that the renderer emits. This is a distinct front-end concern from the engine's logic, but it consumes the markup and classes the engine produces.

**Blocked by:** 03 — the engine emits the nav / switch markup and the `zh-trans` class this ticket styles.

**Status:** ready-for-agent

- [ ] Chinese body text uses a CJK-friendly font stack and comfortable line height across both the zh and bilingual pages.
- [ ] Bilingual Chinese blocks are visually distinct (left rule + faint background) and remain readable on mobile.
- [ ] Every page carries a working `EN / 中 / 对照` switch that stays on the same chapter; the zh nav shows Chinese labels, the bilingual nav shows English + Chinese titles; option `value` attributes are never changed.
