#!/usr/bin/env node
/**
 * run_tests.mjs — zero-dependency test for the yield-map-viewer parser core.
 *
 * Extracts the <script id="ymv-core"> block VERBATIM from ../index.html (so the
 * exact shipped code is what gets tested — no copy can drift) and asserts it
 * reproduces test/expected.json, which make_fixtures.py computed independently
 * in Python. Run:  node tools/yield-map-viewer/test/run_tests.mjs
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HERE = dirname(fileURLToPath(import.meta.url));
const FIX = join(HERE, "..", "fixtures");
const html = readFileSync(join(HERE, "..", "index.html"), "utf8");

const m = html.match(/<script id="ymv-core">([\s\S]*?)<\/script>/);
if (!m) { console.error("FAIL: could not extract ymv-core script from index.html"); process.exit(1); }
// run the shipped code in this realm (Node has TextDecoder/Blob/Response/DecompressionStream)
const YMV = new Function(m[1] + "\n;return YMV;")();

const expected = JSON.parse(readFileSync(join(HERE, "expected.json"), "utf8"));
const read = (name) => new Uint8Array(readFileSync(join(FIX, name)));

let passed = 0, failed = 0;
function check(name, cond, detail) {
  if (cond) { passed++; console.log("  ok  " + name); }
  else { failed++; console.error("  FAIL " + name + (detail ? " — " + detail : "")); }
}
const close = (a, b, tol = 1e-6) => Math.abs(a - b) <= tol;

// ---------- 1. zip reading: stored + deflated ----------
console.log("zip:");
for (const [zipName, label] of [["synthetic-yield-points.zip", "stored"],
                                ["synthetic-yield-points-deflate.zip", "deflated"]]) {
  const entries = await YMV.readZipEntries(read(zipName));
  const names = entries.map((e) => e.name).sort();
  check(`${label} zip lists shp+dbf+prj`,
        JSON.stringify(names) === JSON.stringify(["synthetic-yield-points.dbf",
          "synthetic-yield-points.prj", "synthetic-yield-points.shp"]), names.join(","));
  const shpEntry = entries.find((e) => e.name.endsWith(".shp"));
  check(`${label} zip shp bytes match loose file`,
        Buffer.compare(Buffer.from(shpEntry.data), Buffer.from(read("synthetic-yield-points.shp"))) === 0);
}

// ---------- 2. SHP points ----------
console.log("shp (points):");
const E = expected.points;
const shp = YMV.parseShp(read("synthetic-yield-points.shp"));
check("point count", shp.counts.points === E.count, `${shp.counts.points} != ${E.count}`);
check("bbox", shp.bbox.every((v, i) => close(v, E.bbox[i], 1e-9)), JSON.stringify(shp.bbox));
check("first point xy", close(shp.geoms[0].x, E.first_xy[0], 1e-9) && close(shp.geoms[0].y, E.first_xy[1], 1e-9));
const lastG = shp.geoms[shp.geoms.length - 1];
check("last point xy", close(lastG.x, E.last_xy[0], 1e-9) && close(lastG.y, E.last_xy[1], 1e-9));

// ---------- 3. DBF ----------
console.log("dbf:");
const dbf = YMV.parseDbf(read("synthetic-yield-points.dbf"));
check("field names", JSON.stringify(dbf.fields.map((f) => f.name)) === JSON.stringify(E.field_names),
      dbf.fields.map((f) => f.name).join(","));
check("record count", dbf.records.length === E.record_count, `${dbf.records.length}`);
const r0 = dbf.records[0], fr = E.first_record;
check("first record numerics", close(r0.DRY_YIELD, fr.DRY_YIELD) && close(r0.MOISTURE, fr.MOISTURE) &&
      close(r0.ELEV, fr.ELEV) && r0.PASS_NUM === fr.PASS_NUM,
      JSON.stringify(r0));
check("first record string with comma survives", r0.VARIETY === fr.VARIETY, JSON.stringify(r0.VARIETY));

// ---------- 4. column detection ----------
console.log("column detection:");
check("yield column", YMV.detectYieldColumn(dbf.fields, dbf.records) === E.detected_yield_col);
check("moisture column", YMV.detectMoistureColumn(dbf.fields, dbf.records) === E.detected_moisture_col);
check("numeric fields exclude VARIETY",
      !YMV.numericFieldNames(dbf.fields, dbf.records).includes("VARIETY"));

// ---------- 5. stats vs Python oracle ----------
console.log("stats (vs Python-computed ground truth):");
const ylds = dbf.records.map((r) => r.DRY_YIELD);
const s = YMV.computeStats(ylds);
const T = E.dry_yield_stats;
check("count", s.count === T.count);
check("min", close(s.min, T.min));
check("max", close(s.max, T.max));
check("mean", close(s.mean, T.mean), `${s.mean} != ${T.mean}`);
check("median", close(s.median, T.median), `${s.median} != ${T.median}`);
check("stdev (population)", close(s.stdev, T.stdev), `${s.stdev} != ${T.stdev}`);
check("zero count", ylds.filter((v) => v === 0).length === E.dry_yield_zero_count);
const ms = YMV.computeStats(dbf.records.map((r) => r.MOISTURE));
check("moisture mean", close(ms.mean, E.moisture_mean), `${ms.mean}`);

// ---------- 6. classes ----------
console.log("classification:");
const finite = ylds.filter((v) => typeof v === "number" && isFinite(v));
const breaks = YMV.quantileBreaks(finite, 5);
check("4 quantile breaks", breaks.length === 4, String(breaks.length));
check("breaks ascend", breaks.every((b, i) => i === 0 || b > breaks[i - 1]));
const classCounts = [0, 0, 0, 0, 0];
for (const v of finite) classCounts[YMV.classify(v, breaks)]++;
check("all 5 classes populated", classCounts.every((c) => c > 0), classCounts.join(","));
check("class counts sum to n", classCounts.reduce((a, b) => a + b, 0) === finite.length);

// ---------- 7. CSV ----------
console.log("csv:");
const csv = YMV.buildCsv(dbf.fields.map((f) => f.name), dbf.records, shp.geoms);
const lines = csv.trimEnd().split("\r\n");
check("header row", lines[0] === "X,Y," + E.field_names.join(","), lines[0]);
check("row count = points + header", lines.length === E.count + 1, String(lines.length));
check("comma-bearing value is quoted", lines[1].includes('"SYN-1, demo"'), lines[1]);
check("first row coordinates", lines[1].startsWith(E.first_xy[0] + "," + E.first_xy[1] + ","), lines[1]);

// ---------- 8. polygons ----------
console.log("shp (polygons):");
const EP = expected.swaths;
const pshp = YMV.parseShp(read("synthetic-yield-swaths.shp"));
check("polygon count", pshp.counts.polys === EP.count, String(pshp.counts.polys));
check("bbox", pshp.bbox.every((v, i) => close(v, EP.bbox[i], 1e-9)));
check("ring point count", pshp.geoms[0].rings[0].length === EP.ring_points_each);
check("first ring first xy", close(pshp.geoms[0].rings[0][0][0], EP.first_ring_first_xy[0], 1e-9) &&
      close(pshp.geoms[0].rings[0][0][1], EP.first_ring_first_xy[1], 1e-9));
const pdbf = YMV.parseDbf(read("synthetic-yield-swaths.dbf"));
const pStats = YMV.computeStats(pdbf.records.map((r) => r.DRY_YIELD));
check("swath yield mean", close(pStats.mean, EP.dry_yield_mean), `${pStats.mean}`);

// ---------- 9. coordinates & units ----------
console.log("coordinates/units:");
const prjText = new TextDecoder().decode(read("synthetic-yield-points.prj"));
check("lonlat detected", YMV.looksLikeLonLat(shp.bbox) === true);
check("prj says degrees", YMV.prjUnits(prjText, shp.bbox) === "degree");
const acres = YMV.extentAcres(shp.bbox, "degree");
// synthetic field is ~830m x ~440m ≈ 90 ac; assert the approximation is sane
check("extent acres in sane range (60-130)", acres > 60 && acres < 130, String(acres));

// ---------- 10. garbage in -> clear errors ----------
console.log("error handling:");
const throws = (fn) => { try { fn(); return false; } catch (e) { return /shapefile|\.dbf|zip/i.test(e.message); } };
check("garbage shp throws friendly error", throws(() => YMV.parseShp(new Uint8Array(200))));
check("tiny dbf throws friendly error", throws(() => YMV.parseDbf(new Uint8Array(4))));
const zipThrew = await YMV.readZipEntries(new Uint8Array(500)).then(() => false, (e) => /zip/i.test(e.message));
check("garbage zip rejects with friendly error", zipThrew);

// ---------- 11. zip robustness: nested folders, __MACOSX, multi-set, zip-in-zip ----------
console.log("zip robustness:");
const asDrop = (name) => [{ name, data: read(name) }];

const nestedPool = await YMV.gatherFiles(asDrop("synthetic-nested.zip"));
const nestedSets = YMV.findShapefileSets(nestedPool);
check("nested-folder zip yields one set", nestedSets.length === 1, String(nestedSets.length));
check("nested set path keeps folders", /^JD-Data\/North 40 demo\/Harvest-2026\//.test(nestedSets[0].path), nestedSets[0].path);
check("nested set has dbf+prj mates", !!nestedSets[0].dbf && !!nestedSets[0].prj);
check("nested shp parses to full point count",
      YMV.parseShp(nestedSets[0].shp.data).counts.points === E.count);

const macPool = await YMV.gatherFiles(asDrop("synthetic-macosx.zip"));
const macSets = YMV.findShapefileSets(macPool);
check("__MACOSX noise ignored: exactly one set", macSets.length === 1, macSets.map((s) => s.path).join(";"));
check("the set is the real shp, not AppleDouble junk", !/__MACOSX|\._/.test(macSets[0].path), macSets[0].path);
check("macosx-zip shp parses to full point count",
      YMV.parseShp(macSets[0].shp.data).counts.points === E.count);
check("junk entries flagged in inventory", YMV.inventory(macPool).some((i) => i.junk));
check("isJunkPath catches __MACOSX, ._, .DS_Store",
      YMV.isJunkPath("__MACOSX/._a.shp") && YMV.isJunkPath("x/.DS_Store") &&
      YMV.isJunkPath("._loose.shp") && !YMV.isJunkPath("fields/a.shp"));

const multiPool = await YMV.gatherFiles(asDrop("synthetic-multi.zip"));
const multiSets = YMV.findShapefileSets(multiPool);
check("multi zip finds both sets", multiSets.length === 2, String(multiSets.length));
check("multi sets carry distinct nested paths",
      multiSets[0].path !== multiSets[1].path && multiSets.every((s) => s.path.includes("/")));
const multiParsed = multiSets.map((s) => YMV.parseShp(s.shp.data).counts);
check("multi sets parse: one points layer + one polygon layer",
      multiParsed.some((c) => c.points === E.count) && multiParsed.some((c) => c.polys === EP.count),
      JSON.stringify(multiParsed));
check("each multi set found its own .dbf mate", multiSets.every((s) => !!s.dbf));

const zzPool = await YMV.gatherFiles(asDrop("synthetic-zip-in-zip.zip"));
const zzSets = YMV.findShapefileSets(zzPool);
check("zip-in-zip recursed down to the shapefile",
      zzSets.length === 1 && YMV.parseShp(zzSets[0].shp.data).counts.points === E.count,
      zzSets.map((s) => s.path).join(";"));

// ---------- 12. non-shapefile detection (.jdl and friends) ----------
console.log("monitor-native detection:");
const jdlBytes = read("synthetic-fake.jdl");
const kJdl = YMV.sniffKind("synthetic-fake.jdl", jdlBytes);
check("jdl flagged monitor-native", kJdl.kind === "monitor", kJdl.kind);
check("jdl label names John Deere honestly", /John Deere/.test(kJdl.label) && /no public spec/.test(kJdl.label), kJdl.label);
check("zip sniffed by magic despite wrong name",
      YMV.sniffKind("mystery.bin", read("synthetic-yield-points.zip")).kind === "zip");
check("shp sniffed by magic despite wrong name",
      YMV.sniffKind("mystery.bin", read("synthetic-yield-points.shp")).kind === "shp");
check("dbf sniffed", YMV.sniffKind("synthetic-yield-points.dbf", read("synthetic-yield-points.dbf")).kind === "dbf");
const jdPool = await YMV.gatherFiles(asDrop("synthetic-jd-data.zip"));
check("JD-Data zip of jdl logs: zero shapefile sets", YMV.findShapefileSets(jdPool).length === 0);
const jdInv = YMV.inventory(jdPool);
check("JD-Data zip inventory spots the jdl logs", jdInv.filter((i) => i.kind === "monitor").length === 2,
      JSON.stringify(jdInv.map((i) => i.kind)));
check("inventory reports paths and sizes for diagnostics",
      jdInv.every((i) => i.path.startsWith("JD-Data/") && i.bytes > 0));

// ---------- 13. JD-specific yield column names ----------
console.log("JD column names:");
const fieldsOf = (names) => names.map((n) => ({ name: n, type: "N", length: 10, decimals: 2 }));
const recsOf = (names) => [Object.fromEntries(names.map((n) => [n, 1.5]))];
const det = (names) => YMV.detectYieldColumn(fieldsOf(names), recsOf(names));
check("Yld_Vol_Dr detected", det(["Obj__Id", "Yld_Vol_Dr", "Moisture__"]) === "Yld_Vol_Dr");
check("Yld_Mass_D (10-char truncation) detected", det(["Obj__Id", "Yld_Mass_D"]) === "Yld_Mass_D");
check("VRYIELDVOL detected", det(["VRYIELDVOL", "VRMOISTURE"]) === "VRYIELDVOL");
check("dry beats wet", det(["Yld_Vol_We", "Yld_Vol_Dr"]) === "Yld_Vol_Dr");
check("wet-only export falls back to the wet column", det(["Obj__Id", "Yld_Vol_We"]) === "Yld_Vol_We");
check("moisture never picked as yield", det(["Moisture__", "Elevation_"]) === null);

console.log(`\n${passed} passed, ${failed} failed`);
process.exit(failed ? 1 : 0);
