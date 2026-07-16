#!/usr/bin/env python3
"""
build.py — zero-dependency static data-site builder (Python 3 stdlib ONLY).

Reads config.json + content/pages/*.json + templates/*.html and writes the whole
site to dist/. A broken page FAILS the build (exit 1) — it never ships silently.

Contract, privacy guard, and output artifacts are documented in CONTENT-CONTRACT.md.
No pip, no venv, no Jekyll, no third-party engines. string.Template only.
"""
import json
import re
import sys
import html
import shutil
from pathlib import Path
from string import Template
from datetime import datetime, timezone
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
PAGES_DIR = ROOT / "content" / "pages"
TPL_DIR = ROOT / "templates"
STATIC_DIR = ROOT / "static"

SLUG_RE = re.compile(r"^[a-z0-9-]{3,80}$")
# reserved output paths a page slug must never collide with
RESERVED_SLUGS = {"static", "assets", "404", "feed", "sitemap", "robots", "llms", "tools"}
# Privacy guard: no email may ever reach a rendered page. Emails are what the
# youtube actor SELLS; the site publishes AGGREGATES ONLY.
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")
# Stale-page policy (PLAN-04): a page whose data_source.fetched_at is more than
# this many days before the build date (UTC) gets a robots noindex meta and is
# excluded from sitemap.xml and feed.xml until refreshed. It still renders and
# stays on the homepage. CEILING constant: config.json "stale_after_days" may
# LOWER it, never raise it; a missing/invalid value fails closed to it.
STALE_AFTER_DAYS = 45
NOINDEX_META = '<meta name="robots" content="noindex">'


def die(msg):
    print(f"BUILD FAILED: {msg}", file=sys.stderr)
    sys.exit(1)


def load_config():
    cfg = json.loads((ROOT / "config.json").read_text())
    for key in ("site_url", "site_name", "tagline", "actor_base"):
        if not isinstance(cfg.get(key), str) or not cfg.get(key, "").strip():
            die(f"config.json: required key {key!r} is missing or empty")
    cname = (cfg.get("cname") or "").strip()
    if cname:
        cfg["site_url"] = f"https://{cname}"
    cfg["site_url"] = cfg["site_url"].rstrip("/")
    return cfg


def stale_after_days(cfg):
    """Effective staleness threshold in days. Fail closed: a missing or invalid
    config value means STALE_AFTER_DAYS; a valid one is clamped to the ceiling
    (config may lower it, never raise it)."""
    v = cfg.get("stale_after_days")
    if isinstance(v, bool) or not isinstance(v, int) or v < 1:
        return STALE_AFTER_DAYS
    return min(v, STALE_AFTER_DAYS)


def is_stale(p, today, threshold):
    """True when fetched_at is more than `threshold` days before `today` (the
    build-time UTC date). An unparseable date counts as stale (fail closed)."""
    try:
        fetched = datetime.strptime(p["data_source"]["fetched_at"][:10], "%Y-%m-%d").date()
    except ValueError:
        return True
    return (today - fetched).days > threshold


def tpl(name):
    return Template((TPL_DIR / name).read_text())


def word_count(*strings):
    n = 0
    for s in strings:
        n += len(str(s).split())
    return n


