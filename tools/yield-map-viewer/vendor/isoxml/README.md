# Vendored ISOXML TimeLog parser

`isoxml-timelog.bundle.mjs` — a bundled build of `isoxml` (Apache-2.0), used client-side to
decode ISOXML `TLG*.BIN` binary timelogs (yield points) in yield-map-viewer.

- **Regenerate (never hand-edit):** `node regen.mjs` — pins `isoxml@1.11.2`, bundles with esbuild.
- **Size:** ~762 KB minified (~200 KB gzipped); lazy-loaded on file drop, not on initial tool load.
- **License:** Apache-2.0 (`LICENSE`), attribution in `NOTICE`. Bundle carries an SPDX banner.
- **Why bundled, not tree-shaken further:** `@turf/turf` (partfield geometry, unused by TLG parse)
  tree-shakes to an acceptable size inside the minified bundle; a fragile turf-stub build was
  rejected. Revisit only if the gzipped bundle becomes a load problem.
