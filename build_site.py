#!/usr/bin/env python3
"""Convert the PMPP 4th-edition EPUB into a browsable static website.

Each chapter becomes a standalone HTML page with a sticky top navigation bar
that lets the reader jump to any chapter/section via a <select> dropdown,
plus Prev / Next / Home buttons.
"""
import os
import re
import shutil
import html as ihtml
from lxml import html

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "epub_extract", "OEBPS")
OUT = os.path.join(ROOT, "web")
XHTML_DIR = os.path.join(SRC, "xhtml")

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

        # inject nav css + math css into head
        head_inject = (
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
if __name__ == "__main__":
    groups, flat = parse_nav()
    os.makedirs(OUT, exist_ok=True)
    copy_assets()
    convert_chapters()
    build_index()
    with open(os.path.join(OUT, "topnav.css"), "w", encoding="utf-8") as f:
        f.write(TOPNAV_CSS)
    with open(os.path.join(OUT, "topnav.js"), "w", encoding="utf-8") as f:
        f.write(TOPNAV_JS)
    print("DONE. Open web/index.html in a browser.")