def validate_page(p, path, seen_slugs, seen_titles, seen_descs):
    def req(cond, msg):
        if not cond:
            die(f"{path.name}: {msg}")

    slug = p.get("slug", "")
    req(isinstance(slug, str) and SLUG_RE.match(slug), f"invalid/missing slug {slug!r} (must match {SLUG_RE.pattern})")
    req(slug not in RESERVED_SLUGS, f"slug {slug!r} collides with a reserved output path")
    req(slug not in seen_slugs, f"duplicate slug {slug!r}")
    seen_slugs.add(slug)

    title = p.get("title", "")
    req(isinstance(title, str) and title.strip(), "missing title")
    req(title not in seen_titles, f"duplicate title {title!r}")
    seen_titles.add(title)

    desc = p.get("description", "")
    req(isinstance(desc, str) and 0 < len(desc) <= 160, f"description must be 1..160 chars (got {len(desc)})")
    req(desc not in seen_descs, f"duplicate description {desc!r}")
    seen_descs.add(desc)

    # simple pages (page_type: "simple") — prose pages (policies, product/landing
    # pages) with their own fail-closed gates. Every datapage rule below stays
    # fully intact for data pages; this branch adds a page type, weakens nothing.
    if p.get("page_type") == "simple":
        req("data_source" not in p and "columns" not in p and "rows" not in p,
            "simple pages must not carry data-page fields (data_source/columns/rows)")
        body = p.get("body_html", "")
        req(isinstance(body, str) and body.strip(), "simple page needs body_html")
        low = body.lower()
        for bad in ("<script", "<iframe", "<object", "<embed", "javascript:"):
            req(bad not in low, f"body_html may not contain {bad!r}")
        req(not re.search(r"\son\w+\s*=", low), "body_html may not contain inline on* handlers")
        req(word_count(re.sub(r"<[^>]+>", " ", body)) >= 60,
            "simple page needs >=60 words of body prose")
        pub = p.get("published")
        if pub is not None:
            req(ISO_RE.match(str(pub)), "published, when present, must be ISO-8601 (YYYY-MM-DD...)")
        return slug

    af = p.get("answer_first", "")
    req(isinstance(af, str) and af.strip(), "missing answer_first")

    ds = p.get("data_source", {})
    req(isinstance(ds, dict) and ds.get("run_id"), "data_source.run_id is REQUIRED (no run, no page)")
    req(bool(ds.get("actor")), "data_source.actor required")
    req(ISO_RE.match(str(ds.get("fetched_at", ""))), "data_source.fetched_at must be ISO-8601 (YYYY-MM-DD...)")

    cols = p.get("columns", [])
    req(isinstance(cols, list) and len(cols) >= 2, "columns must have >=2 entries")
    rows = p.get("rows", [])
    req(isinstance(rows, list) and len(rows) >= 10, f"rows must have >=10 entries (got {len(rows)})")
    for r in rows:
        req(isinstance(r, list) and len(r) == len(cols), f"every row must have {len(cols)} cells")

    facts = p.get("facts", [])
    req(isinstance(facts, list) and len(facts) >= 3, "facts must have >=3 entries")
    for f in facts:
        req(isinstance(f, str) and any(c.isdigit() for c in f), f"each fact must contain a digit: {f!r}")

    faq = p.get("faq", [])
    req(isinstance(faq, list) and len(faq) >= 2, "faq must have >=2 {q,a}")
    for qa in faq:
        req(isinstance(qa, dict) and qa.get("q") and qa.get("a"), "each faq needs q and a")

    rp = p.get("related_product", {})
    req(isinstance(rp, dict) and rp.get("name"), "related_product.name required")
    req(str(rp.get("url", "")).startswith("https://apify.com/chilly_damask/"),
        "related_product.url must start with https://apify.com/chilly_damask/")

    analysis = p.get("analysis")
    if analysis is not None:
        req(isinstance(analysis, str) and analysis.strip(),
            "analysis, when present, must be a non-empty string")

    prose = " ".join([af] + facts + [q["q"] + " " + q["a"] for q in faq]
                     + ([analysis] if analysis else []))
    req(word_count(prose) >= 120, f"page needs >=120 prose words (got {word_count(prose)})")

    req(isinstance(p.get("citations", []), list), "citations must be a list")
    return slug


def esc(v):
    return html.escape(str(v))


def render_table(cols, rows):
    thead = "".join(f"<th>{esc(c)}</th>" for c in cols)
    body = []
    for r in rows:
        cells = "".join(f"<td>{esc(c)}</td>" for c in r)
        body.append(f"<tr>{cells}</tr>")
    return (
        '<div style="overflow-x:auto"><table>'
        f"<thead><tr>{thead}</tr></thead>"
        f"<tbody>{''.join(body)}</tbody></table></div>"
    )


