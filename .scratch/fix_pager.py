"""Fix the Prev/Next chapter navigation across all three built sites.

The generator (build_site.py) computes Next against a subsection-level list,
so "Next" lands on the next subsection of the *same* chapter (a self-link).
This rewrites the broken links in the already-built docs/ so the live site is
correct. It is idempotent and safe to re-run after any rebuild.

Order is derived from the source "Prev" links, which already form a single
complete linked list (Cover -> ... -> Index). That chain is the publisher's
intended reading order and is authoritative.

For each page:
  - Next  -> bare filename of the next page in the chain (or ../index.html on
             the last page).
  - Prev  -> bare filename of the previous page in the chain; the first page's
             disabled "Prev" span becomes a ../index.html link.
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITES = {
    "en": os.path.join(ROOT, "docs", "chapters"),
    "zh": os.path.join(ROOT, "docs", "zh", "chapters"),
    "bilingual": os.path.join(ROOT, "docs", "bilingual", "chapters"),
}
HOME = "../index.html"

PREV_RE = re.compile(
    r'<(?:a|span) class="navbtn(?: disabled)?"(?: href="([^"]*)")?>'
    r'(&#8249; (?:Prev|上一页))</(?:a|span)>')
NEXT_RE = re.compile(
    r'<(?:a|span) class="navbtn(?: disabled)?"(?: href="([^"]*)")?>'
    r'((?:Next|下一页) &#8250;)</(?:a|span)>')


def _base(href):
    return re.sub(r'#.*$', '', href.split('/')[-1])


def reading_order(site_dir):
    """Cover -> ... -> Index, derived from the source Prev links."""
    prevmap = {}
    root = None
    for f in glob.glob(os.path.join(site_dir, "*.html")):
        base = os.path.basename(f)
        src = open(f, encoding="utf-8").read()
        m = PREV_RE.search(src)
        if not m:
            continue
        href = m.group(1)
        if not href or not href.strip() or _base(href) == "index.html":
            root = base          # disabled/empty Prev, or a Home link => first page
            continue
        target = _base(href)
        prevmap.setdefault(target, []).append(base)
    if root is None:
        raise SystemExit("no root (first page) found in %s" % site_dir)
    order, cur, seen = [root], root, set()
    while True:
        nxt = prevmap.get(cur)
        if not nxt:
            break
        nxt = nxt[0]
        if nxt in seen:
            raise SystemExit("cycle at %s in %s" % (nxt, site_dir))
        seen.add(nxt)
        order.append(nxt)
        cur = nxt
    return order


def fix_site(site_dir):
    order = reading_order(site_dir)
    pos = {p: i for i, p in enumerate(order)}
    changed = 0
    for f in glob.glob(os.path.join(site_dir, "*.html")):
        base = os.path.basename(f)
        src = open(f, encoding="utf-8").read()
        i = pos.get(base)
        if i is None:
            continue            # not part of the reading chain; leave untouched

        prev_target = HOME if i == 0 else order[i - 1]
        next_target = HOME if i == len(order) - 1 else order[i + 1]

        new = PREV_RE.sub(
            lambda m: '<a class="navbtn" href="%s">%s</a>'
            % (prev_target, m.group(2)), src)
        new = NEXT_RE.sub(
            lambda m: '<a class="navbtn" href="%s">%s</a>'
            % (next_target, m.group(2)), new)
        if new != src:
            open(f, "w", encoding="utf-8").write(new)
            changed += 1
    print("%s: %d/%d pages updated" % (os.path.basename(site_dir), changed,
                                       len(order)))
    return order


if __name__ == "__main__":
    for site_dir in SITES.values():
        fix_site(site_dir)
