# SignalCrate — owned data-site (jaxx-h.github.io)

A public, zero-dependency static site: every page is a unique, real data slice from a
live web-scrape run, rendered answer-first with schema markup so it can be found by
search **and** cited by AI answer engines. This repo is the owned distribution hub —
the canonical destination every other channel (syndication, X) links back to.

**Public repo, no secrets.** Never commit a token, key, or private path here.

## How it works

1. Data pages live in `content/pages/*.json` (see `CONTENT-CONTRACT.md`).
2. `scan_content.py` — PII guard at the **commit boundary**: fails if any content JSON
   contains an email-like string. Any rail that pushes content here must run it BEFORE
   committing (CI also runs it first, as a second net).
3. `build.py` (Python **stdlib only** — no pip, no Jekyll) renders them to `dist/`.
4. `check_site.py` — the independent oracle (root of the repo, shares zero rendering
   code with the builder): sitemap/JSON-LD/canonical/table-depth/title-uniqueness checks.
5. `.github/workflows/build-deploy.yml`: scan → build → check → deploy → `ping_indexnow.py`
   (auto-submits changed URLs to Bing/Yandex/DuckDuckGo; the IndexNow key is public by design).

```
python3 scan_content.py && python3 build.py && python3 check_site.py   # local
```

Template note: the CTA renders **before** the FAQ on data pages — intentional
(conversion before long-tail Q&A), documented here so nobody "fixes" it either way.

### PII incident runbook (if an email ever reaches public git history)
1. Delete/clean the offending file; commit.
2. Force-push a scrubbed history (`git filter-repo` or rebase) — this repo is small.
3. Contact GitHub Support to purge cached views of the old commits.
4. No secrets are involved (emails only), so nothing to rotate.
5. Log the incident to the operator bridge.

## Layout

- `config.json` — site name, url, tagline, optional custom-domain `cname`, analytics slot.
- `build.py` — the builder (contract validation + privacy guard + JSON-LD + sitemap/RSS/llms.txt).
- `check_site.py` — post-build validator (`--live` also curls the deployed site).
- `templates/` — `base.html`, `datapage.html`, `index.html` (string.Template).
- `static/style.css` — one small themeable stylesheet, no webfonts, no JS required.
- `content/pages/` — the data pages (the growing inventory).
- `tools/` — hand-authored client-side tool pages, shipped verbatim to `/tools/<slug>/`
  (each `test/` subdir is dev-only and never deployed). Tools are single-page, fully
  client-side (user files never upload), and deliberately outside the sitemap/nav until
  wired in; `check_site.py` checks each for title, exact canonical, and zero external
  resource loads beyond the site's own analytics snippet.

Fed by the cloud loop in `Jaxx-H/hq-income-engine` (writes contract-shaped page JSON here).
