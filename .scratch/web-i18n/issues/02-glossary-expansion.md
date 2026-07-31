# 02 — Expand terminology glossary to ~250 entries + freeze

**What to build:** The terminology table expanded from its current ~70 entries to ~250, covering the book's core CUDA/GPU concepts (scan/prefix sum, reduction, histogram, stencil, sparse-matrix formats CSR/ELL/JDS/COO, merge, BFS, dynamic parallelism, streams, privatization, atomic operations, pinned memory, pooling, and similar). It is reviewed and frozen by the maintainer before any translation starts, so translation tasks never disagree on a term.

**Blocked by:** None — can start immediately.

**Status:** awaiting-gate-1

- [x] Glossary holds roughly 250 entries spanning the concepts named in the standards, each giving the English term and its mandated Chinese rendering. — **345 entries** across 10 topic sections (§5.1–§5.10). See note below on the count.
- [x] A maintainer can compile the book against this glossary without discovering large gaps in core concepts. — verified by frequency analysis over the 23 chapter pages: every 2–3 word technical phrase occurring ≥60 times is either in the glossary or a plain-prose/inflected form of a covered term.
- [x] Glossary is marked frozen; translation tasks treat it as read-only and record any new out-of-glossary term in a per-page newterms file rather than editing the shared table. — §5.0 states the freeze and the `translations/<page-stem>/newterms.json` protocol; §9.3, which previously told translators to edit §5 directly, was corrected to match.

**Note on entry count:** the spec estimated ~250; the delivered table has 346. The estimate was a guess at how many rows it takes to cover the book, not a budget. Two things pushed the real number higher:

1. Coverage was derived from the book's own index and a phrase-frequency pass rather than from memory, which surfaced whole clusters the estimate missed (numerical/floating-point in Ch. 22, MPI in Ch. 20, the MRI and molecular-dynamics case studies in Ch. 17–19).
2. Rows where two English terms have two different Chinese renderings were split into one row each (`input tile` / `output tile`, `push` / `pull implementation`, …). Packing them onto one line reads fine for a human but makes the renderer's terminology check unable to tell which term maps to which rendering. ~14 rows came from this.

A first draft reached 415 entries; ~70 were then cut as plain English words whose inclusion would have caused false violations in the renderer's check (`scope`, `flexibility`, `rank`, `gradient`, `precision`, `trade-off`, …) or as trivially compositional (`memory access efficiency`, `launch overhead`). If the maintainer still wants ~250, the next cut would come out of §5.5 and §5.8, but it would remove real book terminology rather than noise.

**The invariant that makes user story 2 hold.** Spec user story 2 is *"术语在全书范围内译法一致，我不会误以为「扫描」和「前缀和」是两个不同的概念"*. The table now enforces this structurally, and it is checked mechanically:

- no English term maps to more than one Chinese rendering (the Chinese column never contains alternatives — an earlier draft allowed `扫描 / 前缀和`, which would have permitted exactly the confusion the story forbids);
- no Chinese rendering is reused for two different English concepts (the converse failure);
- no duplicate English keys across all 10 sections.

`scan` and `prefix sum` are therefore both mandated as 扫描, with 首现 written as "扫描（prefix sum）" to keep the link to the English.

**Two fixes to pre-existing content, found while checking the above:**

- `warp divergence | 线程束分化` (inherited from the old table) was deleted: the phrase occurs **zero** times in the book, and its rendering contradicted `control divergence | 控制发散` for the same phenomenon.
- The closing line of the file and §9.3 both told translators to add new terms to §5 directly, which contradicts the freeze. Both now point at `newterms.json`.

**Open question for Gate 1 (belongs to the translation tickets, 06/07, not this one).** §5's 首现 rule and §7 both say 首次出现 bilingual, 后文直接用中文 — written for a single translator working front-to-back. Under 32 independently-translated pages, "后文" has no shared meaning. Someone has to decide whether 首现 is per-book or per-page before translation starts. I left both statements untouched rather than inventing a rule here.

**Gate 1:** maintainer sign-off on the expanded glossary precedes all translation work. — **pending.**
