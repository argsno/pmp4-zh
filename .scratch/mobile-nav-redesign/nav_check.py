#!/usr/bin/env python3
"""Mobile nav behaviour check at 375px — the gates tickets 01/02/03 care about,
which the ticket-04 layout sweep does not cover.

sweep.py answers "does anything overflow / is the column cramped".  This
answers "does the navigation behave the way the redesign specified":

  1. Top bar scrolls away.  At <=640px `.topnav` is `position: static`, so
     after scrolling down its top edge must move up with the content and end
     up off-screen.  (Ticket 01 removed the translateY auto-hide; ticket 02
     unpinned the bar.  Both show up here as "the bar's rect moves".)
  2. Bottom pager is fixed.  It must be display:flex, position:fixed, and its
     rect must NOT move when the page scrolls.  Chapter pages only.
  3. Prev/Next disabled ends.  The first page has no Prev link, the last no
     Next; those render as non-link `.navbtn.disabled`.
  4. The landing page has no bottom pager at all.
  5. The chapter dropdown still jumps: dispatching `change` on #nav-select
     must navigate to the selected chapter.
  6. The last line of content clears the fixed bar (nothing behind it).

Run against a local preview (`python3 -m http.server 8833` in docs/) with a
headless Chrome on :9222 launched with --remote-allow-origins=*:

    python3 nav_check.py                    # local, all three sites
    python3 nav_check.py --base https://argsno.github.io/pmp4-zh
"""
import json
import sys
import time
import urllib.request

import websocket

BASE = "http://localhost:8833"
SITES = ["", "zh/", "bilingual/"]

# First chapter (Prev disabled), a middle chapter, and the last flat page
# (Next disabled) — the three shapes the pager can take.  Cover is the first
# entry of the nav, Index the last, but Index has no zh twin, so the
# last-page case is checked on the English site only.
FIRST_PAGE = "chapters/Cover.html"
MID_PAGE = "chapters/Ch001_1-19_B9780323912310000069.html"
LAST_PAGE_EN = "chapters/Index_537-551_B978032391231000032X.html"


def cdp(ws, method, params=None):
    mid = int(time.time() * 1000000) % 2**31
    ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
    while True:
        msg = json.loads(ws.recv())
        if msg.get("id") == mid:
            return msg


def evaluate(ws, expression):
    res = cdp(ws, "Runtime.evaluate",
              {"expression": expression, "returnByValue": True,
               "awaitPromise": True})
    if "exceptionDetails" in res.get("result", {}):
        return None
    return res["result"]["result"].get("value")


def wait_loaded(ws, timeout=60.0):
    """Poll readyState rather than sleeping a fixed amount: the live site's
    big chapters (Ch016 is 194KB) can take tens of seconds, and measuring
    before layout finishes turns a real failure into a false pass."""
    expr = ("document.readyState === 'complete' && "
            "(document.getElementById('sbo-rt-content') !== null || "
            " !document.getElementById('book-content'))")
    deadline = time.time() + timeout
    while time.time() < deadline:
        if evaluate(ws, expr):
            time.sleep(0.3)
            return True
        time.sleep(0.2)
    return False


def goto(ws, url):
    cdp(ws, "Page.navigate", {"url": url})
    return wait_loaded(ws)


# Measure the top bar and the pager before and after a scroll.  The bar is
# static so its rect must travel with the page; the pager is fixed so its
# rect must not move at all.
_SCROLL_JS = """\
(() => {
  const rect = el => {
    if (!el) return null;
    const r = el.getBoundingClientRect();
    return { top: Math.round(r.top), bottom: Math.round(r.bottom),
             h: Math.round(r.height) };
  };
  const nav = document.querySelector('.topnav');
  const pager = document.querySelector('.bottom-pager');
  const navCS = nav ? getComputedStyle(nav) : null;
  const pagerCS = pager ? getComputedStyle(pager) : null;
  const before = { nav: rect(nav), pager: rect(pager) };
  const scrollable =
    document.documentElement.scrollHeight > window.innerHeight + 1;
  window.scrollTo(0, Math.max(600, document.body.scrollHeight / 2));
  const after = { nav: rect(nav), pager: rect(pager) };
  const vh = window.innerHeight;
  return JSON.stringify({
    scrollable: scrollable,
    scrollY: Math.round(window.scrollY),
    navPosition: navCS ? navCS.position : null,
    navTransform: navCS ? navCS.transform : null,
    navHidden: nav ? nav.classList.contains('nav-hidden') : null,
    pagerExists: !!pager,
    pagerDisplay: pagerCS ? pagerCS.display : null,
    pagerPosition: pagerCS ? pagerCS.position : null,
    before: before, after: after, vh: vh,
    prevDisabled: !!document.querySelector(
      '.bottom-pager .navbtn.disabled:first-child'),
    nextDisabled: !!document.querySelector(
      '.bottom-pager .navbtn.disabled:last-child'),
    pagerBtns: [...document.querySelectorAll('.bottom-pager .navbtn')]
      .map(b => ({ tag: b.tagName.toLowerCase(),
                   disabled: b.classList.contains('disabled'),
                   text: b.textContent.trim().slice(0, 20),
                   href: b.getAttribute('href'),
                   h: Math.round(b.getBoundingClientRect().height) })),
  });
})()
"""

