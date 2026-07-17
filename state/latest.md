# STATE — HQ Income Engine (machine-written bridge)

_Generated 2026-07-17 13:27 UTC by tools/state_snapshot.py (state-snapshot.yml). GitHub is canon; this file replaces the Notion Bridge (operator ruling 2026-07-15)._

## Last 15 commits (hq-income-engine main)
```
39688a0 reward_map v2 PROPOSAL: external_actor_run 0.25 -> 0.05 (operator sign-off)
2e1645d index: rebuild from ee623a3 [skip ci]
ee623a3 Radar governance + Day-1 reprocess (DIRECTIVE 2026-07-17, Tracks 0-2)
5826d14 index: rebuild from 5c04644 [skip ci]
5c04644 R&D: BET-R6 — W3 Memory Watchdog diff/alert engine (build increment)
0551643 refresh(creators): data snapshot [skip ci]
7ca5f4c index: rebuild from 7d827b4 [skip ci]
7d827b4 BET-ATT-001 brand brief: rebuilt on current main (brief file only; outcomes row dropped to avoid the shared-log collision)
1841667 index: rebuild from ee02908 [skip ci]
ee02908 Update observability run log
1c92922 Update observability run log
feea459 Update observability run log
4ebfef7 Update observability run log
9347e91 Update observability run log
9919f05 EU 2023/564 retirement: rebuilt on current main (money-tree + country-map + outcomes row; no shared-file drift)
```

