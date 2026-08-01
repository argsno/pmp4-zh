#!/usr/bin/env python3
"""Convert the PMPP 4th-edition EPUB into a browsable static website.

Each chapter becomes a standalone HTML page with a sticky top navigation bar
that lets the reader jump to any chapter/section via a <select> dropdown,
plus Prev / Next / Home buttons.

Running this script rebuilds all three sites in one pass: the English site
first, then the Chinese and bilingual sites, which the i18n renderer derives
from the freshly built English pages and the `translations/` store.  The
dependency runs one way only — this builder imports `build_i18n`, and
`build_i18n` must never import this module.
"""
import os
import re
import shutil
import sys
import html as ihtml
from lxml import html

import build_i18n.cli

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "epub_extract", "OEBPS")
OUT = os.path.join(ROOT, "docs")
XHTML_DIR = os.path.join(SRC, "xhtml")
TRANSLATIONS = os.path.join(ROOT, "translations")

BOOK_TITLE = "Programming Massively Parallel Processors, 4th Edition"


# ---------------------------------------------------------------------------
# 1. Parse the EPUB3 navigation document into groups (optgroups) + flat order
# ---------------------------------------------------------------------------
def parse_nav():
    tree = html.parse(os.path.join(XHTML_DIR, "nav.xhtml"))
    root = tree.getroot()
    toc = root.xpath('//*[@id="toc"]')[0]
    root_ol = toc.xpath('.//ol')[0]

    groups = []          # list of [group_label, [(opt_label, file), ...]]
    flat = []            # ordered list of (label, file) for prev/next
    group_index = {}    # group_label -> position in groups

    def add_option(glabel, olabel, ofile):
        if glabel not in group_index:
            groups.append([glabel, []])
            group_index[glabel] = len(groups) - 1
        groups[group_index[glabel]][1].append((olabel, ofile))

    def is_front(label):
        k = label.lower()
        return any(w in k for w in
                   ("cover", "title", "contents", "copyright", "dedication",
                    "foreword", "preface", "acknowledg"))

    def walk(ol, parent_label=None):
        for li in ol:
            if not (isinstance(li.tag, str) and li.tag == "li"):
                continue
            a = li.xpath('.//a')
            if not a:
                continue
            a = a[0]
            href = a.get("href")
            label = a.text_content().strip()
            # bare file (no fragment) used for chapter/part heading pages
            bare = href.split("#")[0].replace(".xhtml", ".html")
            # full target (with fragment) used for sub-section deep links
            full = href.replace(".xhtml", ".html")
            child_ol = li.xpath('./ol')
            if child_ol:
                grp = label  # group heading page is the first option
                add_option(grp, label, bare)
                flat.append((label, bare))
                walk(child_ol[0], grp)
            else:
                if parent_label is not None:
                    grp = parent_label          # subsection -> nest under parent group
                else:
                    grp = "Front Matter" if is_front(label) else (
                        "Back Matter" if (label.lower().startswith("index")
                                          or "appendix" in label.lower()) else "Sections")
                add_option(grp, label, full)
                flat.append((label, full))

    walk(root_ol)
    return groups, flat


# ---------------------------------------------------------------------------
# 2. Top navigation bar HTML
# ---------------------------------------------------------------------------
def make_header(current, prefix, home_url):
    opts = []
    for glabel, items in groups:
        opts.append('    <optgroup label="%s">'
                    % ihtml.escape(glabel))
        for olabel, ofile in items:
            val = prefix + ofile
            sel = ""
            if current is not None and ofile == current:
                sel = " selected"
            opts.append('      <option value="%s"%s>%s</option>'
                        % (ihtml.escape(val), sel, ihtml.escape(olabel)))
        opts.append('    </optgroup>')
    select = (
        '  <div class="topnav-inner">\n'
        '    <span class="book-title">%s</span>\n' % ihtml.escape(BOOK_TITLE) +
        '    <select id="nav-select" class="nav-select" title="Choose a chapter">\n'
        + "\n".join(opts) + '\n'
        '    </select>\n'
    )

    # Prev / Next (chapter pages only)
    nav_btns = ""
    if current is not None:
        idx = None
        for i, (_, f) in enumerate(flat):
            if f.split("#")[0] == current:
                idx = i
                break
        if idx is not None:
            prev = flat[idx - 1] if idx > 0 else None
            nxt = flat[idx + 1] if idx < len(flat) - 1 else None
            prev_html = ('<a class="navbtn" href="%s%s">&#8249; Prev</a>'
                         % (prefix, prev[1])) if prev else \
                        '<span class="navbtn disabled">&#8249; Prev</span>'
            next_html = ('<a class="navbtn" href="%s%s">Next &#8250;</a>'
                         % (prefix, nxt[1])) if nxt else \
                        '<span class="navbtn disabled">Next &#8250;</span>'
            nav_btns = prev_html + "\n    " + next_html + "\n"

    home = '<a class="navbtn" href="%s">Home</a>' % home_url
    return (
        '<header class="topnav">\n' + select +
        '    <div class="nav-buttons">\n      ' + home +
        (("\n      " + nav_btns) if nav_btns else "") +
        '\n    </div>\n  </div>\n</header>'
    )


