#!/usr/bin/env python3
"""
check_site.py — the INDEPENDENT post-build oracle. Stdlib only.

Shares ZERO rendering code with build.py (the builder never grades itself).
It re-derives expectations from config.json + dist/ alone and fails on any
contract violation build.py might have let through via a regression.

  python3 check_site.py                  # deep-check the local dist/ build
  python3 check_site.py --live           # additionally fetch the LIVE sitemap and
                                         # assert every listed URL returns 200 (cap 50)
  python3 check_site.py --stale-selftest # prove the stale-page policy end-to-end
                                         # against a synthetic build in a temp dir

Exits non-zero on any failure so CI blocks a broken deploy.
"""
import json
import sys
import re
import shutil
import subprocess
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
CANONICAL_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
TITLE_RE = re.compile(r"<title>([^<]*)</title>")
JSONLD_RE = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
RUN_ID_RE = re.compile(r"\b[A-Za-z0-9]{15,20}\b")  # Apify run ids are ~17-char alphanumerics
# Stale-page policy oracle: independent mirror of build.py's ceiling constant.
# config.json "stale_after_days" may LOWER it, never raise it; missing/invalid
# values fail closed to it.
STALE_AFTER_DAYS = 45
NOINDEX_META = '<meta name="robots" content="noindex">'

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


def stale_threshold(cfg):
    """Effective staleness threshold in days, re-derived independently of
    build.py: missing/invalid config -> STALE_AFTER_DAYS (fail closed); a valid
    value is clamped to the ceiling (config may lower it, never raise it)."""
    v = cfg.get("stale_after_days")
    if isinstance(v, bool) or not isinstance(v, int) or v < 1:
        return STALE_AFTER_DAYS
    return min(v, STALE_AFTER_DAYS)


def page_fetch_date(html_str):
    """The page's fetch date (YYYY-MM-DD) as declared in its Dataset JSON-LD
    dateModified — the only provenance dist/ itself carries. None if absent."""
    for b in JSONLD_RE.findall(html_str):
        try:
            obj = json.loads(b)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("@type") == "Dataset":
            return str(obj.get("dateModified", ""))[:10]
    return None


def page_is_simple(html_str):
    """True when the page declares WebPage JSON-LD and no Dataset block — the
    marker build.py stamps on page_type: "simple" pages (policies, landing
    pages). A page carrying BOTH types counts as a data page (fail closed)."""
    has_webpage = False
    for b in JSONLD_RE.findall(html_str):
        try:
            obj = json.loads(b)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            if obj.get("@type") == "Dataset":
                return False
            if obj.get("@type") == "WebPage":
                has_webpage = True
    return has_webpage