## Open PRs
```
#55 [claude/wizardly-cray-gb4qbb] DEMAND RESEARCH: Japan-market check for a foreign-AI-company hiring content gap
#54 [claude/verify-pass-uqpzty] verify: daily pass — back-check EU 2023/564 and listing-seo pricing memos against primary sources
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
{"ts": "2026-07-16T14:10:00Z", "bet": "BET-R6", "action": "sweep-2 targeted verification: WebSearch tested H3 (portability-tool demand/traction) and H4 (decision-journal retention) against their own sweep-1 what-would-change-our-minds conditions, per PROGRAM.md (no wedge greenlit until load-bearing hypotheses survive sweep 2)", "evidence": "KB-28: XTrace, a funded competitor ($3.3M pre-seed led by Draper Associates, founded 2024, Private Beta), builds exactly W2's \"private, portable AI memory infrastructure\" thesis -- but traction is enterprise/regulated-industry, not consumer. KB-29: free OSS DIY tools already exist for W2's mechanic (mychatarchive, hippo-memory, assorted chatgpt-export repos), plus native Claude/Google cross-platform memory import-export now ships. Consumer-scale portability traction remains NONE FOUND either way (no positive or negative data) -- so H3 stays open (confidence held 0.55) but W2's defensibility section now names real, cited competition instead of an assumed-open field. KB-30: an independent Indie Hackers founder tested W1's exact wedge shape (frictionless/voice journaling with review) and killed it, diagnosing the SAME behavioral blocker H4's own contradicting evidence flagged (\"the real pain is not doing it consistently, not lack of a tool\"); industry-wide stat found 87% of journaling-app users abandon within 7 days. KB-31: counter-evidence that calibration training works when review IS sustained (19% forecasting improvement, secondary-sourced, flagged for sweep-3 primary check) -- isolates the real open question to retention, not mechanism value. H4 downgraded open-to-weakened (confidence 0.5->0.35, hypothesis-register.md); W1 demoted from an uncontested rank-1 pending an actual retention MVP (wedge-registry.md); D-003 logged (decision-log.md).", "score": {"C": 5, "D": 3, "F": 4, "R": 5, "T": 5}, "verdict": "LIVE (C5xD3xF4=60, unchanged at program level -- ambition and machine-feasibility did not move; this run's finding is a wedge-level rerank, not a bet-level kill. Time-to-evidence (T) proven 5/5 again: two load-bearing hypotheses moved on a single cheap WebSearch pass, exactly the CHARTER T=5 case.)", "next": "Two paths open, pick ONE next run (depth over breadth): (a) continue sweep-2 on the remaining open hypotheses (H2 memory-reliability willingness-to-pay, H5 proactivity, H6 trust-escalation) -- all still cheap WebSearch-shaped tests per their own what-would-change-our-minds conditions; or (b) stop researching W1 and either run a real zero-friction-logger retention probe (the only test that can actually revive H4) or shift build attention to W3 (Memory Watchdog -- cheapest, least contested, no comparable failure precedent found this run, and is explicitly the trust-earning on-ramp to W2 per H6). Do not re-run the same XTrace/OSS-competitor search again -- that evidence is now committed; next run should hit new ground (H2/H5/H6) or move from research to a build-shaped experiment."}
{"ts": "2026-07-17T08:20:00Z", "bet": "BET-R6", "action": "W3 'Memory Watchdog' experiment 1: built the wedge's core mechanic as a real, self-tested prototype (a build-shaped increment, different from the prior two research-only sweep-2 runs, per PROGRAM.md's own 'depth over breadth, pick one' next-step and wedge-registry.md's own recommendation to weigh W3 against a W1 retention MVP)", "evidence": "Shipped brain/rnd/prototypes/BET-R6-W3/memory_watchdog.py (stdlib, argparse CLI, no network/API access required or used). Core mechanic: parse a memory-summary export (one remembered fact per line -- the actual render shape of ChatGPT's and Claude's own memory-summary pages per KB-02/KB-05) into normalized facts, diff two snapshots, and classify every change as ADDED / REMOVED (silently gone -- the exact alert condition W3 exists to catch) / CHANGED (paraphrase-matched by word-overlap Jaccard similarity so platform rewording doesn't fire a false 'you lost a memory' alert) / UNCHANGED, plus alert-level rollup (ALERT on any REMOVED, WARN on CHANGED-only, INFO on ADDED-only, OK on no diff). Also built the operational shell the wedge spec calls for: `add-snapshot` (versioned local storage under snapshots/<assistant>/) and `diff-latest` (auto-diffs the two newest snapshots). Verified two ways: (1) `--self-test` -- 9 deterministic assertions against a synthetic, clearly-labeled fixture (not claimed as real user data), all PASS, independently re-runnable; (2) manual CLI smoke test with real temp files exercising diff/add-snapshot/diff-latest end-to-end, output matches expected classification exactly (verified this run, temp artifacts discarded, not committed). Honest gap: snapshots/ ships EMPTY -- this run produced feasibility evidence (the engine works, deterministic, cheap), not market evidence; no real ChatGPT/Claude memory-page export has been captured yet, which needs an operator paste (same intake pattern as the existing Apify README paste workflow, brain/outcomes.jsonl 2026-07-13/07-16) or a future authenticated session. Horizon scan (KB-33, knowledge-base.md): WebSearch found 'memory integrity/audit' emerging as a live 2026 platform theme -- AgentPrizm publicly launched a governed AI-agent-memory platform July 9 2026 ('agents that can prove what they remember', audit receipts, verifiable deletion) and Microsoft's Security Blog published 'Guarding AI memory' June 22 2026 -- but both are B2B/agent-infra and adversarial-security framed respectively, not W3's consumer/benign-silent-loss wedge; NONE FOUND of a direct consumer competitor this run. Does not create or kill a bet; noted for the eventual W3 gate's competitive section.", "score": {"C": 5, "D": 3, "F": 4, "R": 5, "T": 5}, "verdict": "LIVE (C5xD3xF4=60, program-level score unchanged -- this is a wedge-level feasibility increment, not a program-level rescore, matching the 2026-07-16 precedent's own distinction. R and T both proven 5/5 again: the diff/alert mechanic is now a working, independently-re-runnable artifact (compounds the harness -- CHARTER Reusability -- since snapshot/diff/alert is a generically useful pattern beyond this one wedge) built and tested in a single cheap run with zero spend.", "next": "Two paths, pick ONE next run (depth over breadth): (a) get one real before/after memory-summary export -- flag to the operator as an intake ask (paste your own ChatGPT or Claude memory-page text twice, a week apart) and run diff-latest on real data instead of the fixture, which is the only way this stops being feasibility-only evidence; or (b) run a W3 demand/build gate to the same evidence standard as the W1 NO-GO and W2 gates (gates/W3-*.md), scoring distribution (r/ChatGPTPro's 300+ threads per KB-12), the newly-found AgentPrizm/Microsoft adjacency (KB-33) as a competitive section, and H2's still-open willingness-to-pay gap. Do not re-run the same H3/H4 WebSearch sweep again -- that ground is covered; this bet's open surface is now build-and-gate-shaped, not research-shaped. Forecast F-009 opened this run (W3 gate GO/NO-GO, p=0.55, resolves 2026-08-15) -- next run touching W3 should check whether new evidence should move it via tools/beliefs.py, not by hand."}
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

## WORLD_CHANGES — frontier radar (generated, DIRECTIVE 2026-07-17)
```
latest funnel (2026-07-17): Funnel: observed 7 · verified 2 · candidates 7 · roadmap-implications 0 · priority-changes 0
open belief candidates + threats:
- [CAND-2026-07-17-zeroclick] belief-shift (UNVERIFIED): ~68% of Google searches are zero-click in early 2026 (+7.5pp); click-based site monetization is on a
- [CAND-2026-07-17-ai-referral-conv] door (UNVERIFIED): AI-referred sessions convert 6-9x better than Google organic
- [CAND-2026-07-17-mcp-monetization] door (UNVERIFIED): <5% of ~11,000 MCP servers are monetized (pre-monetization App Store moment)
- [CAND-2026-07-17-gate-gaming] threat (UNVERIFIED): ~20% of 'solved' SWE-bench is invalid / reward-hacking generalizes to sabotage
- [CAND-2026-07-17-geo-first-rec] belief-shift (UNVERIFIED): the highest-leverage move this quarter is the GEO/citation pivot on the owned site
- [CAND-2026-07-17-apify-sunset] door (VERIFIED): Apify rental pricing retiring: new rentals blocked 2026-04-01, full sunset 2026-10-01, migration DEF
- [CAND-2026-07-17-youtube-ip] threat (VERIFIED): YouTube: datacenter/VPN IP ranges reputation-flagged Google-wide; PO tokens gating endpoints; reside
```

