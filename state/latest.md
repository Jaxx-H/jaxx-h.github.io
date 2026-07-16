# STATE — HQ Income Engine (machine-written bridge)

_Generated 2026-07-16 12:12 UTC by tools/state_snapshot.py (state-snapshot.yml). GitHub is canon; this file replaces the Notion Bridge (operator ruling 2026-07-15)._

## Last 15 commits (hq-income-engine main)
```
cec8fd3 metrics: 2026-07-16 — daily snapshot (3 reward row(s))
de4b79f index: rebuild from 4f5f19c [skip ci]
4f5f19c OPERATOR LITERACY RULE: repo CLAUDE.md + brain/glosses.jsonl (strategy-chat ruling 2026-07-16) (#43)
f2a8394 index: rebuild from 21eb432 [skip ci]
21eb432 R6: W1 Calibration gate verdict — NO-GO encoded (H4 near-dead, registry gated, D-003); W2 Exit-Rights Memory is next (#42)
ff16b86 index: rebuild from c2d1451 [skip ci]
c2d1451 WS-2: fold-in event chains — sole ledger writer, DISARMED (DIRECTIVE v3) — operator-ratify (#41)
3642534 index: rebuild from f8ebf45 [skip ci]
f8ebf45 Merge pull request #40 from Jaxx-H/claude/r6-personal-ai-discovery
9825d43 BET-R6 sweep 1: tracks 1/2/6/7 verbatim + knowledge base + hypotheses + wedges + decision log
d24eed8 BET-R6: personal-AI category discovery program (operator directive 2026-07-16)
f323d53 index: rebuild from 0ddf382 [skip ci]
0ddf382 Merge pull request #39 from Jaxx-H/claude/ws0-workflow-hygiene
671af22 index: rebuild from 174d836 [skip ci]
174d836 WS-1: index-on-merge kernel (DIRECTIVE v3) — operator-ratify (#38)
```

## Open PRs
```
#44 [claude/frontier-fopw6v] R&D: BET-R6 — sweep-2 tests H3/H4, demotes W1 rank-1, names a funded W2 competitor
#4 [claude/wizardly-cray-69npyj] distribution: complete the dev.to job-scraper tutorial (devto-syndication arm)
```

## Reward ledger — newest 8 rows (brain/experiments.jsonl)
```json
{"ts": "2026-07-13", "arm": "apify-listing-seo", "reward": 0, "cost": 1, "source": "cloud/websearch-spotcheck", "evidence": "brain/research/2026-07-13-apify-listing-seo-competitive-scan.md", "note": "WebSearched core buyer-intent queries for all 3 actors (job scraper/hiring-signals, youtube channel email finder, app store+google play review scraper). NONE of our 3 listings appeared in any result set across 4 queries (job-scraper: 10 named competitors visible, none ours; youtube-lead: 6+ named competitors, none ours; review-scraper: 8+ named competitors, none ours) -- organic-visibility gap confirmed as still open, not resolved by the 2026-07-10 seoTitle/seoDescription change. Not exhaustive (WebSearch snippets, not full SERPs) so treat as directional signal, not proof of zero ranking."}
{"ts": "2026-07-15", "arm": "multilingual-demand", "reward": 0, "cost": 1, "source": "cloud/websearch-spotcheck", "evidence": "brain/research/2026-07-15-multilingual-language-gap-recheck-hiring-review.md", "note": "First-ever observation for this arm (was n=0). WebSearched native-term queries in German, Japanese, Korean for whether job-scraper (hiring-signals) or review-scraper (app-review scraping) categories have an underserved non-English market. All 3 found established, sometimes more-sophisticated native incumbents (index Salesdriver 15-country EU coverage; SalesNow AI-agent-native MCP integration; HashScraper+AppTweak Korean app-review tooling) -- NO GAP found in any of the 3 markets checked for this specific hypothesis (translate-existing-actor-category-to-new-language). validated_gaps has no traffic-weighted event in reward_map.json so reward=0 is the honest, expected value for a qualitative research arm; this is not a traffic/revenue measurement."}
{"ts": "2026-07-15", "arm": "owned-geo-site", "reward": 0.01, "cost": 0, "source": "local/collect_metrics", "evidence": "metrics/daily/2026-07-15.json#goatcounter.total", "note": "1 organic_pageview x 0.01 = 0.01; window 2026-07-12T16:00:00Z..2026-07-15T23:00:00Z (backfill self-heals closed-laptop gaps)"}
{"ts": "2026-07-15", "arm": "apify-listing-seo", "reward": 21.75, "cost": 0, "source": "local/collect_metrics", "evidence": "metrics/daily/2026-07-15.json#apify.actors", "note": "87 external_actor_run x 0.25 = 21.75 (totalRuns delta {'youtube-lead': 35, 'review-scraper': 25, 'job-scraper': 27}; may include own runs); window 2026-07-12T16:00:00Z..2026-07-15T23:00:00Z (backfill self-heals closed-laptop gaps)"}
{"ts": "2026-07-15", "arm": "apify-listing-seo", "reward": 0.12, "cost": 0, "source": "local/collect_metrics#revenue", "evidence": "metrics/revenue/2026-07.json#entries", "note": "revenue_id=2026-07-apify-job-scraper-1 0.12 revenue_usd x 1.0 = 0.12 (first paid usage ever — Apify Insights July 2026, paying-user revenue on company-careers-job-scraper (being listed produ)"}
{"ts": "2026-07-16", "arm": "owned-geo-site", "reward": 0.2, "cost": 0, "source": "local/collect_metrics", "evidence": "metrics/daily/2026-07-16.json#goatcounter.total", "note": "20 organic_pageview x 0.01 = 0.2; window 2026-07-15T23:00:00Z..2026-07-16T12:00:00Z (backfill self-heals closed-laptop gaps)"}
{"ts": "2026-07-16", "arm": "apify-listing-seo", "reward": 0.5, "cost": 0, "source": "local/collect_metrics", "evidence": "metrics/daily/2026-07-16.json#apify.actors", "note": "2 external_actor_run x 0.25 = 0.5 (totalRuns delta {'youtube-lead': 0, 'review-scraper': 0, 'job-scraper': 1, 'podcast-host': 1}; may include own runs); window 2026-07-15T23:00:00Z..2026-07-16T12:00:00Z (backfill self-heals closed-laptop gaps)"}
{"ts": "2026-07-16", "arm": "apify-listing-seo", "reward": 1.88, "cost": 0, "source": "local/collect_metrics#revenue", "evidence": "metrics/revenue/2026-07.json#entries", "note": "revenue_id=2026-07-apify-portfolio-2 1.88 revenue_usd x 1.0 = 1.88 (operator-attested in session 2026-07-15: Apify Insights July total now ~$2.00; this entry books the delta over the prior)"}
```