def stale_findings(dist_dir, base, threshold):
    """Stale-policy oracle over a built dist/. Returns (stale_slugs, violations).

    A page whose fetch date is more than `threshold` days before the check-time
    UTC date is STALE: it must carry the robots noindex meta and be absent from
    sitemap.xml and feed.xml. A fresh page must carry NO noindex meta and be
    present in the sitemap. Pure function so --stale-selftest can aim it at a
    scratch build (and at deliberately tampered ones)."""
    today = datetime.now(timezone.utc).date()
    stale, violations = set(), []
    try:
        tree = ET.parse(dist_dir / "sitemap.xml")
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = {el.text for el in tree.getroot().findall("sm:url/sm:loc", ns)}
    except (OSError, ET.ParseError) as e:
        violations.append(f"stale policy: cannot read sitemap.xml: {e}")
        locs = set()
    feed_path = dist_dir / "feed.xml"
    feed = feed_path.read_text() if feed_path.exists() else ""
    for d in sorted(p for p in dist_dir.iterdir()
                    if p.is_dir() and p.name not in ("static", "tools", "hq", "state")):
        idx = d / "index.html"
        if not idx.exists():
            continue  # check_local reports the missing index.html itself
        h = idx.read_text()
        url = f"{base}/{d.name}/"
        if page_is_simple(h):
            # simple pages never go stale: always indexable, always in the
            # sitemap, never in the feed
            if NOINDEX_META in h:
                violations.append(f"simple page {d.name} must not carry a noindex meta")
            if url not in locs:
                violations.append(f"simple page {d.name} missing from sitemap.xml")
            if url in feed:
                violations.append(f"simple page {d.name} must not be listed in feed.xml")
            continue
        try:
            fetched = datetime.strptime(page_fetch_date(h) or "", "%Y-%m-%d").date()
        except ValueError:
            violations.append(f"page {d.name}: no parseable fetch date in Dataset "
                              f"JSON-LD — cannot grade staleness (fail closed)")
            continue
        if (today - fetched).days > threshold:
            stale.add(d.name)
            if NOINDEX_META not in h:
                violations.append(f"stale page {d.name} is missing {NOINDEX_META}")
            if url in locs:
                violations.append(f"stale page {d.name} must not be listed in sitemap.xml")
            if url in feed:
                violations.append(f"stale page {d.name} must not be listed in feed.xml")
        else:
            if NOINDEX_META in h:
                violations.append(f"fresh page {d.name} must not carry a noindex meta")
            if url not in locs:
                violations.append(f"fresh page {d.name} missing from sitemap.xml")
    return stale, violations


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

    page_dirs = sorted(d for d in DIST.iterdir()
                       if d.is_dir() and d.name not in ("static", "tools", "hq", "state"))

    # --- stale policy: stale pages must be noindexed + out of sitemap/feed,
    # fresh pages must be indexable + in the sitemap
    cfg = json.loads((ROOT / "config.json").read_text())
    stale_slugs, stale_errs = stale_findings(DIST, base, stale_threshold(cfg))
    for m in stale_errs:
        err(m)

    # --- sitemap parses as XML; URL count == FRESH page dirs + homepage; URLs match
    fresh_dirs = [d for d in page_dirs if d.name not in stale_slugs]
    try:
        tree = ET.parse(DIST / "sitemap.xml")
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locs = [el.text for el in tree.getroot().findall("sm:url/sm:loc", ns)]
        if len(locs) != len(fresh_dirs) + 1:
            err(f"sitemap has {len(locs)} URLs, expected {len(fresh_dirs) + 1} (fresh pages + homepage)")
        expected = {base + "/"} | {f"{base}/{d.name}/" for d in fresh_dirs}
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

        if page_is_simple(h):
            # simple pages: prose shape only — an <h1> and at least one <p>
            if "<h1>" not in h:
                err(f"simple page {d.name} missing <h1>")
            if "<p" not in h:
                err(f"simple page {d.name} has no paragraph content")
        else:
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

    n_tools = check_tools(base)

    print(f"local: deep-checked {len(page_dirs)} page(s) "
          f"({len(stale_slugs)} stale) + {n_tools} tool page(s) "
          f"+ sitemap/feed/robots/titles + stale policy")


# resource-loading attributes a tool page may not point off-site (anchors/links
# in prose are fine — these are the tags that make the browser fetch something)
TOOL_RESOURCE_RE = re.compile(
    r'<(?:script|img|iframe|video|audio|source|embed)[^>]*\ssrc="([^"]*)"'
    r'|<link[^>]*\shref="([^"]*)"', re.I)


def check_tools(base):
    """Oracle for hand-authored /tools/<slug>/ pages (client-side tools that
    bypass the content contract). Each must have a non-empty <title>, an exact
    canonical URL, and — the tools' core promise — load NO external resource
    beyond the site's own configured analytics snippet. Deep-dir dirs without
    an index.html fail. Returns the number of tool pages checked."""
    tools_dir = DIST / "tools"
    if not tools_dir.exists():
        return 0
    cfg = json.loads((ROOT / "config.json").read_text())
    allowed = set(re.findall(r'src="([^"]+)"', cfg.get("analytics_snippet", "")))
    n = 0
    for d in sorted(p for p in tools_dir.iterdir() if p.is_dir()):
        idx = d / "index.html"
        if not idx.exists():
            err(f"tool {d.name} has no index.html")
            continue
        n += 1
        h = idx.read_text()
        t = TITLE_RE.search(h)
        if not t or not t.group(1).strip():
            err(f"tool {d.name} missing <title>")
        m = CANONICAL_RE.search(h)
        want = f"{base}/tools/{d.name}/"
        if not m:
            err(f"tool {d.name} missing canonical link")
        elif m.group(1) != want:
            err(f"tool {d.name} canonical is {m.group(1)!r}, expected {want!r}")
        for rm in TOOL_RESOURCE_RE.finditer(h):
            u = rm.group(1) or rm.group(2)
            if not u:
                continue
            external = u.startswith(("http://", "https://", "//"))
            if external and u not in allowed and not u.startswith(base):
                err(f"tool {d.name} loads external resource {u!r} "
                    f"(tools must be self-contained; only the site analytics snippet is allowed)")
    return n


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


