# DESIGN DOCTRINE — every page/tool the factory ships reads this first

## HOUSE SKIN — pixel-farm (DEFAULT for every tool/page; operator-locked 2026-07-16)

The operator set a standing house style: a **Stardew-Valley-like pixel-art farm**.
Every new tool/page ships in this skin unless the operator directs a deliberate
break for that page. It is the concrete default expression of the 8 rules below
(where an old rule conflicts — e.g. rule 2's near-black ground — the skin wins
as the default; the rules still govern intent). Reference implementation:
`tools/yield-map-viewer/index.html` — new builds copy its `#farm` renderer and
panel/token CSS rather than reinventing them.

**The scene (ambient, procedural, canvas):** a low-res `<canvas>` buffer scaled
up with `image-rendering: pixelated`, fixed behind the UI
(`position: fixed; inset: 0; z-index: 0; pointer-events: none`) with a
readability scrim above it (z-index 1; content at z-index 2). Dawn/dusk North
Dakota sky as a banded gradient with a low pixel sun, drifting pixel clouds, a
distant pixel tree line, and a receding one-point-perspective tilled field —
converging furrows plus alternating crop stripes. A slow **green X9-class
combine** drives one way; a **red row-crop tractor** drives the other. The scene
is deterministic (no RNG) so every load composes the same.

**Panel chrome (Stardew wood/parchment HUD):** opaque parchment panels with
chunky pixel-bevel borders — a `--frame-dark` border plus layered inset
box-shadows (`--frame-mid` / `--frame-light` / `--frame-shadow`) and a hard
drop shadow. **Sharp corners only — `border-radius` is banned in this skin.**
Uppercase mono labels (`.plabel`: small tracked monospace, gold, with a
gold/green/red pixel-square prefix), pixel checkboxes, and beveled buttons that
press down 2px on `:active`.

**Palette:** harvest gold + Deere-green + tractor-red signature over parchment
browns; light mode = bright dawn field, dark mode = dusk. Token set:
`--sky`, `--panel/-2/-hud`, `--ink/--muted/--faint`, `--frame-dark/mid/light/shadow`,
`--gold/--green/--red`, `--line/--line-strong`, `--hud-coin`. Theme-aware in
BOTH directions: `@media (prefers-color-scheme: dark)` **and** explicit
`:root[data-theme="light"]` / `:root[data-theme="dark"]` override blocks; JS
renderers resolve theme via `effectiveTheme()` (data-theme attribute wins, OS
scheme is the fallback) and observe both. Per-tool DATA palettes stay
subject-native and validator-passed (e.g. the yield tool's 5-class
harvest-gold ramp) — the skin themes the chrome, never the data encoding.

**TRADEMARK-SAFE (non-negotiable):** evocative pixel art ONLY — a GENERIC green
combine and a GENERIC red tractor. No John Deere or Case logos, wordmarks,
model numbers as branding, or trade dress. Naming real products in factual
prose (file formats, export menu paths) is fine; drawing their marks is not.

**Behavior contract:** self-contained (procedural canvas or data-URIs; zero
external requests beyond the site's analytics snippet — the tool oracle in
`check_site.py` enforces this). `prefers-reduced-motion: reduce` renders ONE
static frame and never starts a rAF loop; the loop pauses on tab-hidden and
resumes on visible; resize relayouts (debounced). The farm is a pure background:
it must never intercept pointer events or affect the tool's interactive layers.

---

**Operator art direction (2026-07-16, binding taste input):** "sites all look same and lame —
they should be themed like they are, and gamified and simplified to be unique and cool."
Reference aesthetic to borrow from (operator's sister's 3D art site, tylarframe.com — borrow
the *interest*, not the artsiness, and adapt per niche):

## What the reference actually does (read from its source, 2026-07-16)

- **Stark near-black ground** (`#19191a`) with pure white/black contrast — the canvas recedes,
  the artwork carries everything.
- **Full-bleed dimensional art as the surface**: her "3D aesthetic" is rendered artwork used as
  cover-positioned background layers (26 full-bleed panels on one page) — depth comes from the
  IMAGERY, not CSS tricks.
- **Bold display type, tiny type system**: Fjalla One (condensed display) + Montserrat/Lato,
  and almost nothing else. Minimal nav, few words.
- **Entrance motion** (animate.css-class reveals) — elements arrive, they don't just exist.
- Built on canvas-heavy rendering (193 canvas nodes) — the page IS a composition, not a document.

## Translation rules for OUR pages/tools (adapt per niche, never carbon-copy)

1. **The data is the artwork.** We already render canvas (yield maps, calibration charts).
   Elevate those renders to full-bleed, dimensional hero surfaces — lighting, depth,
   texture — instead of small widgets in a white page. A yield map should feel like terrain;
   a calibration chart like an instrument.
2. **Dark dimensional ground by default** (near-black `#19191a`-family, never pure `#000`),
   ONE subject-native accent per tool (harvest gold, forecast teal…), white space as drama.
3. **One condensed display face** for the tool's name/moment + one quiet body face. Few words.
4. **Depth cues without WebGL bloat**: layered shadows, subtle parallax on the hero canvas,
   extruded/inset type for titles — CSS + canvas only; keep the zero-external-request law.
5. **Entrance moments**: the parse/result "paints in" (staged reveal), respecting
   `prefers-reduced-motion`.
6. **One light gamified mechanic per tool** (collectible card, score, badge, shareable image) —
   never fake data, never dark patterns.
7. **Simplify to cool**: fewer controls visible, defaults do the work, advanced behind a fold.
8. Niche-appropriate: a farmer tool can be handsome AND rugged; an ag page doesn't need art-house,
   it needs *character*. Borrow the interest level, not the gallery vibe.

Hard constraints unchanged: single-file tools, zero external requests (fonts inlined or system
stacks), PII gate, honest copy, light+dark both considered (a deliberate single-theme is allowed
when the design commits to it).