## R&D book — newest 5 bet rows (brain/rnd/bets.jsonl)
```json
{"ts": "2026-07-16T12:00:00Z", "bet": "BET-R1", "action": "experiment-1: pain-mining pass over committed review-scraper data (data/runs/reviews/*/latest.json)", "evidence": "Built brain/rnd/prototypes/BET-R1/pain_miner.py (stdlib, self-tested, deterministic keyword taxonomy, no ML). Scanned 1448 real reviews across 10 apps already committed to this repo, 827 (57%) rated <=2 stars. Severity-weighted ranked gap list (brain/rnd/prototypes/BET-R1/ranked_gaps.md + gap_list.json): crashes/bugs (severity 176), notifications (158), pricing/subscription (127), customer-support (119), missing-feature (111). Ag-ops apps show disproportionate negative share for their size vs job-search apps: climate-fieldview 66.2% negative (49/74), john-deere-operations-center 50.5% (48/95), fbn 46.4% (13/28) -- with concrete, cited complaints: subscription-gated data export (climate-fieldview 1-star: cancel your plan and \"they won't give it to you without it\"), a broken signup flow (agriwebb 1-star: \"the app doesn't have a sign up page\"), Android/iOS feature-parity gaps. WebSearch confirmed real competitive demand for this exact content angle: G2, Capterra, SaaSHub, Sourceforge, and Datarade all already publish ranking 'Climate FieldView alternatives' pages, while Climate's own ToS/FAQ claims data export is fully supported -- a policy-vs-lived-experience gap a review-cited comparison page could credibly cover with real citations, not fabricated ones. Job-search apps (monster 86.2% neg, indeed 62.5%, linkedin 66.7%) have higher raw volume but that lane was already flagged saturated by the 2026-07-11 and 2026-07-13 research runs, so excluded from the top candidate this run.", "score": {"C": 4, "D": 3, "F": 5, "R": 5, "T": 5}, "verdict": "LIVE (C4xD3xF5=60, revised from seed C4xD4xF4=64 to C4xD3xF5=60 after real evidence: F and T revised up from estimated 4/unscored to proven 5/5 since the pipeline ran end-to-end this run; D revised down from seeded 4 to 3 because the CONTENT layer for the top candidate already has ranking competitors (G2/Capterra/SaaSHub) -- the defensible asset is the review-mining sensor + our own weekly-refreshed corpus, not the eventual comparison-page content itself)", "next": "Feed the top-ranked gap (ag-ops subscription/data-export lock-in pain) into the existing P2 page-factory as a new registered slice, quote-cited to real reviews, through the standard PII-scan + quality-gate rail -- next run, not this one (depth over breadth). Re-run pain_miner.py as new review verticals land via the Mon/Wed/Fri refresh crons so the gap list compounds instead of going stale; do not fabricate search-volume or funnel numbers beyond what a cited WebSearch or registered slice run finds."}
```

