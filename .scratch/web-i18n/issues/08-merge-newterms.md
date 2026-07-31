# 08 — Merge `newterms.json` + revise `TRANSLATION_STANDARDS.md`

**What to build:** Fold the per-page newterms findings back into the terminology glossary and amend the standards document so it matches what was actually done, keeping the standard and the practice from drifting apart.

**Blocked by:** 07 — all translation is done and newterms files are collected first.

**Status:** ready-for-agent

- [ ] Consolidated new terms are merged into the glossary with agreed Chinese renderings.
- [ ] §4.6 is updated to record that nav display text is now localized while the option `value` is preserved.
- [ ] §6.2 is tightened from "uniform across the book" to the enforced mandatory CJK spacing rule, since the loose wording would have produced inconsistency under concurrent translation.

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