# ---------------------------------------------------------------------------
# 3. Static assets for the navigation bar
# ---------------------------------------------------------------------------
TOPNAV_CSS = """\
/* Chinese typesetting, for the zh and bilingual sites.  Imported here rather
   than linked from each page because the i18n renderer never touches <head> —
   the pages it produces ask for exactly the stylesheets the English ones do.
   None of its rules match an English page. */
@import url("chinese.css");

.topnav {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: #1f2a44;
  color: #fff;
  border-bottom: 2px solid #0d1530;
  box-shadow: 0 2px 6px rgba(0,0,0,.25);
  /* Latin faces first, CJK behind them: the English bar renders exactly as it
     did, and the Chinese chapter titles in the other two get a real face. */
  font-family: var(--zh-font);
}
.topnav-inner {
  display: flex;
  align-items: center;
  gap: 14px;
  max-width: 1100px;
  margin: 0 auto;
  padding: 8px 16px;
  flex-wrap: wrap;
}
.book-title {
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
  color: #cdd7f0;
}
.nav-select {
  flex: 1 1 260px;
  min-width: 220px;
  max-width: 520px;
  padding: 6px 10px;
  border-radius: 6px;
  border: 1px solid #3a4a73;
  background: #fff;
  color: #1f2a44;
  font-size: 14px;
}
.nav-buttons {
  display: flex;
  gap: 8px;
}
.navbtn {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 6px;
  background: #3a4a73;
  color: #fff;
  text-decoration: none;
  font-size: 13px;
  white-space: nowrap;
}
.navbtn:hover { background: #4f63a0; }
.navbtn.disabled { background: #2a3350; color: #6b7591; cursor: default; }

/* EN / 中 / 对照 — the same chapter in the other two sites.  The current one
   is a span rather than a link, so it reads as a position, not an offer. */
.langswitch {
  display: flex;
  gap: 4px;
  padding-left: 10px;
  border-left: 1px solid #3a4a73;
}
.langbtn {
  display: inline-block;
  padding: 6px 10px;
  border: 1px solid #3a4a73;
  border-radius: 6px;
  background: #2a3350;
  color: #cdd7f0;
  text-decoration: none;
  font-size: 13px;
  white-space: nowrap;
}
a.langbtn:hover { background: #4f63a0; color: #fff; }
.langbtn.active {
  background: #cdd7f0;
  border-color: #cdd7f0;
  color: #1f2a44;
  font-weight: 600;
  cursor: default;
}

/* ≤640px: the bar reorders into three deliberate rows — row 1 the book title
   beside the language switch, row 2 the full-width chapter selector, row 3
   Home / Prev / Next.  English pages have no language switch, so row 1 holds
   the title alone; the same order rules leave no gap or empty row.  The title
   truncates with an ellipsis whenever its row runs out of room. */
@media (max-width: 640px) {
  .book-title {
    order: 1;
    flex: 1 1 auto;
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .langswitch {
    order: 1;
    flex: 0 0 auto;
    padding-left: 0;
    border-left: none;
  }
  .nav-select {
    order: 2;
    flex: 1 1 100%;
    max-width: 100%;
  }
  .nav-buttons {
    order: 3;
  }
}

/* Content column — the EPUB stylesheet indents every block `div` 2em a side
   (`#sbo-rt-content div`), which compounds across nesting and leaves a 375px
   phone very little reading width.  These media queries halve that indent as
   the viewport narrows.  topnav.css is linked by every page of all three
   sites, so the trim reaches the English pages too, not just the Chinese
   ones. */
@media (max-width: 768px) {
  #book-content #sbo-rt-content div {
    margin-left: 1em;
    margin-right: 1em;
  }
  /* Code blocks scroll inside their own box instead of shoving the whole
     page sideways.  (Tables need no help here: override_v1.css already makes
     them `display: block; overflow: auto`.) */
  #book-content #sbo-rt-content pre {
    overflow-x: auto;
    max-width: 100%;
  }
  /* Long URLs in the reference lists and long inline-code tokens can be
     wider than the phone column; let them wrap instead of pushing the whole
     page sideways.  `overflow-wrap` is inherited, so setting it on the
     content column covers not just `a`, `code` and the EPUB's
     `span.inlinecode` (which resolved to a wider monospace on the Chinese
     site, overflowing its column with long CUDA identifiers) but also bare
     runs of text in plain paragraphs — e.g. the `1/(5%+0.95%)=…` speed-up
     arithmetic in Ch019 overflowed at 375px on the zh site. */
  #book-content #sbo-rt-content {
    overflow-wrap: break-word;
  }
}

/* ≤480px: the title shrinks to 12px type, and every tappable control grows
   to a ~40px touch target.  The chapter select stays a native element; its
   16px type also stops iOS from zooming the page when the picker is
   focused.  The content column narrows with the viewport: block margins drop
   to ~0.6em a side, the base font rises to 17px so Chinese text reads
   comfortably (the book's em/% type sizes scale with it), and the reading
   column widens to ~96% of the viewport, centered.  The body's default 8px
   margin is dropped here so the 96% really is 96% of the phone screen, not
   of the smaller box the margin leaves.  This block must come after the
   ≤768px one so its tighter rules win the cascade at phone widths. */
@media (max-width: 480px) {
  body {
    margin: 0;
  }
  .book-title {
    font-size: 12px;
  }
  .navbtn,
  .langbtn {
    padding: 12px 14px;
    font-size: 14px;
  }
  .nav-select {
    padding: 10px 12px;
    font-size: 16px;
    min-height: 40px;
  }
  #book-content #sbo-rt-content div {
    margin-left: 0.6em;
    margin-right: 0.6em;
  }
  /* The part-title div (`<div id="PN">`) is `width: 100%` in the EPUB
     stylesheet, with default content-box sizing.  Once the block margins
     above shrink the column at ≤480px, that 100% width plus the side
     margins overflows the phone screen (the Part divider pages scrolled
     sideways).  A block div fills its container on its own — `width: auto`
     lets it do that *after* the margins are taken, instead of on top of
     them. */
  #book-content #sbo-rt-content #PN {
    width: auto;
  }
  #book-content #sbo-rt-content {
    font-size: 17px;
    /* The reading column widens to ~96% of the viewport, centered.  The
       same two selectors beat override_v1.css's own ≤768px `width: 90%`
       because topnav.css loads after it. */
    width: 96%;
    margin-left: auto;
    margin-right: auto;
  }
}

/* Landing page */
.landing { max-width: 900px; margin: 32px auto; padding: 0 20px;
  font-family: var(--zh-font);
  color: #1f2a44; }
.landing h1 { font-size: 26px; }
.landing .sub { color: #555; margin-bottom: 24px; }
.landing ul { list-style: none; padding-left: 0; }
.landing li { padding: 2px 0; }
.landing .grp { font-weight: 600; margin-top: 16px; }
.landing a { color: #2a4a9c; text-decoration: none; }
.landing a:hover { text-decoration: underline; }
.landing .subitem { padding-left: 18px; font-size: 14px; color: #444; }
"""

