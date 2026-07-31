# 03 — `build_i18n` render engine (the `render()` seam)

**What to build:** A deterministic rendering module exposing `render(page_html, translations)` that turns one English page plus its structured translation data into a Chinese page and a bilingual page, or reports violations. It owns: extraction of translatable nodes (`p`, `li`, `h1`–`h4`, `figcaption`, `td`, `th`, `caption`, excluding `pre`, `math`, bibliography entries, and the generated top nav); the placeholder grammar (paired `【N】…【/N】`, atomic `【MN】`, zero-width stripped-then-reinserted); injection back into structure; bilingual interleaving; CJK space normalization; the renderer-generated localized top navigation; and the six hard validations. It also provides CLI entry points to extract empty skeletons, render all three sites, and run validation standalone. The module must stay unaware of the existing site builder (one-way dependency).

**Blocked by:** None — can start immediately (reads the translation standards and the glossary read-only).

**Status:** ready-for-agent

- [ ] `render(page_html, translations)` returns `zh_html` / `bilingual_html` (or `None` when violations exist) plus a list of violations.
- [ ] Extractable nodes are limited to the specified element set; `pre`, `math`, and bibliography entries never appear as translatable nodes and survive in the output byte-identical.
- [ ] Placeholder sets are validated as exactly equal between source and translation (no add / remove / re-number / mismatch), and zero-width anchors / pagebreaks are re-inserted at the start of their node.
- [ ] Bilingual output doubles block-level nodes, marks Chinese blocks with a `zh-trans` class, and does not duplicate `pre` / `math` / references.
- [ ] CLI can extract skeletons, render all three sites, and validate independently; a failing page is skipped, never emitted broken.
