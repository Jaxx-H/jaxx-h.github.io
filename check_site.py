#!/usr/bin/env python3
"""
check_site.py — the INDEPENDENT post-build oracle. Stdlib only.

Shares ZERO rendering code with build.py (the builder never grades itself).
It re-derives expectations from config.json + dist/ alone and fails on any
contract violation build.py might have let through via a regression.

  python3 check_site.py         # deep-check the local dist/ build
  python3 check_site.py --live  # additionally fetch the LIVE sitemap and
                                # assert every listed URL returns 200 (cap 50)

Exits non-zero on any failure so CI blocks a broken deploy.
"""
import json
import sys
import re
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
TITLE_RE = re.compile(r"<title>([^<]*)</title>")
JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
RUN_ID_RE = re.compile(r"\b[A-Za-z0-9]{15,20}\b")  # Apify run ids are ~17-char alphanumerics

errors = []


def err(m):
    errors.append(m)


class PageShape(HTMLParser):
    """Track document order of the answer <p>, first <table>, and count table rows."""
    def __init__(self):
        super().__init__()
        self.events = []          # ordered tags of interest
        self.tbody_rows = 0
        self._in_tbody = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "p" and a.get("class") == "answer":
            self.events.append("answer_p")
        elif tag == "table":
            self.events.append("table")
        elif tag == "tbody":
            self._in_tbody = True
        elif tag == "tr" and self._in_tbody:
            self.tbody_rows += 1

    def handle_endtag(self, tag):
        if tag == "tbody":
            self._in_tbody = False


def site_base():
    cfg = json.loads((ROOT / "config.json").read_text())
    cname = (cfg.get("cname") or "").strip()
    return (f"https://{cname}" if cname else cfg["site_url"]).rstrip("/")


def check_local():
    if not DIST.exists():
        err("dist/ does not exist — run build.py first")
        return

    base = site_base()
    required = ["index.html", "sitemap.xml", "robots.txt", "feed.xml",
                "llms.txt", "404.html", ".nojekyll", "static/style.css"]
    for r in required:
        if not (DIST / r).exists():
            err(f"missing required output: {r}")

    page_dirs = sorted(d for d in DIST.iterdir() if d.is_dir() and d.name != "static")

    # --- sitemap parses as XML; URL count == page dirs + homepage; URLs match dirs
    try:
        tree = ET.parse(DIST / "sitemap.xml")
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text for el in tree.getroot().findall("sm:url/sm:loc", ns)]
        if len(locs) != len(page_dirs) + 1:
            err(f"sitemap has {len(locs)} URLs, expected {len(page_dirs) + 1} (pages + homepage)")
        expected = {base + "/"} | {f"{base}/{d.name}/" for d in page_dirs}
        for loc in locs:
            if loc not in expected:
                err(f"sitemap lists unexpected URL {loc}")
        for e in expected - set(locs):
            err(f"sitemap missing URL {e}")
    except ET.ParseError as e:
        err(f"sitemap.xml does not parse as XML: {e}")
        locs = []

    # --- feed.xml parses as XML
    try:
        ET.parse(DIST / "feed.xml")
    except ET.ParseError as e:
        err(f"feed.xml does not parse as XML: {e}")

    # --- robots.txt: has Sitemap line, has NO Disallow
    robots = (DIST / "robots.txt").read_text() if (DIST / "robots.txt").exists() else ""
    if "Sitemap:" not in robots:
        err("robots.txt missing Sitemap: line")
    if "Disallow" in robots:
        err("robots.txt contains a Disallow line (AI crawlers must stay welcome)")

    # --- per-page deep checks + title uniqueness across dist
    titles = {}
    for d in page_dirs:
        idx = d / "index.html"
        if not idx.exists():
            err(f"page {d.name} has no index.html")
            continue
        h = idx.read_text()

        # canonical EQUALS the page URL exactly
        m = CANONICAL_RE.search(h)
        want = f"{base}/{d.name}/"
        if not m:
            err(f"page {d.name} missing canonical link")
        elif m.group(1) != want:
            err(f"page {d.name} canonical is {m.group(1)!r}, expected {want!r}")

        # every JSON-LD block must json.loads
        blocks = JSONLD_RE.findall(h)
        if not blocks:
            err(f"page {d.name} has no JSON-LD block")
        for i, b in enumerate(blocks):
            try:
                json.loads(b)
            except json.JSONDecodeError as e:
                err(f"page {d.name} JSON-LD block {i + 1} does not parse: {e}")

        # answer-first <p> before first <table>; >=10 tbody rows
        shape = PageShape()
        shape.feed(h)
        if "answer_p" not in shape.events or "table" not in shape.events:
            err(f"page {d.name} missing answer paragraph or data table")
        elif shape.events.index("answer_p") > shape.events.index("table"):
            err(f"page {d.name}: data table appears before the answer paragraph")
        if shape.tbody_rows < 10:
            err(f"page {d.name} table has {shape.tbody_rows} body rows, need >=10")

        # provenance carries a run-id-shaped token
        if "Data from run" not in h or not RUN_ID_RE.search(h.split("Data from run", 1)[-1][:60]):
            err(f"page {d.name} provenance line missing a run-id-shaped token")

        # title present + unique
        t = TITLE_RE.search(h)
        if not t or not t.group(1).strip():
            err(f"page {d.name} missing <title>")
        else:
            if t.group(1) in titles:
                err(f"duplicate <title> between {titles[t.group(1)]} and {d.name}")
            titles[t.group(1)] = d.name

    # homepage title counts toward uniqueness too
    home = (DIST / "index.html").read_text() if (DIST / "index.html").exists() else ""
    t = TITLE_RE.search(home)
    if t and t.group(1) in titles:
        err(f"homepage <title> duplicates page {titles[t.group(1)]}")

    # --- email scan over ALL html (belt and braces)
    for html_file in DIST.rglob("*.html"):
        m = EMAIL_RE.search(html_file.read_text())
        if m:
            err(f"{html_file.relative_to(DIST)} contains email-like string {m.group(0)!r}")

    print(f"local: deep-checked {len(page_dirs)} page(s) + sitemap/feed/robots/titles")


def fetch_code(u):
    req = urllib.request.Request(u, headers={"User-Agent": "check_site/2.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.getcode(), resp.read()


def check_live():
    base = site_base()
    # fetch the LIVE sitemap and assert every listed URL is 200 (cap 50)
    try:
        code, body = fetch_code(base + "/sitemap.xml")
        if code != 200:
            err(f"live sitemap returned {code}")
            return
        root = ET.fromstring(body)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text for el in root.findall("sm:url/sm:loc", ns)][:50]
    except Exception as e:
        err(f"live sitemap fetch/parse failed: {e}")
        return
    for u in locs + [base + "/robots.txt"]:
        try:
            code, _ = fetch_code(u)
            if code != 200:
                err(f"live {u} returned {code}")
            else:
                print(f"live: {u} -> 200")
        except Exception as e:
            err(f"live {u} failed: {e}")


def main():
    check_local()
    if "--live" in sys.argv:
        check_live()
    if errors:
        print("\nVALIDATION FAILED:", file=sys.stderr)
        for e in errors:
            print("  - " + e, file=sys.stderr)
        sys.exit(1)
    print("OK: all checks passed")


if __name__ == "__main__":
    main()
