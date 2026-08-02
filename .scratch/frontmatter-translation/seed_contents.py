#!/usr/bin/env python3
"""Seed the Contents page's translations from `translations/nav.json`.

The printed Table of Contents lists exactly the entries the chapter dropdown
lists, so every one of its 288 nodes is a string nav.json already has a
maintainer-reviewed rendering for.  Re-translating them by hand would be both
wasted work and a way to drift the two apart: the same chapter would be named
one thing in the dropdown and another in the table of contents.

Each node is either bare text or one inline element wrapping the whole label
(`【1】Chapter 1. Introduction【/1】`, the link).  The placeholder gate compares
the marker sets either side, so the wrapper is preserved and only the text
inside it is swapped.

Idempotent: run it again after `extract --force` to re-seed.
"""
import glob
import json
import os
import re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
CONTENTS = os.path.join(ROOT, "translations", "Contents")
NAV = os.path.join(ROOT, "translations", "nav.json")

WRAPPED = re.compile(r"^【(\d+)】(.*)【/\1】$", re.S)

# One entry carries markup *inside* the label: §17.3's title is
# `Computing F<sup>H</sup>D`, the MRI reconstruction operator.  The dropdown
# flattens it to `17.3 Computing FHD`, so nav.json is keyed by the flat form
# and cannot say where the superscript goes.  Rather than guess by searching
# the Chinese for `FHD` — which would silently mangle any future entry whose
# markup lands elsewhere — the one case states its own answer.
INNER_MARKUP = {
    "17.3 Computing F【2】H【/2】D": "17.3 计算 F【2】H【/2】D",
}


def main():
    with open(NAV, encoding="utf-8") as fh:
        nav = json.load(fh)

    seeded = missing = 0
    for path in sorted(glob.glob(os.path.join(CONTENTS, "part-*.json"))):
        with open(path, encoding="utf-8") as fh:
            shard = json.load(fh)
        for node in shard["nodes"]:
            english = node["en"]
            match = WRAPPED.match(english)
            inner = match.group(2) if match else english
            chinese = INNER_MARKUP.get(inner.strip()) or nav.get(inner.strip())
            if chinese is None:
                missing += 1
                print("no nav.json entry for %r" % inner[:60])
                continue
            if match:
                node["zh"] = "【%s】%s【/%s】" % (match.group(1), chinese,
                                              match.group(1))
            else:
                node["zh"] = chinese
            seeded += 1
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(shard, fh, ensure_ascii=False, indent=2)
            fh.write("\n")

    print("seeded %d node(s); %d without a nav.json entry" % (seeded, missing))
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
