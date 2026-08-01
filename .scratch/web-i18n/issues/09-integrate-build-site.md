# 09 — Integrate `build_i18n` into the site builder

**What to build:** Wire the i18n pipeline into the existing single build command so rebuilding the English site also rebuilds the zh and bilingual sites. The dependency stays one-way: the builder imports `build_i18n`, and `build_i18n` never imports the builder.

**Blocked by:** 03 (engine exists), 06 (pipeline proven on the first batch).

**Status:** done

- [x] Running the existing build command regenerates EN + zh + bilingual in one pass.
- [x] The builder imports `build_i18n`; `build_i18n` contains no import of the builder.
- [x] A page that fails validation is reported and skipped rather than emitting a broken page.

Exit-status contract: `python build_site.py` now returns the i18n renderer's status
(0 all pages ok, 1 some skipped, 2 store broken).  The 4 out-of-scope pages
(Index/Contents/Copyright/Title_page) always skip, so a full build reports 33 ok,
4 skipped and exits 1 — same as `python -m build_i18n render` already did.
