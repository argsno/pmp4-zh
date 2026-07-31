# 09 — Integrate `build_i18n` into the site builder

**What to build:** Wire the i18n pipeline into the existing single build command so rebuilding the English site also rebuilds the zh and bilingual sites. The dependency stays one-way: the builder imports `build_i18n`, and `build_i18n` never imports the builder.

**Blocked by:** 03 (engine exists), 06 (pipeline proven on the first batch).

**Status:** ready-for-agent

- [ ] Running the existing build command regenerates EN + zh + bilingual in one pass.
- [ ] The builder imports `build_i18n`; `build_i18n` contains no import of the builder.
- [ ] A page that fails validation is reported and skipped rather than emitting a broken page.
