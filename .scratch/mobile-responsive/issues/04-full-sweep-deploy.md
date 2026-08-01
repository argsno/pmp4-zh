# 04 — Full-site mobile sweep + deploy

**What to build:** The mobile adaptation is verified end-to-end across all three sites, any straggler conflicts left over from tickets 02 and 03 (e.g. an Elsevier class that sets its own `!important` margins and shrugs off the global trim) are fixed, and the result ships to the live GitHub Pages site. This is the manual gate before publishing.

**Blocked by:** 02 — Mobile navigation bar layout; 03 — Mobile content column.

**Status:** in-progress (sweep + fixes done, pending review/commit/deploy)

- [x] Sweep at 375/480/768px over representative pages — a content-heavy chapter, a table-heavy chapter, a math/formula-heavy chapter, and a landing page — on all three sites (en/zh/bilingual).
- [x] Any elements that resist the margin trim or overflow at phone widths are individually fixed; the final state shows no horizontal page scroll and no cramped text.
- [x] A local HTTP server preview (device emulation) is what the sweep is run against, not guesses.
- [ ] After the sweep passes, the changes are pushed to main and the live site is confirmed to render the mobile layout.
