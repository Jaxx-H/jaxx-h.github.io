#!/usr/bin/env python3
"""
check_site.py — post-build validator. Stdlib only.

  python3 check_site.py         # check the local dist/ build
  python3 check_site.py --live  # additionally curl the live site for HTTP 200s

Exits non-zero on any failure so CI blocks a broken deploy.
"""
import json
import sys
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

errors = []


def err(m):
    errors.append(m)


def check_local():
    if not DIST.exists():
        err("dist/ does not exist — run build.py first")
        return
    required = ["index.html", "sitemap.xml", "robots.txt", "feed.xml",
                "llms.txt", "404.html", ".nojekyll", "static/style.css"]
    for r in required:
        if not (DIST / r).exists():
            err(f"missing required output: {r}")

    # every page dir has index.html + a canonical + no emails
    page_dirs = [d for d in DIST.iterdir() if d.is_dir() and d.name != "static"]
    for d in page_dirs:
        idx = d / "index.html"
        if not idx.exists():
            err(f"page {d.name} has no index.html")
            continue
        h = idx.read_text()
        if 'rel="canonical"' not in h:
            err(f"page {d.name} missing canonical link")
        if "application/ld+json" not in h:
            err(f"page {d.name} missing JSON-LD")
        m = EMAIL_RE.search(h)
        if m:
            err(f"page {d.name} contains email-like string {m.group(0)!r} (privacy leak)")

    # scan ALL html for emails (belt and braces)
    for html_file in DIST.rglob("*.html"):
        m = EMAIL_RE.search(html_file.read_text())
        if m:
            err(f"{html_file.relative_to(DIST)} contains email-like string {m.group(0)!r}")

    print(f"local: checked {len(page_dirs)} page(s) + required artifacts")


def check_live():
    cfg = json.loads((ROOT / "config.json").read_text())
    cname = (cfg.get("cname") or "").strip()
    base = f"https://{cname}" if cname else cfg["site_url"].rstrip("/")
    urls = [base + "/", base + "/sitemap.xml", base + "/robots.txt"]
    # include one page url if present
    page_dirs = [d for d in DIST.iterdir() if d.is_dir() and d.name != "static"] if DIST.exists() else []
    if page_dirs:
        urls.append(f"{base}/{page_dirs[0].name}/")
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "check_site/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                code = resp.getcode()
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
