#!/usr/bin/env python3
"""Ticket 04 sweep — verify the mobile layout across representative pages of
all three sites (en / zh / bilingual) at the three phone-ish widths 375, 480
and 768px, over CDP into a headless Chrome that has device-metrics override
enabled (Chrome's --window-size clamps at 500px, so only CDP can exercise the
≤480px rules).

Checks per page:
  1. The page itself must not scroll horizontally — scrollWidth must fit
     clientWidth.
  2. No element may poke past the right edge of the viewport (or hang off the
     left edge) unless it lives inside a scrollable box — tables and code
     blocks are *supposed* to scroll inside their own container (ticket 03).
  3. The content-column trim actually landed (the gate for "no cramped
     text"): on phone widths the reading column must hold ≥80% of the
     viewport, and the widest block divs inside #sbo-rt-content must carry
     the expected side margins rather than the EPUB's 2em indent.

Usage:
    python3 sweep.py            # representative pages × 3 sites × 3 widths
    python3 sweep.py --all      # every chapter page at 375px, all 3 sites

Run against a local preview: `python3 -m http.server 8833` in docs/, and a
headless Chrome with --remote-debugging-port=9222 --remote-allow-origins=*.
"""
import itertools
import json
import os
import sys
import time
import urllib.request

import websocket


def cdp(ws, method, params=None):
    mid = int(time.time() * 1000000) % 2**31
    ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == mid:
            return msg


def evaluate(ws, expression):
    res = cdp(ws, "Runtime.evaluate",
              {"expression": expression, "returnByValue": True})
    if "exceptionDetails" in res.get("result", {}):
        return None
    return res["result"]["result"].get("value")


def wait_loaded(ws, timeout=15.0):
    """Wait until the page's DOM is ready and, on chapter pages, the content
    column exists.

    A fixed sleep after Page.navigate can turn a slow load into a false pass
    (overflow measured before the content has laid out), so poll instead.
    The landing page has no #sbo-rt-content, so only `readyState` is required
    universally; the content column is awaited only when the page has one.
    """
    expr = ("document.readyState === 'complete' && "
            "(document.getElementById('sbo-rt-content') !== null || "
            " !document.getElementById('book-content'))")
    deadline = time.time() + timeout
    while time.time() < deadline:
        if evaluate(ws, expr):
            time.sleep(0.3)  # let layout settle
            return True
        time.sleep(0.15)
    return False


BASE = "http://localhost:8833"

# A content-heavy chapter, a table-heavy chapter, a math/formula-heavy
# chapter, the landing page, and a Part divider page.  Ch016 is both the
# math-heavy (43 <math> blocks) and the widest table (12 rows); Ch005
# carries the 4-column table.  The Part pages are the ones that carry the
# `<div id="PN">` that ticket 04 had to special-case.
PAGES = [
    "chapters/Ch001_1-19_B9780323912310000069.html",  # content-heavy
    "chapters/Ch005_93-121_B9780323912310000185.html",  # 4-column table
    "chapters/Ch016_355-388_B9780323912310000240.html",  # math + 12-row table
    "chapters/Part1.html",                               # part divider (#PN)
    "index.html",                                        # landing page
]
SITES = ["", "zh/", "bilingual/"]
WIDTHS = [375, 480, 768]

# Any element poking past an edge of the viewport, unless a scrollable
# ancestor contains it.  Also catches the negative-text-indent footnote
# anchors that hang off the left edge.
_OFFENDERS_JS = """\
(() => {
  const vw = document.documentElement.clientWidth;
  const bad = [];
  for (const el of document.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    const rightBad = r.right > vw + 1;
    const leftBad = r.left < -1 && r.width > 0;
    if (!rightBad && !leftBad) continue;
    let a = el.parentElement;
    let scrollable = false;
    while (a) {
      const s = getComputedStyle(a);
      if ((s.overflowX === 'auto' || s.overflowX === 'scroll') &&
          a.scrollWidth > a.clientWidth) { scrollable = true; break; }
      a = a.parentElement;
    }
    if (scrollable) continue;
    let parent = el.parentElement;
    let covered = false;
    while (parent) {
      if (parent.__bad) { covered = true; break; }
      parent = parent.parentElement;
    }
    if (!covered) {
      el.__bad = true;
      bad.push({
        tag: el.tagName.toLowerCase(),
        id: el.id || null,
        cls: (el.className && typeof el.className === 'string')
             ? el.className.slice(0, 80) : null,
        left: Math.round(r.left),
        right: Math.round(r.right),
        vw: vw,
      });
    }
  }
  return JSON.stringify(bad);
})()
"""