def _fixture_page(slug, run_id, fetched_at):
    """A contract-satisfying, OBVIOUSLY-synthetic page for --stale-selftest.
    Written only into the self-test's temp dir — never into content/pages/."""
    filler = ("Synthetic filler sentence number %d written only so this fixture "
              "clears the 120 word prose floor of the page contract.")
    return {
        "slug": slug,
        "title": f"Stale-policy self-test fixture: {slug}",
        "description": f"Synthetic self-test fixture {slug}. Never deployed; exists only in a temp dir.",
        "answer_first": " ".join(filler % i for i in (1, 2, 3)),
        "data_source": {"actor": "selftest/fixture-actor", "run_id": run_id,
                        "fetched_at": fetched_at},
        "columns": ["fixture row", "count"],
        "rows": [[f"fixture-row-{i:02d}", str(i)] for i in range(10)],
        "facts": [filler % i for i in (4, 5, 6)],
        "faq": [{"q": f"Is this fixture data real? ({slug})", "a": filler % 7},
                {"q": f"Why does this page exist? ({slug})", "a": filler % 8}],
        "related_product": {"name": "Self-test fixture",
                            "url": "https://apify.com/chilly_damask/selftest-fixture"},
        "citations": [],
    }


def stale_selftest():
    """Prove the stale-page policy end-to-end in a throwaway copy of the site.

    Builds a scratch site (temp dir; the real content/pages/ is never touched)
    holding one synthetic STALE page (fetched_at 2020-01-01) and one synthetic
    FRESH page (fetched today), then asserts all four policy outcomes:
      1. the stale page's HTML carries the robots noindex meta,
      2. the stale page is absent from sitemap.xml,
      3. the fresh page's HTML carries NO noindex meta,
      4. the fresh page is present in sitemap.xml,
    plus: the oracle (stale_findings) agrees with the correct build, and —
    negative tests — still catches a stripped noindex meta and a stale URL
    injected back into the sitemap."""
    today = datetime.now(timezone.utc).date().isoformat()
    cfg = json.loads((ROOT / "config.json").read_text())
    base = site_base()
    with tempfile.TemporaryDirectory(prefix="stale-selftest-") as td:
        site = Path(td) / "site"
        (site / "content" / "pages").mkdir(parents=True)
        shutil.copy2(ROOT / "build.py", site / "build.py")
        shutil.copytree(ROOT / "templates", site / "templates")
        shutil.copytree(ROOT / "static", site / "static")
        shutil.copy2(ROOT / "config.json", site / "config.json")
        for slug, run_id, fetched in (("stale-fixture", "SELFTESTRUNSTALE1", "2020-01-01"),
                                      ("fresh-fixture", "SELFTESTRUNFRESH1", today)):
            (site / "content" / "pages" / f"{slug}.json").write_text(
                json.dumps(_fixture_page(slug, run_id, fetched), indent=1))
        r = subprocess.run([sys.executable, "build.py"], cwd=site,
                           capture_output=True, text=True)
        if r.returncode != 0:
            err(f"selftest: scratch build failed:\n{r.stderr.strip()}")
            return
        dist = site / "dist"
        stale_html = (dist / "stale-fixture" / "index.html").read_text()
        fresh_html = (dist / "fresh-fixture" / "index.html").read_text()
        sitemap = (dist / "sitemap.xml").read_text()

        # the four policy assertions
        if NOINDEX_META not in stale_html:
            err("selftest: stale page lacks the noindex meta")
        if f"{base}/stale-fixture/" in sitemap:
            err("selftest: stale page is listed in sitemap.xml")
        if NOINDEX_META in fresh_html:
            err("selftest: fresh page carries a noindex meta")
        if f"{base}/fresh-fixture/" not in sitemap:
            err("selftest: fresh page missing from sitemap.xml")
        if "data refreshing" not in (dist / "index.html").read_text():
            err("selftest: homepage does not mark the stale page as data refreshing")

        # the oracle agrees with a correct build...
        threshold = stale_threshold(cfg)
        stale, v = stale_findings(dist, base, threshold)
        if stale != {"stale-fixture"} or v:
            err(f"selftest: oracle disagrees with a correct build: stale={sorted(stale)} violations={v}")

        # ...and catches each tampered regression (negative tests)
        (dist / "stale-fixture" / "index.html").write_text(
            stale_html.replace(NOINDEX_META, ""))
        _, v = stale_findings(dist, base, threshold)
        if not any("noindex" in m for m in v):
            err("selftest: oracle missed a stale page stripped of its noindex meta")
        (dist / "stale-fixture" / "index.html").write_text(stale_html)

        (dist / "sitemap.xml").write_text(sitemap.replace(
            "</urlset>",
            f"  <url><loc>{base}/stale-fixture/</loc><lastmod>2020-01-01</lastmod></url>\n</urlset>"))
        _, v = stale_findings(dist, base, threshold)
        if not any("sitemap" in m for m in v):
            err("selftest: oracle missed a stale URL injected into sitemap.xml")

    if not errors:
        print("stale-selftest: scratch build + 4 policy assertions + oracle negative tests passed")


def main():
    if "--stale-selftest" in sys.argv:
        stale_selftest()
    else:
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
