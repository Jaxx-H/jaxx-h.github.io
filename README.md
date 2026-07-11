# SignalCrate — owned data-site (jaxx-h.github.io)

A public, zero-dependency static site: every page is a unique, real data slice from a
live web-scrape run, rendered answer-first with schema markup so it can be found by
search **and** cited by AI answer engines. This repo is the owned distribution hub —
the canonical destination every other channel (syndication, X) links back to.

**Public repo, no secrets.** Never commit a token, key, or private path here.

## How it works

1. Data pages live in `content/pages/*.json` (see `CONTENT-CONTRACT.md`).
2. `build.py` (Python **stdlib only** — no pip, no Jekyll) renders them to `dist/`.
3. `check_site.py` validates the build.
4. `.github/workflows/build-deploy.yml` runs both on every push to `main` and deploys
   `dist/` to GitHub Pages.

```
python3 build.py && python3 check_site.py   # local
```

## Layout

- `config.json` — site name, url, tagline, optional custom-domain `cname`, analytics slot.
- `build.py` — the builder (contract validation + privacy guard + JSON-LD + sitemap/RSS/llms.txt).
- `check_site.py` — post-build validator (`--live` also curls the deployed site).
- `templates/` — `base.html`, `datapage.html`, `index.html` (string.Template).
- `static/style.css` — one small themeable stylesheet, no webfonts, no JS required.
- `content/pages/` — the data pages (the growing inventory).

Fed by the cloud loop in `Jaxx-H/hq-income-engine` (writes contract-shaped page JSON here).
