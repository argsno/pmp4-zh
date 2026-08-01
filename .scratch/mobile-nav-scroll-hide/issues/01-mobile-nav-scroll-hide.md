# 01 — Mobile: auto-hide the top nav on scroll-down, reveal on scroll-up

**What to build:** On phones (≤640px viewport) the top navigation bar slides up out of the way while the reader scrolls down through a chapter, reclaiming reading space; scrolling up even a little brings it back immediately. The bar never disappears within ~100px of the page top or ~200px of the page bottom, so the chapter dropdown and prev/next buttons stay reachable exactly when they are needed. It also stays put while the reader is actually using it — chapter select open, a button focused or pressed. The always-fixed bar on desktop is untouched. The 0.2s slide respects the OS "Reduce Motion" setting by toggling instantly when it is on. The behaviour is shared, so it works the same on the English, Chinese, and bilingual sites and on the landing page.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] On a ≤640px viewport, cumulative scroll-down of ≥20px hides the bar with a ~0.2s slide; any upward scroll reveals it immediately.
- [ ] The bar always stays visible within ~100px of the page top and ~200px of the page bottom.
- [ ] The bar stays visible while the reader interacts with it (chapter select open, buttons focused or pressed).
- [ ] The behaviour activates only on mobile widths; desktop keeps the always-fixed bar with no regression.
- [ ] With the OS "Reduce Motion" setting on, the bar toggles instantly without the slide animation.
- [ ] The behaviour is identical across the English, Chinese, and bilingual sites and the landing page, via the single shared asset.
- [ ] Rebuilding the site cleanly regenerates all pages (the language sites' asset symlinks stay intact) and the full test suite passes, including new assertions that the generated CSS/JS contain the hidden-state rules and scroll wiring.