def render_facts(facts):
    return "<ul class=\"facts\">" + "".join(f"<li>{esc(f)}</li>" for f in facts) + "</ul>"


def render_faq(faq):
    out = []
    for qa in faq:
        out.append(f"<details><summary>{esc(qa['q'])}</summary><p>{esc(qa['a'])}</p></details>")
    return "".join(out)


def render_analysis(p):
    a = p.get("analysis")
    return f'<h2>Analysis</h2><p class="analysis">{esc(a)}</p>' if a else ""


def render_citations(cits):
    if not cits:
        return ""
    items = "".join(f'<li><a href="{esc(u)}" rel="nofollow">{esc(u)}</a></li>' for u in cits)
    return f"<h2>Sources</h2><ul>{items}</ul>"


def dataset_jsonld(p, cfg, canonical):
    ds = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": p["title"],
        "description": p["description"],
        "dateModified": p["data_source"]["fetched_at"],
        "creator": {"@type": "Organization", "name": cfg["site_name"]},
        "url": canonical,
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q["q"],
             "acceptedAnswer": {"@type": "Answer", "text": q["a"]}}
            for q in p["faq"]
        ],
    }
    return (
        f'<script type="application/ld+json">{json.dumps(ds)}</script>\n'
        f'<script type="application/ld+json">{json.dumps(faq)}</script>'
    )


def privacy_scan(html_str, where):
    m = EMAIL_RE.search(html_str)
    if m:
        die(f"PRIVACY GUARD: email-like string {m.group(0)!r} would be published in {where}. "
            f"Pages publish AGGREGATES ONLY — strip all email/contact fields.")


