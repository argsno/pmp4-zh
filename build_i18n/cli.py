"""Command line entry points.

    python -m build_i18n extract     # write empty translation skeletons
    python -m build_i18n render      # build web/zh and web/bilingual
    python -m build_i18n validate    # run the same gates, write nothing

A page whose translation trips a gate is reported and skipped.  Half-rendered
pages are never written: a missing page is a problem someone will fix, a subtly
broken one is a problem nobody will notice.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import pathlib
import sys

from .document import Document
from .glossary import load_glossary
from .nav import nav_labels
from .render import extract, render

WEB = "web"
TRANSLATIONS = "translations"
NAV_FILE = "nav.json"
SITES = ("zh", "bilingual")
# The EPUB's own navigation document: a machine artefact, not a readable page.
NOT_A_PAGE = frozenset({"nav.html"})
SHARD_CHARS = 8000
MAX_REPORT = 5


def main(argv=None):
    args = _parser().parse_args(argv)
    return args.run(args)


# ---------------------------------------------------------------------------
# extract
# ---------------------------------------------------------------------------
def _extract(args):
    """Empty skeletons, sharded so a translator's reply is never truncated."""
    web, root = pathlib.Path(args.web), pathlib.Path(args.translations)
    labels, written, kept, nodes = {}, 0, 0, 0
    for path in _pages(web, args.only):
        page_html = _read(path)
        for label in _nav_labels(page_html):
            labels.setdefault(label, "")
        directory = root / path.stem
        if any(directory.glob("part-*.json")) and not args.force:
            kept += 1
            continue
        stored = _stored_nodes(directory)
        fresh = extract(page_html, path.stem)["nodes"]
        _write_skeleton(directory, path.stem, fresh, stored, args.shard_chars)
        written += 1
        nodes += len(fresh)
    _write_nav_skeleton(root / NAV_FILE, labels)
    print("extract: %d page(s), %d node(s) written; %d page(s) left alone"
          % (written, nodes, kept))
    return 0


def _write_skeleton(directory, page, nodes, stored, budget):
    """Rewrite one page's shards, carrying over translations that still apply."""
    done = {node.get("id"): node.get("zh", "") for node in stored}
    nodes = [dict(node, zh=done.get(node["id"], "")) for node in nodes]
    directory.mkdir(parents=True, exist_ok=True)
    for stale in directory.glob("part-*.json"):
        stale.unlink()
    for number, shard in enumerate(_shards(nodes, budget)):
        _write_json(directory / ("part-%02d.json" % number),
                    {"page": page, "nodes": shard})


def _shards(nodes, budget):
    """Split on node boundaries only; an empty page still gets one shard."""
    shard, size = [], 0
    for node in nodes:
        if shard and size + len(node["en"]) > budget:
            yield shard
            shard, size = [], 0
        shard.append(node)
        size += len(node["en"])
    yield shard


def _nav_labels(page_html):
    doc = Document(page_html)
    header = doc.find("header", "topnav")
    return [] if header is None else nav_labels(doc, header)


def _write_nav_skeleton(path, labels):
    """One shared file for the navigation, in book order."""
    stored = _read_json(path) or {}
    merged = {label: stored.get(label, "") for label in labels}
    for label, chinese in stored.items():       # translations for labels the
        if chinese and label not in merged:     # navigation no longer shows
            merged[label] = chinese
    if merged or path.exists():
        _write_json(path, merged)


# ---------------------------------------------------------------------------
# render / validate
# ---------------------------------------------------------------------------
def _render(args):
    return _build(args, write=True)


def _validate(args):
    return _build(args, write=False)


def _build(args, write):
    web, root = pathlib.Path(args.web), pathlib.Path(args.translations)
    glossary = load_glossary()
    nav = _read_nav(root / NAV_FILE)
    if write:
        for site in SITES:
            _provision(web, site)

    done, failed = 0, 0
    for path in _pages(web, args.only):
        page_html = _read(path)
        translations = _page_translations(page_html, path.stem, nav,
                                          _stored_nodes(root / path.stem),
                                          args.allow_untranslated)
        result = render(page_html, translations, glossary=glossary,
                        require_translated=not args.allow_untranslated)
        if result.violations:
            failed += 1
            _report(path.name, result.violations, args.max_report)
            continue
        done += 1
        if write:
            for site, html in (("zh", result.zh_html),
                               ("bilingual", result.bilingual_html)):
                (web / site / "chapters" / path.name).write_text(
                    html, encoding="utf-8")

    print("%s: %d page(s) ok, %d skipped"
          % ("render" if write else "validate", done, failed))
    return 1 if failed else 0