TOPNAV_JS = """\
(function () {
  var sel = document.getElementById('nav-select');
  if (sel) {
    sel.addEventListener('change', function () {
      if (this.value) window.location.href = this.value;
    });
  }
})();
"""


# ---------------------------------------------------------------------------
# 4. Convert each chapter XHTML -> HTML page
# ---------------------------------------------------------------------------
def convert_chapters():
    chapters_dir = os.path.join(OUT, "chapters")
    os.makedirs(chapters_dir, exist_ok=True)
    for fn in sorted(os.listdir(XHTML_DIR)):
        if not fn.endswith(".xhtml"):
            continue
        if fn == "nav.xhtml":   # the EPUB navigation doc itself; not a readable page
            continue
        src_path = os.path.join(XHTML_DIR, fn)
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()

        # rewrite .xhtml references -> .html (keeps #fragments)
        content = content.replace(".xhtml", ".html")

        base = fn[:-6] + ".html"
        header = make_header(base, prefix="", home_url="../index.html")

        # inject viewport meta + nav css + math css into head
        head_inject = (
            '<meta name="viewport" content="width=device-width, initial-scale=1"/>\n'
            '<link rel="stylesheet" href="../topnav.css"/>\n'
            '<link rel="stylesheet" href="../styles/math.css"/>\n'
        )
        content = content.replace("</head>", head_inject + "</head>", 1)

        # insert sticky header right after <body>
        content = re.sub(r"<body[^>]*>", lambda m: m.group(0) + "\n" + header,
                         content, count=1)

        # inject script before </body>
        content = content.replace(
            "</body>",
            '<script src="../topnav.js"></script>\n</body>', 1)

        out_path = os.path.join(chapters_dir, base)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("converted:", base)


