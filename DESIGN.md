# DESIGN DOCTRINE — every page/tool the factory ships reads this first

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
