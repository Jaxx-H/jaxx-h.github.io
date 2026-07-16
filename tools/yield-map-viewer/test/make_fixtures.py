#!/usr/bin/env python3
"""
make_fixtures.py — deterministic, OBVIOUSLY-SYNTHETIC shapefile fixtures for the
yield-map-viewer tool, plus expected.json ground truth. Python 3 stdlib ONLY.

Everything here is generated from a fixed seed — no real field, no real farm,
no real yield monitor. File names and attribute values (VARIETY "SYN-1, demo")
say so. The page's demo button loads the .zip and labels it synthetic.

expected.json is the independent oracle: Python computes point counts, bbox,
spot coordinates, and DRY_YIELD/MOISTURE statistics; the node test asserts the
in-browser JS parser reproduces them. The JS parser never grades itself.

Run from anywhere:  python3 tools/yield-map-viewer/test/make_fixtures.py
"""
import json
import math
import random
import struct
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FIX = HERE.parent / "fixtures"
FIX.mkdir(exist_ok=True)

rng = random.Random(42)  # fixed seed — fixtures are reproducible byte-for-byte

WGS84_PRJ = (
    'GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",'
    "6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],"
    'UNIT["Degree",0.0174532925199433]]'
)


# ---------------- SHP writing (ESRI shapefile, big+little endian mix) --------
def shp_header(shape_type, bbox, content_bytes):
    file_len_words = (100 + content_bytes) // 2
    h = struct.pack(">i", 9994) + b"\x00" * 20 + struct.pack(">i", file_len_words)
    h += struct.pack("<ii", 1000, shape_type)
    h += struct.pack("<4d", *bbox)          # xmin ymin xmax ymax
    h += struct.pack("<4d", 0.0, 0.0, 0.0, 0.0)  # z/m ranges unused
    return h