def _page_translations(page_html, stem, nav, stored, fill_english):
    """What `render` is handed for one page.

    With `fill_english` the untranslated remainder is filled in with the English
    text, which renders a browsable draft of a page nobody has translated yet.
    """
    nodes = [node for node in stored
             if not fill_english or (node.get("zh") or "").strip()]
    if fill_english:
        done = {node.get("id") for node in nodes}
        nodes += [{"id": node["id"], "zh": node["en"]}
                  for node in extract(page_html, stem)["nodes"]
                  if node["id"] not in done]
    return {"page": stem, "nav": nav, "nodes": nodes}


def _provision(web, site):
    """Give a site root the assets its pages ask for, without copying them.

    The renderer never touches `<head>`, so a page under `web/<site>/chapters/`
    still asks for `../styles` and `../images`.  Those become symlinks back to
    the English originals: one copy of 35MB of images and fonts, not three.  A
    real file already sitting in the site root — a Chinese stylesheet, a
    translated landing page — is left alone.
    """
    root = web / site
    (root / "chapters").mkdir(parents=True, exist_ok=True)
    for entry in sorted(web.iterdir()):
        if entry.name in SITES or entry.name == "chapters":
            continue
        link, target = root / entry.name, os.path.join("..", entry.name)
        if link.is_symlink():
            if os.readlink(link) == target:
                continue
            link.unlink()
        elif link.exists():
            continue
        link.symlink_to(target)


def _report(name, violations, limit):
    print("%s: %d violation(s)" % (name, len(violations)), file=sys.stderr)
    for violation in violations[:limit]:
        print("  %s" % violation, file=sys.stderr)
    if len(violations) > limit:
        print("  … and %d more" % (len(violations) - limit), file=sys.stderr)


# ---------------------------------------------------------------------------
# Files
# ---------------------------------------------------------------------------
def _pages(web, only):
    paths = sorted(path for path in (web / "chapters").glob("*.html")
                   if path.name not in NOT_A_PAGE)
    if not only:
        return paths
    patterns = [p if any(c in p for c in "*?[") else "*%s*" % p for p in only]
    return [path for path in paths
            if any(fnmatch.fnmatch(path.name, p) for p in patterns)]


def _stored_nodes(directory):
    nodes = []
    for part in sorted(directory.glob("part-*.json")):
        nodes.extend(_read_json(part).get("nodes", []))
    return nodes


def _read_nav(path):
    return {english: chinese
            for english, chinese in (_read_json(path) or {}).items() if chinese}


def _read(path):
    return path.read_text(encoding="utf-8")


def _read_json(path):
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")


# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
def _parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--web", default=WEB, metavar="DIR",
                        help="the English site (default: %(default)s)")
    common.add_argument("--translations", default=TRANSLATIONS, metavar="DIR",
                        help="translation store (default: %(default)s)")
    common.add_argument("--only", action="append", metavar="PATTERN",
                        help="page name or glob; repeatable")

    parser = argparse.ArgumentParser(
        prog="python -m build_i18n", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)

    extract_cmd = commands.add_parser(
        "extract", parents=[common], help="write empty translation skeletons")
    extract_cmd.add_argument(
        "--force", action="store_true",
        help="re-extract pages that already have shards, keeping the "
             "translations of nodes that still exist")
    extract_cmd.add_argument("--shard-chars", type=int, default=SHARD_CHARS,
                             metavar="N", help="English characters per shard "
                             "(default: %(default)s)")
    extract_cmd.set_defaults(run=_extract)

    for name, run, help_text in (
            ("render", _render, "build the zh and bilingual sites"),
            ("validate", _validate, "run the gates without writing anything")):
        command = commands.add_parser(name, parents=[common], help=help_text)
        command.add_argument(
            "--allow-untranslated", action="store_true",
            help="fill anything not yet translated with the English text and "
                 "skip the Chinese-text and glossary gates")
        command.add_argument("--max-report", type=int, default=MAX_REPORT,
                             metavar="N", help="violations printed per failing "
                             "page (default: %(default)s)")
        command.set_defaults(run=run)
    return parser
