# 06 — First batch: translate + render 4 representative pages

**What to build:** The end-to-end proof of the whole pipeline on four deliberately different pages — chapter 1 (style baseline), a figure-dense chapter, chapter 16 (the most block-level nodes, 261), and the preface (a different register) — rendered into zh + bilingual with a Chinese landing `index.html`. This is the tracer bullet: if these four render correctly and read well, the remaining 28 are the same shape.

**Blocked by:** 02 (glossary frozen), 04 (harness green), 05 (styles + switch present).

**Status:** ready-for-agent

- [ ] All four pages render in zh and bilingual with zero violations and pass the test harness.
- [ ] The Chinese landing index lists chapters in Chinese.
- [ ] A maintainer confirms in a browser that translation style and bilingual layout are acceptable before further pages proceed (Gate 2).