## ROADMAP head
```
# ROADMAP — current priorities (rewrite as evidence lands)

**North star:** [[STRATEGY.md]] — marketing-first, own-the-customer, Chegg-test every build. Supply (actors) is nearly free; leverage is on attention + a moat the model can't reproduce.

## State (2026-07-11, after the full system audit — `brain/research/2026-07-11-full-system-audit.md`)
- 3 actors LIVE + priced + public on Apify. Revenue $0 — **structural, not a bug**: a marketplace listing is a conversion endpoint, not a demand engine. More actors will NOT move it; one owned channel will.
- **Audit verdict:** strategy right, loop right, but (a) our actors are easy/low-defense targets = the commoditized 0–5-user end of Apify's power law (top earners are all hard anti-bot targets we don't maintain); (b) our hiring-signals wedge is saturated (13+ competitors); (c) we own no distribution channel. All three are fixed below.
- Everything backed up + reset-proof (13 private repos, memory mirror, `restore.sh`); cloud loop LIVE 3×/day.

## P0 — VALIDATE THE NEW WEDGE (regulatory forced-adoption), then commit
The audit found a far better vein than hiring-signals: **legally-forced 2026–2028 compliance mandates** on small businesses/farmers (demand mandated, dated, fined, underserved long tail; language-gap arbitrage country-by-country). Lead candidate fits THIS operator uniquely:
1. **EU electronic pesticide / plant-protection record-keeping** (Reg EU 2023/564, electronic + machine-readable, effective 2026). Operator is a farmer → domain trust + IS the customer; passes the Chegg test; buildable in weeks; no KYC/network blockers.
2. **Loop's next demand-research runs VALIDATE before we build:** confirm the reg + per-country electronic deadline (primary sources only), find which language markets have NO localized incumbent, size the underserved smallholder tail, and spec a mobile-form → validated JSON/XML/CSV MVP. Kill/keep on evidence; do NOT fabricate certainty.
3. Fallbacks if farm-compliance doesn't validate: single-country e-invoicing micro-SaaS on **rented Peppol** (own the customer via white-label) · localized-clone of a proven English micro-SaaS.

## P1 — BUILD ONE OWNED CHANNEL (this is the whole game)
We have zero owned distribution. Fix, in order of payback speed:
1. **An email list we own** — the #1 differentiator between the 44%-at-$0 and the earners. A one-page site + capture around the chosen wedge.
2. **Manual last-mile the machine drafts, the operator ships:** genuine community participation (Reddit/Discord, 9:1 give-before-ask) + ~10 hyper-personalized cold outreach/day to the EXACT buyer. These pay in 30–90 days; SEO/build-in-public compound over 6–12mo. (Mass-posting = banned; the safe version is slow + manual — HARD LAW 1c.)
3. **De-emphasize generic SEO** — AI Overviews cut position-1 CTR 58%; AI-written slop is penalized. Only comparison/"X-alternative" content aimed at buyers already shopping earns.

## P2 — Actors become funnel, not product
Keep the 3 live as free lead-gen that routes buyers to the owned product. Optional: move ONE actor toward a genuinely contested target we commit to maintaining weekly (maintenance IS the moat) — only if it feeds the wedge.

## ALWAYS-ON ENGINE (build sequence — `brain/ARCHITECTURE.md`)
```

## R&D portfolio head
```
# R&D portfolio — the frontier bets (seeded 2026-07-15)

Scored per CHARTER.md rubric (Ceiling × Defensibility × Feasibility ≥ 27 to stay live).
Initial scores are the seeding session's honest estimates — the frontier loop re-scores as
evidence lands. Ledger: `bets.jsonl` (append-only outcomes per run).

> **GATE AMENDMENT (operator ruling 2026-07-15, via strategy chat):** every opportunity the
> demand-mining factory surfaces MUST name (a) where its buyers already congregate and (b) how
> they would find this specific product — a concrete distribution answer. Without one the
> verdict is half a verdict and the opportunity does not rank. Attention is a required field —
> a mined app with no distribution path inherits Cal AI's playbook minus their paid-attention
> budget and dies at the attention node.

## BET-R1 — The demand-mining app factory  ·  C4 × D3 × F5 = 60  ·  LIVE
Turn our scrapers from products into SENSORS: mine app-store reviews + job posts + community
complaints at scale for high-volume, high-severity, FIXABLE pain (the Cal-AI opportunity shape,
found programmatically instead of by luck). Rank gaps → machine ships candidate web apps
(no review latency, Stripe capture, instant A/B) → closed outcome loop kills or scales → winners
get ported to the App Store. Durable asset: the opportunity-detection pipeline itself + the
portfolio of surviving products. Defensibility: the review-mining sensor + our own weekly-
```

