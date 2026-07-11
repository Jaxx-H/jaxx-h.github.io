# Page contract

Every file in `content/pages/<slug>.json` MUST satisfy this contract or `build.py`
aborts the whole build with exit 1 (a broken page never ships). This is the interface
the cloud loop writes to: fill the JSON, the machinery renders + deploys.

## Required fields

| Field | Rule |
|---|---|
| `slug` | `^[a-z0-9-]{3,80}$`, unique across the site. Becomes `/<slug>/`. |
| `title` | Non-empty, unique across the site. |
| `description` | 1–160 chars. Used as meta description + card subtitle. |
| `answer_first` | One paragraph that directly answers the query with concrete numbers. |
| `data_source.actor` | The Apify actor name the data came from. |
| `data_source.run_id` | **REQUIRED.** The real run id. No run, no page. |
| `data_source.fetched_at` | ISO-8601 date (`YYYY-MM-DD...`). Drives sort order + provenance. |
| `columns` | ≥2 column headers. |
| `rows` | ≥10 rows; every row has exactly `len(columns)` cells. |
| `facts` | ≥3 strings, **each containing a digit**. |
| `faq` | ≥2 `{q, a}` objects. |
| `related_product.name` | CTA label. |
| `related_product.url` | Must start with `https://apify.com/chilly_damask/`. |
| `citations` | List of URLs (may be empty only if all data is from the actor run). |

Also enforced: total prose (`answer_first` + `facts` + `faq`) ≥ 120 words.

## Hard privacy guard

`build.py` scans every rendered HTML page for an email-like string
(`[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`) and **fails the build** if one is
found. Pages publish **aggregates only** — channel names, counts, subscriber bands,
country. Email/contact data is what the actor *sells*; it never appears on the site.

## What the build emits (to `dist/`)

- `/<slug>/index.html` per page — answer-first prose, facts, data table, FAQ, CTA,
  provenance line, embedded Dataset + FAQPage JSON-LD.
- `index.html` — all pages newest-first, ItemList JSON-LD.
- `sitemap.xml`, `robots.txt` (no `Disallow` — AI crawlers welcome), `feed.xml` (RSS),
  `llms.txt`, `404.html`, `.nojekyll`, `static/style.css`, and `CNAME` when
  `config.json.cname` is set.

## Local workflow

```
python3 build.py        # render content/pages/*.json -> dist/
python3 check_site.py   # validate the build (CI runs this too)
```

GitHub Actions runs both on every push to `main` and deploys `dist/` to Pages.
No dependencies, no build step beyond `python3`.