def main():
    cfg = load_config()
    site_url = cfg["site_url"]
    year = datetime.now(timezone.utc).strftime("%Y")
    today = datetime.now(timezone.utc).date()
    threshold = stale_after_days(cfg)

    base = tpl("base.html")
    datapage = tpl("datapage.html")
    index_tpl = tpl("index.html")

    page_files = sorted(PAGES_DIR.glob("*.json"))
    seen_slugs, seen_titles, seen_descs = set(), set(), set()
    pages = []
    for pf in page_files:
        try:
            p = json.loads(pf.read_text())
        except json.JSONDecodeError as e:
            die(f"{pf.name}: invalid JSON — {e}")
        validate_page(p, pf, seen_slugs, seen_titles, seen_descs)
        pages.append(p)

    # simple pages render separately: never stale, listed in the sitemap,
    # excluded from the index card grid / feed / llms pages list (data surfaces)
    simple_pages = [p for p in pages if p.get("page_type") == "simple"]
    pages = [p for p in pages if p.get("page_type") != "simple"]

    # newest first
    pages.sort(key=lambda p: p["data_source"]["fetched_at"], reverse=True)

    # stale-page policy: stale pages still render (200) and stay on the
    # homepage, but are noindexed and dropped from sitemap.xml + feed.xml
    for p in pages:
        p["_stale"] = is_stale(p, today, threshold)
    fresh = [p for p in pages if not p["_stale"]]

    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # per-page
    for p in pages:
        slug = p["slug"]
        canonical = f"{site_url}/{slug}/"
        ds = p["data_source"]
        prov = (f"Data from run {esc(ds['run_id'])} of "
                f"<a href=\"{esc(p['related_product']['url'])}\">{esc(p['related_product']['name'])}</a>, "
                f"fetched {esc(ds['fetched_at'][:10])}.")
        cta = (f'<div class="cta"><p><strong>Get this data live for your own inputs.</strong></p>'
               f'<p><a class="btn" href="{esc(p["related_product"]["url"])}">Run '
               f'{esc(p["related_product"]["name"])} on Apify →</a></p></div>')
        content = datapage.substitute(
            h1=esc(p["title"]),
            answer_first=esc(p["answer_first"]),
            facts=render_facts(p["facts"]),
            table=render_table(p["columns"], p["rows"]),
            analysis=render_analysis(p),
            faq=render_faq(p["faq"]),
            cta=cta,
            provenance=prov,
            citations=render_citations(p.get("citations", [])),
        )
        page_html = base.substitute(
            title=esc(p["title"]),
            description=esc(p["description"]),
            canonical=canonical,
            robots=NOINDEX_META if p["_stale"] else "",
            jsonld=dataset_jsonld(p, cfg, canonical),
            analytics=cfg.get("analytics_snippet", ""),
            site_name=esc(cfg["site_name"]),
            tagline=esc(cfg["tagline"]),
            site_url=site_url,
            year=year,
            content=content,
        )
        privacy_scan(page_html, f"page {slug}")
        out_dir = DIST / slug
        out_dir.mkdir(parents=True)
        (out_dir / "index.html").write_text(page_html)

    # simple pages (page_type: "simple")
    for p in simple_pages:
        slug = p["slug"]
        canonical = f"{site_url}/{slug}/"
        webpage = {
            "@context": "https://schema.org", "@type": "WebPage",
            "name": p["title"], "description": p["description"], "url": canonical,
        }
        content = f'<article class="simple"><h1>{esc(p["title"])}</h1>\n{p["body_html"]}\n</article>'
        page_html = base.substitute(
            title=esc(p["title"]),
            description=esc(p["description"]),
            canonical=canonical,
            robots="",
            jsonld=f'<script type="application/ld+json">{json.dumps(webpage)}</script>',
            analytics=cfg.get("analytics_snippet", ""),
            site_name=esc(cfg["site_name"]),
            tagline=esc(cfg["tagline"]),
            site_url=site_url,
            year=year,
            content=content,
        )
        privacy_scan(page_html, f"page {slug}")
        out_dir = DIST / slug
        out_dir.mkdir(parents=True)
        (out_dir / "index.html").write_text(page_html)

    # index
    cards = []
    for p in pages:
        refreshing = " — data refreshing" if p["_stale"] else ""
        cards.append(
            f'<article class="card"><h2><a href="/{esc(p["slug"])}/">{esc(p["title"])}</a></h2>'
            f'<p>{esc(p["description"])}</p>'
            f'<p class="meta">Updated {esc(p["data_source"]["fetched_at"][:10])}{refreshing}</p></article>'
        )
    if not pages:
        cards.append('<p>No datasets published yet.</p>')
    itemlist = {
        "@context": "https://schema.org", "@type": "ItemList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "url": f"{site_url}/{p['slug']}/"}
            for i, p in enumerate(pages)
        ],
    }
    index_content = index_tpl.substitute(
        site_name=esc(cfg["site_name"]),
        tagline=esc(cfg["tagline"]),
        cards="\n".join(cards),
    )
    index_html = base.substitute(
        title=esc(cfg["site_name"]) + " — " + esc(cfg["tagline"]),
        description=esc(cfg["tagline"]),
        canonical=f"{site_url}/",
        robots="",
        jsonld=f'<script type="application/ld+json">{json.dumps(itemlist)}</script>',
        analytics=cfg.get("analytics_snippet", ""),
        site_name=esc(cfg["site_name"]),
        tagline=esc(cfg["tagline"]),
        site_url=site_url,
        year=year,
        content=index_content,
    )
    privacy_scan(index_html, "index")
    (DIST / "index.html").write_text(index_html)

    # sitemap.xml — FRESH pages only (stale pages rejoin once refreshed);
    # homepage lastmod = newest page fetch date (the homepage changes whenever
    # inventory changes), falling back to today for an empty site
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = ([f"{site_url}/"] + [f"{site_url}/{p['slug']}/" for p in fresh]
            + [f"{site_url}/{p['slug']}/" for p in simple_pages])
    home_lastmod = (max(p["data_source"]["fetched_at"][:10] for p in pages)
                    if pages else today_str)
    lastmods = ([home_lastmod] + [p["data_source"]["fetched_at"][:10] for p in fresh]
                + [str(p.get("published", today_str))[:10] for p in simple_pages])
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, lm in zip(urls, lastmods):
        sm.append(f"  <url><loc>{xml_escape(u)}</loc><lastmod>{lm}</lastmod></url>")
    sm.append("</urlset>")
    (DIST / "sitemap.xml").write_text("\n".join(sm))

    # robots.txt — deliberately NO Disallow: AI crawlers welcome
    (DIST / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {site_url}/sitemap.xml\n")

    # feed.xml (RSS 2.0, 30 newest FRESH pages — stale pages rejoin once refreshed)
    items = []
    for p in fresh[:30]:
        items.append(
            "<item>"
            f"<title>{xml_escape(p['title'])}</title>"
            f"<link>{site_url}/{p['slug']}/</link>"
            f"<guid>{site_url}/{p['slug']}/</guid>"
            f"<description>{xml_escape(p['answer_first'])}</description>"
            "</item>"
        )
    rss = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<rss version="2.0"><channel>'
           f"<title>{xml_escape(cfg['site_name'])}</title>"
           f"<link>{site_url}/</link>"
           f"<description>{xml_escape(cfg['tagline'])}</description>"
           + "".join(items) + "</channel></rss>")
    (DIST / "feed.xml").write_text(rss)

    # llms.txt
    lt = [f"# {cfg['site_name']}", "", f"> {cfg['tagline']}", "",
          "Answer-first datasets built from live web-scrape runs. Each page carries a "
          "unique real data slice, a fetch date, and a source run id.", "", "## Pages"]
    for p in pages:
        lt.append(f"- {site_url}/{p['slug']}/ — {p['description']}")
    (DIST / "llms.txt").write_text("\n".join(lt) + "\n")

    # 404
    notfound = base.substitute(
        title="Not found — " + esc(cfg["site_name"]),
        description="Page not found.",
        canonical=f"{site_url}/",
        robots="",
        jsonld="", analytics=cfg.get("analytics_snippet", ""),
        site_name=esc(cfg["site_name"]), tagline=esc(cfg["tagline"]),
        site_url=site_url, year=year,
        content='<h1>404</h1><p>That page does not exist. <a href="/">Back to the index →</a></p>',
    )
    (DIST / "404.html").write_text(notfound)

    # belt-and-braces: never let Pages run Jekyll
    (DIST / ".nojekyll").write_text("")

    # IndexNow key file (hosted at /<key>.txt) so we can push instant index pings
    # to Bing / Yandex / DuckDuckGo with no account and no secret.
    inkey = (cfg.get("indexnow_key") or "").strip()
    if inkey:
        (DIST / f"{inkey}.txt").write_text(inkey + "\n")

    # static assets
    if STATIC_DIR.exists():
        shutil.copytree(STATIC_DIR, DIST / "static")

    # hand-authored client-side tool pages: tools/<slug>/index.html ships
    # verbatim to /tools/<slug>/ (plus any runtime assets like demo fixtures).
    # test/ subdirs are dev-only and never deployed. Tool pages are deliberately
    # NOT in the sitemap/nav yet — soft launch; check_site.py checks them
    # separately (title, canonical, no external resource loads).
    tools_dir = ROOT / "tools"
    if tools_dir.exists():
        shutil.copytree(tools_dir, DIST / "tools",
                        ignore=shutil.ignore_patterns("test"))

    # CNAME (only when a custom domain is configured)
    if (cfg.get("cname") or "").strip():
        (DIST / "CNAME").write_text(cfg["cname"].strip() + "\n")

    n_stale = len(pages) - len(fresh)
    stale_note = f" ({n_stale} stale: noindexed, out of sitemap/feed)" if n_stale else ""
    simple_note = f" + {len(simple_pages)} simple page(s)" if simple_pages else ""
    print(f"Built {len(pages)} data page(s){simple_note}{stale_note} → {DIST}")


if __name__ == "__main__":
    main()
