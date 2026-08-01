# 08 — Merge `newterms.json` + revise `TRANSLATION_STANDARDS.md`

**What to build:** Fold the per-page newterms findings back into the terminology glossary and amend the standards document so it matches what was actually done, keeping the standard and the practice from drifting apart.

**Blocked by:** 07 — all translation is done and newterms files are collected first.

**Status:** done

- [x] Consolidated new terms are merged into the glossary with agreed Chinese renderings.
- [x] §4.6 is updated to record that nav display text is now localized while the option `value` is preserved.
- [x] §6.2 is tightened from "uniform across the book" to the enforced mandatory CJK spacing rule, since the loose wording would have produced inconsistency under concurrent translation.

## Merge outcome

**446 entries** merged into §5 (glossary grows 351 → 797). Full `validate`: **33 pages ok, 4 skipped** (unchanged).

- **52 translation nodes** were surgically reconciled to a single agreed rendering so that cross-page inconsistencies could be merged rather than dropped (e.g. 活动线程 → 活跃线程 in Ch007/008/009/018; 非活动线程 → 非活跃线程 in Ch004; 以…为中心分解 → 面向…分解 in Ch018; 公共副本 → 公有副本; 数据复用 → 数据重用; 浮点运算 → 浮点算术 where it denoted floating-point *arithmetic*, keeping it distinct from §5.7 FLOP = 浮点运算). These are prose-only edits; no placeholders or code/formula blocks touched.
- **4 duplicates** of existing §5 rows skipped (identical renderings): `Bezier curve`, `quadtree`, `stub function`, `OpenACC`.
- **Rendering corrected to match practice**: `biased encoding → 移码（有偏）编码` (was 偏置编码, which its own page never used). `AI` / `CUDA FORTRAN` / `C++AMP` / `Visual Profiler` normalized to the `保留英文` convention.
- **21 entries NOT merged** (recorded renderings cannot be enforced without breaking pages or distorting prose):

| entry | reason |
|---|---|
| `order (of a control point)` → 阶 | plain word; `order` appears in 88 nodes as ordinary English |
| `feature`, `pass`, `accuracy`, `accessibility`, `flexibility`, `observation`, `approximation`, `batch`, `overflow`, `scope`, `sensor (DRAM sensing)` | plain-English-word class (issue 02 already cut `scope`/`flexibility`/`rank`); enforcing would mandate renderings for ordinary usage |
| `rank` → 秩 | plain word; MPI rank is already §5.9 `MPI rank → MPI 进程号` |
| `Outline`, `Fundamental Concepts` | UI headings; `Outline` also conflicts with 本章大纲 (translations) vs 本章概要 (nav.json) |
| `lifetime` → 生命周期 | Foreword uses "in my lifetime" as ordinary English — needs a denylist entry, which is the separate false-positive task (§5) |
| `streak` → 连串更新, `blockage` → 阻塞 | translations paraphrase; forcing the rendering would distort the sentence |
| `arithmetic to global memory access ratio`, `floating-point to global memory access ratio`, `compute to memory access ratio` | ratio-family variants whose pages disagree on 之比/比 and 算术/浮点; §5.4 `compute to global memory access ratio` and the safe `arithmetic-to-global memory access ratio` (Ch007) cover the family |

The 23 `glossary false positive` records were not merged either; they are the denylist task's backlog (ticket §5, out of scope here). `newterms.json` files are left in place as the provenance record.

## Proposal context (from the ticket 06 co-owned glossary-merge task)

Two near-duplicate working proposals lived at the repo root (`glossary_proposal.md`,
`glossary_section5_proposal.md`). Their load-bearing analysis is folded in here and the
loose files are removed.

**Scope warning:** those proposals covered only the ticket-06 batch (Ch001 / Ch003 /
FigureP.1, 17 net entries). Ticket 07 added ~28 more pages with their own `newterms.json`.
Collect the **full inventory across all 32 translatable pages** before merging; the
analysis below carries over regardless of which entries are in the final set.

### Normalization decisions that carry over

1. **Substring collision — headword wins (terascale / exascale).** Ch001 recorded
   headwords (`terascale → 万亿次级`, `exascale → 百亿亿次级`); FigureP.1 recorded phrase
   forms (`terascale computing → 万亿次级计算`, `exascale computing → 百亿亿次级计算`).
   The short entry is the *strictly weaker constraint*: `terascale → 万亿次级` is
   satisfied by prose using either form (万亿次级 is a substring of 万亿次级计算), whereas
   the long form is satisfied only by the exact long string. Adding the long forms would
   retroactively fail FigureP.1 p0015, which uses the short form. Keep headword forms only;
   do **not** add `* computing` entries.
2. **The merge is a gate change, not an append.** Every §5 entry can retroactively fail an
   already-passing page (read-only simulation showed FigureP.1 go 0 → 1 glossary violation
   when the long form was overlaid). Before landing any entry, check it against all existing
   translations; after applying the full set, run a **full `validate` across every page**,
   not just the changed one.
3. **Safe entries.** `保留英文` entries (e.g. `Volta / Turing / Ampere`) resolve to no
   mandated Chinese in `glossary.py` and can never offend — safe to add.
4. **Related gate behavior.** The `verbatim-drift` gate is order-sensitive at page level:
   atomic 【M】 blocks must keep English source order. Incidents of real 【M】 transpositions
   were caught and corrected on Ch16 during ticket 06.
5. **False-positive class (separate owned task).** The gate over-fires on ambiguous common
   nouns (`reduction` in "cost reductions"). Neither the mandated rendering nor the
   keep-English hatch fixes it; the fix is an allowlist in `build_i18n/glossary.py`
   `offending_terms` (or disambiguated entries like `reduction (parallel pattern)`). This is
   a shared-code change and is **out of scope** for this ticket — needs its own task.
