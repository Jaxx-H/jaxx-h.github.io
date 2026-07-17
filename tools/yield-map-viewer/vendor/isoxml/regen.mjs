#!/usr/bin/env node
// Regenerate the vendored ISOXML TimeLog parser bundle. Reproducible, not hand-pruned.
//   node regen.mjs      -> writes isoxml-timelog.bundle.mjs
// Pins upstream by npm version (immutable). Bump PIN + re-run to update; commit the diff.
import { execSync } from 'node:child_process';
import { mkdtempSync, writeFileSync, readFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
const HERE = dirname(fileURLToPath(import.meta.url));
const PIN = '1.11.2';                         // dev4Agriculture/isoxml-js, Apache-2.0
const work = mkdtempSync(join(tmpdir(), 'isoxml-regen-'));
execSync(`npm init -y`, { cwd: work, stdio: 'ignore' });
execSync(`npm install isoxml@${PIN} esbuild`, { cwd: work, stdio: 'inherit' });
writeFileSync(join(work, 'entry.mjs'), `export { ISOXMLManager } from 'isoxml';\n`);
const banner = `/*! Vendored from isoxml@${PIN} (dev4Agriculture/isoxml-js), Apache-2.0.\n` +
  ` * Only the TimeLog parse path is used by yield-map-viewer. Full license: ./LICENSE, attribution: ./NOTICE.\n` +
  ` * DO NOT EDIT BY HAND — regenerate with: node vendor/isoxml/regen.mjs */`;
execSync(`node_modules/.bin/esbuild entry.mjs --bundle --format=esm --platform=browser --minify ` +
  `--banner:js=${JSON.stringify(banner)} --outfile=${JSON.stringify(join(HERE, 'isoxml-timelog.bundle.mjs'))}`,
  { cwd: work, stdio: 'inherit' });
console.log('vendored bundle regenerated from isoxml@' + PIN);