# Does the fixed bar cover the end of the text?  Scroll to the bottom and
# compare the content column's last painted edge against the bar's top.
_CLEARANCE_JS = """\
(() => {
  const sbo = document.getElementById('sbo-rt-content');
  const pager = document.querySelector('.bottom-pager');
  if (!sbo || !pager) return JSON.stringify({ n: true });
  window.scrollTo(0, document.body.scrollHeight);
  const s = sbo.getBoundingClientRect();
  const p = pager.getBoundingClientRect();
  return JSON.stringify({
    n: false,
    contentBottom: Math.round(s.bottom),
    pagerTop: Math.round(p.top),
    padBottom: getComputedStyle(sbo).paddingBottom,
  });
})()
"""


def check_page(ws, base, site, page, expect_pager=True,
               expect_prev_disabled=None, expect_next_disabled=None):
    url = "%s/%s%s" % (base, site, page)
    name = ("%s%s" % (site, page))[:58]
    if not goto(ws, url):
        print("%-58s FAILED-TO-LOAD" % name)
        return 1
    raw = evaluate(ws, _SCROLL_JS)
    if raw is None:
        print("%-58s EVAL-FAILED" % name)
        return 1
    d = json.loads(raw)
    problems = []

    # 1. the bar is unpinned and actually leaves the screen
    if d["navPosition"] != "static":
        problems.append("topnav position=%s (want static)" % d["navPosition"])
    if d["navTransform"] not in (None, "none"):
        problems.append("topnav transform=%s" % d["navTransform"])
    if d["navHidden"]:
        problems.append("topnav still uses .nav-hidden")
    # Only pages taller than the viewport can demonstrate the scroll-away.  A
    # short page (Cover is 656px at 375px) has nothing to scroll, so demanding
    # movement there would fail a page that is in fact correct — `static`
    # positioning, checked above, is the real gate.
    if d["scrollable"] and d["before"]["nav"] and d["after"]["nav"]:
        moved = d["before"]["nav"]["top"] - d["after"]["nav"]["top"]
        if moved <= 0:
            problems.append("topnav did not scroll away (moved %dpx)" % moved)
        elif d["after"]["nav"]["bottom"] > 0:
            problems.append("topnav still on screen after scroll (bottom=%d)"
                            % d["after"]["nav"]["bottom"])

    # 2. the pager: present or absent as the page type demands, and fixed
    if expect_pager:
        if not d["pagerExists"]:
            problems.append("no bottom pager")
        else:
            if d["pagerDisplay"] == "none":
                problems.append("pager display:none at 375px")
            if d["pagerPosition"] != "fixed":
                problems.append("pager position=%s (want fixed)"
                                % d["pagerPosition"])
            b, a = d["before"]["pager"], d["after"]["pager"]
            if b and a and (b["top"] != a["top"]):
                problems.append("pager moved on scroll (%d -> %d)"
                                % (b["top"], a["top"]))
            if a and abs(a["bottom"] - d["vh"]) > 2:
                problems.append("pager not at viewport bottom (%d vs %d)"
                                % (a["bottom"], d["vh"]))
            btns = d["pagerBtns"]
            if len(btns) != 2:
                problems.append("pager has %d buttons (want 2)" % len(btns))
            for btn in btns:
                if btn["h"] < 40:
                    problems.append("pager button %r only %dpx tall"
                                    % (btn["text"], btn["h"]))
                if btn["disabled"] and btn["tag"] != "span":
                    problems.append("disabled button is a <%s>" % btn["tag"])
                if not btn["disabled"] and not btn["href"]:
                    problems.append("enabled button %r has no href"
                                    % btn["text"])
    elif d["pagerExists"] and d["pagerDisplay"] != "none":
        problems.append("landing page shows a bottom pager")

    if expect_prev_disabled is not None:
        if d["prevDisabled"] != expect_prev_disabled:
            problems.append("prevDisabled=%s (want %s)"
                            % (d["prevDisabled"], expect_prev_disabled))
    if expect_next_disabled is not None:
        if d["nextDisabled"] != expect_next_disabled:
            problems.append("nextDisabled=%s (want %s)"
                            % (d["nextDisabled"], expect_next_disabled))

    # 3. content clears the fixed bar
    if expect_pager:
        craw = evaluate(ws, _CLEARANCE_JS)
        if craw:
            c = json.loads(craw)
            if not c.get("n"):
                if c["contentBottom"] > c["pagerTop"] + 1:
                    problems.append(
                        "content runs under the pager (content %d > pager %d)"
                        % (c["contentBottom"], c["pagerTop"]))
                if c["padBottom"] == "0px":
                    problems.append("content column has no bottom padding")

    print("%-58s %s" % (name, ", ".join(problems) if problems else "ok"))
    return 1 if problems else 0


