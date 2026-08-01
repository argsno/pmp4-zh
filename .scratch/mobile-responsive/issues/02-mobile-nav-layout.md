# 02 — Mobile navigation bar layout

**What to build:** On narrow screens the top navigation bar reorganizes into deliberate rows and becomes touch-friendly, with every control still visible (no hamburger). At ≤640px the flex container reorders its children so the layout reads as: row 1 = book title + language switch (EN/中/对照), row 2 = chapter selector full-width, row 3 = Home/Prev/Next buttons. At ≤480px the book title shrinks and truncates with an ellipsis instead of overflowing, and all tappable controls (nav buttons, language buttons, the select) get ~40px+ touch targets. The chapter `<select>` stays as-is because it renders as a native mobile picker.

**Blocked by:** 01 — Viewport meta on every chapter page.

**Status:** implemented

- [x] At ≤640px viewport width, the bar shows the three rows in the approved order (title+langswitch / select / buttons) on all three sites.
- [x] At ≤480px the title is truncated with an ellipsis and never overflows its row, on both the English and localized (Chinese) titles.
- [x] At ≤480px, nav and language buttons have a touch height of at least 40px, and the chapter select is at least 40px tall.
- [x] English pages (which have no language switch) still lay out cleanly — no orphaned gaps or broken rows.
- [x] The rebuilt bar is identical across desktop widths (no regression above 640px).