# ---------------------------------------------------------------------------
# 5. Landing page (index.html)
# ---------------------------------------------------------------------------
def build_index():
    header = make_header(None, prefix="chapters/", home_url="index.html")
    toc_html = ['<div class="landing">',
                '<h1>%s</h1>' % ihtml.escape(BOOK_TITLE),
                '<p class="sub">Wen-mei W. Hwu, David B. Kirk, Izzat El Hajj &mdash; '
                'A Hands-on Approach (4th Edition)</p>',
                '<p>Use the dropdown in the top navigation bar to jump to any '
                'chapter or section. Browse the full table of contents below.</p>']
    for glabel, items in groups:
        toc_html.append('<div class="grp">%s</div>' % ihtml.escape(glabel))
        toc_html.append('<ul>')
        for olabel, ofile in items:
            toc_html.append(
                '<li class="subitem"><a href="chapters/%s">%s</a></li>'
                % (ihtml.escape(ofile), ihtml.escape(olabel)))
        toc_html.append('</ul>')
    toc_html.append('</div>')

    page = (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        '<meta charset="utf-8"/>\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1"/>\n'
        '<title>%s</title>\n' % ihtml.escape(BOOK_TITLE) +
        '<link rel="stylesheet" href="topnav.css"/>\n'
        '</head>\n<body>\n' + header + "\n" + "\n".join(toc_html) +
        '\n<script src="topnav.js"></script>\n</body>\n</html>\n'
    )
    with open(os.path.join(OUT, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    print("built: index.html")


# ---------------------------------------------------------------------------
# 6. Copy shared assets
# ---------------------------------------------------------------------------
def copy_assets():
    # override_v1.css sits at OEBPS root
    shutil.copy2(os.path.join(SRC, "override_v1.css"),
                 os.path.join(OUT, "override_v1.css"))
    # styles/ and images/
    for d in ("styles", "images"):
        src = os.path.join(SRC, d)
        dst = os.path.join(OUT, d)
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    print("copied: override_v1.css, styles/, images/")


# ---------------------------------------------------------------------------
def main():
    """Rebuild the English site, then the zh and bilingual sites from it.

    Returns the i18n renderer's exit status: 0 when every page passed, 1 when
    one or more pages were reported and skipped, 2 when the translation store
    itself is broken.  A skipped page is a problem someone will fix; the build
    command must not pretend the three sites are complete.
    """
    global groups, flat
    groups, flat = parse_nav()
    os.makedirs(OUT, exist_ok=True)
    copy_assets()
    convert_chapters()
    build_index()
    with open(os.path.join(OUT, "topnav.css"), "w", encoding="utf-8") as f:
        f.write(TOPNAV_CSS)
    with open(os.path.join(OUT, "topnav.js"), "w", encoding="utf-8") as f:
        f.write(TOPNAV_JS)

    status = build_i18n.cli.main(
        ["render", "--web", OUT, "--translations", TRANSLATIONS])
    if status == 0:
        print("DONE. Open docs/index.html in a browser.")
    elif status == 2:
        print("docs/zh and docs/bilingual: the translation store is unusable "
              "(see above).", file=sys.stderr)
    else:
        print("docs/zh and docs/bilingual: some pages were skipped (see above).",
              file=sys.stderr)
    return status


if __name__ == "__main__":
    sys.exit(main())