def check_dropdown(ws, base, site):
    """The chapter selector must still navigate (ticket 01 kept exactly this
    one handler when it deleted the auto-hide JS)."""
    url = "%s/%s%s" % (base, site, MID_PAGE)
    name = "%s[dropdown]" % site
    if not goto(ws, url):
        print("%-58s FAILED-TO-LOAD" % name[:58])
        return 1
    target = evaluate(ws, """\
(() => {
  const sel = document.getElementById('nav-select');
  if (!sel) return '';
  const opt = [...sel.options].find(
    o => o.value && !o.disabled && o.value !== sel.value);
  if (!opt) return '';
  sel.value = opt.value;
  sel.dispatchEvent(new Event('change'));
  return opt.value;
})()
""")
    if not target:
        print("%-58s no usable option in #nav-select" % name[:58])
        return 1
    deadline = time.time() + 15
    while time.time() < deadline:
        here = evaluate(ws, "location.href")
        if here and here.rsplit("/", 1)[-1] == target.rsplit("/", 1)[-1]:
            print("%-58s ok (-> %s)" % (name[:58], target[:28]))
            return 0
        time.sleep(0.2)
    print("%-58s dropdown did not navigate (wanted %s)" % (name[:58], target))
    return 1


def main():
    base = BASE
    if "--base" in sys.argv:
        base = sys.argv[sys.argv.index("--base") + 1].rstrip("/")

    with urllib.request.urlopen("http://127.0.0.1:9222/json") as r:
        targets = json.load(r)
    page_target = next(t for t in targets if t["type"] == "page")
    ws = websocket.create_connection(page_target["webSocketDebuggerUrl"],
                                     timeout=90)
    cdp(ws, "Page.enable")
    cdp(ws, "Runtime.enable")
    cdp(ws, "Emulation.setDeviceMetricsOverride",
        {"width": 375, "height": 812, "deviceScaleFactor": 2, "mobile": True})

    print("== %s @375px ==" % base)
    bad = total = 0
    for site in SITES:
        for page, prev_dis, next_dis in (
                (FIRST_PAGE, True, False),
                (MID_PAGE, False, False)):
            total += 1
            bad += check_page(ws, base, site, page,
                              expect_pager=True,
                              expect_prev_disabled=prev_dis,
                              expect_next_disabled=next_dis)
        total += 1
        bad += check_page(ws, base, site, "index.html", expect_pager=False)
        total += 1
        bad += check_dropdown(ws, base, site)

    # Last flat page: Next must be disabled.  English only — the renderer
    # skips Index, so zh/bilingual have no counterpart to check.
    total += 1
    bad += check_page(ws, base, "", LAST_PAGE_EN, expect_pager=True,
                      expect_prev_disabled=False, expect_next_disabled=True)

    ws.close()
    print("\n%d failing of %d" % (bad, total))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
