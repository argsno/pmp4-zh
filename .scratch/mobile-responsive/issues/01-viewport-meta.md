# 01 — Viewport meta on every chapter page

**What to build:** Every chapter page across all three sites (English, Chinese, bilingual) carries a viewport meta tag, so mobile browsers render the page at the real device width instead of scaling the desktop layout down from ~980px. Without this, none of the responsive media queries ever fire on a phone. The landing pages already have the tag; the 23×3 chapter pages do not.

**Blocked by:** None — can start immediately.

**Status:** implemented

- [x] After a rebuild, every chapter page in all three sites contains a `<meta name="viewport" content="width=device-width, initial-scale=1"/>` in its `<head>`.
- [x] The tag comes from the build step, not from editing the EPUB source files, so future rebuilds keep it.
- [ ] In DevTools device emulation at 375px width, a chapter page's layout viewport is ~375px (no desktop-width zoom-out).
- [x] The full rebuild completes without render failures on the translation pages.
