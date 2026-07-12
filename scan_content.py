#!/usr/bin/env python3
"""
scan_content.py — PII guard at the COMMIT boundary. Stdlib only.

Scans the RAW text of every content/pages/*.json for email-like strings and
exits 1 on any hit. This runs BEFORE build.py in CI (and must run in any rail
that pushes content into this PUBLIC repo — e.g. the private repo's site-sync —
so an email never reaches public git history at all, not merely never renders).

The render-time guard in build.py stays as the second layer; this is the first.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

hits = []
for f in sorted((ROOT / "content" / "pages").glob("*.json")):
    m = EMAIL_RE.search(f.read_text())
    if m:
        hits.append((f.name, m.group(0)))

if hits:
    print("PII SCAN FAILED — email-like strings in content JSON (must never be committed):",
          file=sys.stderr)
    for name, s in hits:
        print(f"  {name}: {s!r}", file=sys.stderr)
    sys.exit(1)

print(f"PII scan OK: {len(list((ROOT / 'content' / 'pages').glob('*.json')))} content file(s) clean")
