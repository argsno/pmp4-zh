# 03 — Mobile content column

**What to build:** The reading column becomes usable on phones. The EPUB stylesheet indents every block `div` 2em a side, which compounds across nesting and leaves a 375px phone very little reading width. At ≤768px those side margins are cut to 1em; at ≤480px they drop to ~0.6em, the content base font rises to 17px (so Chinese text reads comfortably; percentage-based element sizes scale with it), and the content column widens to ~96%. These rules apply to all three sites including the English one, not just Chinese pages. Wide tables and code blocks keep scrolling horizontally inside their own block rather than forcing the page to scroll.

**Blocked by:** 01 — Viewport meta on every chapter page.

**Status:** implemented

- [x] At ≤768px, side margins of the nested content blocks are ~1em (halved from 2em) on all three sites.
- [x] At ≤480px, side margins are ~0.6em, body text renders at ~17px, and the content column occupies ~96% of the viewport.
- [x] At 375px, the page has no horizontal scroll; only tables and code blocks scroll within their own containers.
- [x] The same rules affect the English site, not just Chinese — the English mobile experience matches.
- [x] Desktop rendering (≥769px) is unchanged.
