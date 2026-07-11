#!/usr/bin/env python3
"""
ping_indexnow.py — submit all live URLs to IndexNow (Bing/Yandex/DuckDuckGo).

No account, no secret, ToS-safe. Reads config.json for the site + key, reads the
built dist/ (or content/pages/) for the URL list, and POSTs one batch to IndexNow.
Run after every deploy that adds/changes pages. Stdlib only.
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
cfg = json.loads((ROOT / "config.json").read_text())
key = (cfg.get("indexnow_key") or "").strip()
if not key:
    print("no indexnow_key in config.json — nothing to do")
    sys.exit(0)

cname = (cfg.get("cname") or "").strip()
base = f"https://{cname}" if cname else cfg["site_url"].rstrip("/")
host = base.split("://", 1)[1]

# URL list from built dist/ if present, else from content/pages/
dist = ROOT / "dist"
urls = [base + "/"]
if dist.exists():
    for d in sorted(dist.iterdir()):
        if d.is_dir() and d.name != "static" and (d / "index.html").exists():
            urls.append(f"{base}/{d.name}/")
else:
    for pf in sorted((ROOT / "content" / "pages").glob("*.json")):
        slug = json.loads(pf.read_text()).get("slug")
        if slug:
            urls.append(f"{base}/{slug}/")

payload = json.dumps({
    "host": host,
    "key": key,
    "keyLocation": f"{base}/{key}.txt",
    "urlList": urls,
}).encode()

req = urllib.request.Request(
    "https://api.indexnow.org/indexnow",
    data=payload,
    headers={"Content-Type": "application/json; charset=utf-8"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=25) as resp:
        print(f"IndexNow: HTTP {resp.getcode()} for {len(urls)} URL(s)")
        for u in urls:
            print("  submitted:", u)
except urllib.error.HTTPError as e:
    # 200/202 are success; IndexNow returns 200 with empty body normally
    print(f"IndexNow HTTP {e.code}: {e.reason}")
    if e.code not in (200, 202):
        sys.exit(1)
except Exception as e:
    print(f"IndexNow ping failed: {e}")
    sys.exit(1)