# The widest block divs inside the content column, so the margin trim can be
# seen to have landed; plus the column's own width/font/margins.
_TRIM_JS = """\
(() => {
  const sbo = document.getElementById('sbo-rt-content');
  if (!sbo) return JSON.stringify({});
  const s = getComputedStyle(sbo);
  const out = { sboWidth: Math.round(sbo.getBoundingClientRect().width),
               sboFont: s.fontSize, sboMarginL: s.marginLeft };
  const margins = [];
  for (const el of sbo.querySelectorAll('div')) {
    const cs = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    if (r.width < 2) continue;
    margins.push({ m: cs.marginLeft, w: Math.round(r.width),
                   cls: (el.className && typeof el.className === 'string')
                        ? el.className.slice(0, 40) : null });
  }
  margins.sort((a, b) => b.w - a.w);
  out.sample = margins.slice(0, 5);
  return JSON.stringify(out);
})()
"""


def _offenders(ws):
    value = evaluate(ws, _OFFENDERS_JS)
    if value is None:
        return None
    return json.loads(value)


def _trim(ws):
    value = evaluate(ws, _TRIM_JS)
    if value is None:
        return None
    return json.loads(value)


def sweep_page(ws, site, page, width):
    url = "%s/%s%s" % (BASE, site, page)
    cdp(ws, "Page.navigate", {"url": url})
    if not wait_loaded(ws):
        return url, None, [], {}
    overflow = evaluate(
        ws, "document.documentElement.scrollWidth > "
            "document.documentElement.clientWidth + 1")
    if overflow is None:
        return url, None, [], {}
    offenders = _offenders(ws)
    trim = _trim(ws)
    return url, bool(overflow), offenders, trim


def check_cramped(trim, width):
    """Gate the spec's "no cramped text": the column must keep ≥80% of the
    viewport at ≤480px, and the widest content block must show a trimmed
    margin (≤1.5em) rather than the EPUB's 2em indent."""
    if not trim or not trim.get("sboWidth"):
        return False
    if width <= 480 and trim["sboWidth"] < width * 0.8:
        return True
    if not trim.get("sample"):
        return False
    widest_margin = trim["sample"][0]["m"]
    # A margin that big means the trim never landed on the widest block.
    if widest_margin.endswith("em"):
        try:
            return float(widest_margin[:-2]) > 1.5
        except ValueError:
            return False
    return False


def report(url, overflow, offenders, cramped, failed_load):
    name = url.replace(BASE + "/", "")
    if failed_load:
        print("%-64s FAILED-TO-LOAD" % name[:64])
        return 1
    problems = []
    if overflow:
        problems.append("OVERFLOW")
    if offenders:
        problems.append("%d offender(s)" % len(offenders))
    if cramped:
        problems.append("CRAMPED")
    status = ", ".join(problems) if problems else "ok"
    print("%-64s %s" % (name[:64], status))
    for o in offenders:
        print("    + %s#%s .%s left=%d right=%d vw=%d"
              % (o["tag"], o["id"], o["cls"],
                 o["left"], o["right"], o["vw"]))
    return 1 if problems else 0


def sweep_one(ws, site, page, width):
    url, overflow, offenders, trim = sweep_page(ws, site, page, width)
    failed_load = overflow is None
    cramped = check_cramped(trim, width)
    return report(url, overflow, offenders or [], cramped, failed_load)


def main():
    all_pages = "--all" in sys.argv

    with urllib.request.urlopen("http://127.0.0.1:9222/json") as r:
        targets = json.load(r)
    page_target = next(t for t in targets if t["type"] == "page")
    ws = websocket.create_connection(page_target["webSocketDebuggerUrl"],
                                     timeout=20)
    cdp(ws, "Page.enable")
    cdp(ws, "Runtime.enable")

    total = 0
    bad_total = 0
    for width in WIDTHS:
        cdp(ws, "Emulation.setDeviceMetricsOverride",
            {"width": width, "height": 900, "deviceScaleFactor": 1,
             "mobile": True})
        print("\n== %dpx ==" % width)
        for site, page in itertools.product(SITES, PAGES):
            total += 1
            bad_total += sweep_one(ws, site, page, width)

    if all_pages:
        # Full-site pass: every chapter page at 375px, on all three sites.
        chapters = sorted(os.listdir(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs",
            "chapters")))
        cdp(ws, "Emulation.setDeviceMetricsOverride",
            {"width": 375, "height": 900, "deviceScaleFactor": 1,
             "mobile": True})
        print("\n== all chapters @375px (all sites) ==")
        for site, name in itertools.product(SITES, chapters):
            total += 1
            bad_total += sweep_one(ws, site, "chapters/" + name, 375)

    ws.close()
    print("\n%d failing of %d" % (bad_total, total))
    return 1 if bad_total else 0


if __name__ == "__main__":
    sys.exit(main())