def write_point_shp(path, points):
    recs = b""
    for i, (x, y) in enumerate(points, 1):
        content = struct.pack("<i2d", 1, x, y)
        recs += struct.pack(">ii", i, len(content) // 2) + content
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    bbox = (min(xs), min(ys), max(xs), max(ys))
    path.write_bytes(shp_header(1, bbox, len(recs)) + recs)
    return bbox


def write_polygon_shp(path, polygons):
    """polygons: list of rings, each ring a closed list of (x, y)."""
    recs = b""
    for i, ring in enumerate(polygons, 1):
        xs = [p[0] for p in ring]
        ys = [p[1] for p in ring]
        content = struct.pack("<i4d", 5, min(xs), min(ys), max(xs), max(ys))
        content += struct.pack("<ii", 1, len(ring))       # numParts, numPoints
        content += struct.pack("<i", 0)                    # part start index
        for x, y in ring:
            content += struct.pack("<2d", x, y)
        recs += struct.pack(">ii", i, len(content) // 2) + content
    ax = [p[0] for ring in polygons for p in ring]
    ay = [p[1] for ring in polygons for p in ring]
    bbox = (min(ax), min(ay), max(ax), max(ay))
    path.write_bytes(shp_header(5, bbox, len(recs)) + recs)
    return bbox


# ---------------- DBF writing (dBase III) -------------------------------------
def write_dbf(path, fields, rows):
    """fields: [(name, type, length, decimals)]; rows: list of value tuples."""
    n = len(rows)
    header_size = 32 + 32 * len(fields) + 1
    record_size = 1 + sum(f[2] for f in fields)
    h = bytes([0x03, 125, 1, 1]) + struct.pack("<i", n)
    h += struct.pack("<HH", header_size, record_size) + b"\x00" * 20
    for name, ftype, length, dec in fields:
        fd = name.encode("ascii")[:11].ljust(11, b"\x00")
        fd += ftype.encode("ascii") + b"\x00" * 4
        fd += bytes([length, dec]) + b"\x00" * 14
        h += fd
    h += b"\x0d"
    body = b""
    for row in rows:
        rec = b" "
        for (name, ftype, length, dec), val in zip(fields, row):
            if ftype == "N":
                s = f"{val:.{dec}f}" if dec else str(int(val))
                rec += s.rjust(length).encode("ascii")[:length]
            else:  # C
                rec += str(val).ljust(length).encode("ascii")[:length]
        body += rec
    path.write_bytes(h + body + b"\x1a")


# ---------------- point fixture: serpentine harvest passes -------------------
N_PASSES, PTS_PER_PASS = 24, 25
LON0, LON1 = -93.6500, -93.6400   # ~830 m east-west (synthetic Iowa-ish spot)
LAT0, LAT1 = 42.0000, 42.0040     # ~440 m north-south

points, attrs = [], []
for p in range(N_PASSES):
    lat = LAT0 + (LAT1 - LAT0) * p / (N_PASSES - 1)
    lons = [LON0 + (LON1 - LON0) * i / (PTS_PER_PASS - 1) for i in range(PTS_PER_PASS)]
    if p % 2 == 1:
        lons.reverse()
    for i, lon in enumerate(lons):
        fx = (lon - LON0) / (LON1 - LON0)
        fy = (lat - LAT0) / (LAT1 - LAT0)
        base = 150.0 + 45.0 * math.sin(fx * math.pi) + 25.0 * fy
        yld = max(0.0, base + rng.gauss(0, 12.0))
        # end-of-pass turn rows: obviously-synthetic zero yield
        if i == 0 and p % 4 == 0:
            yld = 0.0
        moisture = 15.5 + 2.0 * (1 - fy) + rng.gauss(0, 0.4)
        elev = 285.0 + 8.0 * fx + rng.gauss(0, 0.5)
        variety = "SYN-1, demo" if p < N_PASSES // 2 else "SYN-2 demo"
        points.append((lon, lat))
        attrs.append((round(yld, 2), round(moisture, 2), round(elev, 2), p + 1, variety))

pt_fields = [
    ("DRY_YIELD", "N", 12, 2),
    ("MOISTURE", "N", 8, 2),
    ("ELEV", "N", 10, 2),
    ("PASS_NUM", "N", 6, 0),
    ("VARIETY", "C", 20, 0),
]
pt_bbox = write_point_shp(FIX / "synthetic-yield-points.shp", points)
write_dbf(FIX / "synthetic-yield-points.dbf", pt_fields, attrs)
(FIX / "synthetic-yield-points.prj").write_text(WGS84_PRJ)

# zips: one stored (works even without DecompressionStream), one deflated
for name, method in (("synthetic-yield-points.zip", zipfile.ZIP_STORED),
                     ("synthetic-yield-points-deflate.zip", zipfile.ZIP_DEFLATED)):
    with zipfile.ZipFile(FIX / name, "w", method) as z:
        for ext in ("shp", "dbf", "prj"):
            fn = f"synthetic-yield-points.{ext}"
            zi = zipfile.ZipInfo(fn, date_time=(2026, 1, 1, 0, 0, 0))
            zi.compress_type = method
            z.writestr(zi, (FIX / fn).read_bytes())

# ---------------- polygon fixture: swath rectangles --------------------------
polys, poly_attrs = [], []
for p in range(N_PASSES):
    lat = LAT0 + (LAT1 - LAT0) * p / (N_PASSES - 1)
    half = (LAT1 - LAT0) / (N_PASSES - 1) / 2 * 0.9
    ring = [(LON0, lat - half), (LON1, lat - half), (LON1, lat + half),
            (LON0, lat + half), (LON0, lat - half)]
    polys.append(ring)
    poly_attrs.append((round(140.0 + 3.0 * p + rng.gauss(0, 5.0), 2), p + 1))

poly_fields = [("DRY_YIELD", "N", 12, 2), ("PASS_NUM", "N", 6, 0)]
poly_bbox = write_polygon_shp(FIX / "synthetic-yield-swaths.shp", polys)
write_dbf(FIX / "synthetic-yield-swaths.dbf", poly_fields, poly_attrs)

# ---------------- expected.json: the independent oracle ----------------------
def stats(vals):
    vals = sorted(vals)
    n = len(vals)
    mean = sum(vals) / n
    median = vals[n // 2] if n % 2 else (vals[n // 2 - 1] + vals[n // 2]) / 2
    stdev = math.sqrt(sum((v - mean) ** 2 for v in vals) / n)  # population sd
    return {"count": n, "min": vals[0], "max": vals[-1], "mean": mean,
            "median": median, "stdev": stdev}

ylds = [a[0] for a in attrs]
expected = {
    "points": {
        "count": len(points),
        "bbox": list(pt_bbox),
        "first_xy": list(points[0]),
        "last_xy": list(points[-1]),
        "field_names": [f[0] for f in pt_fields],
        "record_count": len(attrs),
        "first_record": {"DRY_YIELD": attrs[0][0], "MOISTURE": attrs[0][1],
                         "ELEV": attrs[0][2], "PASS_NUM": attrs[0][3],
                         "VARIETY": attrs[0][4]},
        "dry_yield_stats": stats(ylds),
        "dry_yield_zero_count": sum(1 for v in ylds if v == 0.0),
        "moisture_mean": sum(a[1] for a in attrs) / len(attrs),
        "detected_yield_col": "DRY_YIELD",
        "detected_moisture_col": "MOISTURE",
    },
    "swaths": {
        "count": len(polys),
        "bbox": list(poly_bbox),
        "ring_points_each": len(polys[0]),
        "first_ring_first_xy": list(polys[0][0]),
        "dry_yield_mean": sum(a[0] for a in poly_attrs) / len(poly_attrs),
    },
}
(HERE / "expected.json").write_text(json.dumps(expected, indent=1))
print(f"wrote fixtures to {FIX} and ground truth to {HERE / 'expected.json'}")
