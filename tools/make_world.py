"""Build the embedded world for elsewhere.

Inputs (fetched separately, public domain):
  world110.json            Natural Earth 110m admin-0 countries (GeoJSON)
  Koeppen-Geiger-ASCII.txt Kottek et al. 2006 climate grid, 0.5 deg

Outputs world_data.js:
  WORLD_C     countries: name, continent, quantized delta-encoded rings
  WORLD_COAST resampled ocean-coast points (from edges no two countries share)
  KG_RLE      1-deg Koeppen class raster, run-length encoded row by row
  KG_CLASSES  index -> class string legend
"""
import json, math, os
from collections import Counter

SRC_W = "world110.json"
SRC_K = "Koeppen-Geiger-ASCII.txt"
OUT = "world_data.js"
TOL = 0.12          # Douglas-Peucker tolerance, degrees
MIN_RING = 0.45     # drop rings smaller than this bbox (tiny islands)
Q = 20              # quantize to 0.05 deg
COAST_STEP = 0.65


def dp(points, tol):
    if len(points) < 3:
        return points
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        if b <= a + 1:
            continue
        ax, ay = points[a]; bx, by = points[b]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        dmax, imax = -1.0, -1
        for i in range(a + 1, b):
            px, py = points[i]
            if L2 == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
                d = math.hypot(px - (ax + t * dx), py - (ay + t * dy))
            if d > dmax:
                dmax, imax = d, i
        if dmax > tol:
            keep[imax] = True
            stack.append((a, imax)); stack.append((imax, b))
    return [p for p, k in zip(points, keep) if k]


def rings_of(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    return [poly[0] for poly in geom["coordinates"]]


def main():
    fc = json.load(open(SRC_W))
    countries = []
    all_edges = {}
    for f in fc["features"]:
        p = f["properties"]
        name = p.get("NAME_EN") or p.get("NAME") or p.get("ADMIN")
        cont = p.get("CONTINENT", "")
        if name == "Antarctica":
            continue
        rings = []
        for ring in rings_of(f["geometry"]):
            xs = [q[0] for q in ring]; ys = [q[1] for q in ring]
            if max(xs) - min(xs) < MIN_RING and max(ys) - min(ys) < MIN_RING:
                continue
            for i in range(len(ring) - 1):
                a = (round(ring[i][0], 3), round(ring[i][1], 3))
                b = (round(ring[i + 1][0], 3), round(ring[i + 1][1], 3))
                if a == b:
                    continue
                k = (a, b) if a < b else (b, a)
                all_edges[k] = all_edges.get(k, 0) + 1
            simp = dp([(q[0], q[1]) for q in ring], TOL)
            if len(simp) >= 4:
                rings.append(simp)
        if rings:
            countries.append((name, cont, rings))

    outline = [k for k, c in all_edges.items() if c == 1]
    shared = sum(1 for c in all_edges.values() if c > 1)
    print(f"countries: {len(countries)}, edges {len(all_edges)}, shared {shared}, coast {len(outline)}")

    coast = []
    for (a, b) in outline:
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(d / COAST_STEP))
        for i in range(n + 1):
            u = i / n
            coast.append((a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1])))
    seen, cpts = set(), []
    for x, y in coast:
        k = (round(x * 2), round(y * 2))
        if k not in seen:
            seen.add(k)
            cpts.append((x, y))
    print("coast points:", len(cpts))

    def enc_ring(ring):
        out, px, py = [], 0, 0
        for x, y in ring:
            qx, qy = round(x * Q), round(y * Q)
            out.extend((qx - px, qy - py)); px, py = qx, qy
        return out

    js_c = [{"n": n, "k": c[:2].lower(), "r": [enc_ring(r) for r in rings]}
            for n, c, rings in countries]
    js_coast = []
    for x, y in cpts:
        js_coast.extend((round(x * Q), round(y * Q)))

    # ---- Koeppen 1-deg raster ----
    cells = {}
    with open(SRC_K) as f:
        next(f)
        for line in f:
            p = line.split()
            if len(p) < 3:
                continue
            lat, lon, cls = float(p[0]), float(p[1]), p[2]
            key = (math.floor(lon + 180), math.floor(lat + 90))   # 1-deg bin
            cells.setdefault(key, []).append(cls)
    grid = {}
    for key, lst in cells.items():
        grid[key] = Counter(lst).most_common(1)[0][0]
    classes = sorted({v for v in grid.values()})
    idx = {c: i for i, c in enumerate(classes)}
    print(f"koeppen: {len(grid)} land cells, {len(classes)} classes")

    # RLE rows south->north, lon -180..180; token = char(class) + base36 runlen
    # water = '.'; class chars start at 'A'
    rows = []
    for gy in range(180):
        row = []
        run_c, run_n = None, 0
        for gx in range(360):
            c = grid.get((gx, gy))
            ch = "." if c is None else chr(65 + idx[c])
            if ch == run_c:
                run_n += 1
            else:
                if run_c is not None:
                    row.append(run_c + _b36(run_n))
                run_c, run_n = ch, 1
        row.append(run_c + _b36(run_n))
        rows.append("".join(row))
    rle = "|".join(rows)
    print(f"rle: {len(rle)} bytes")

    with open(OUT, "w") as f:
        f.write("const WORLD_C=" + json.dumps(js_c, separators=(",", ":"))
                + ";\nconst WORLD_COAST=" + json.dumps(js_coast, separators=(",", ":"))
                + ";\nconst KG_CLASSES=" + json.dumps(classes, separators=(",", ":"))
                + ";\nconst KG_RLE=" + json.dumps(rle) + ";\n")
    print(f"wrote {OUT}: {os.path.getsize(OUT)} bytes")


def _b36(n):
    s = ""
    while n:
        s = "0123456789abcdefghijklmnopqrstuvwxyz"[n % 36] + s
        n //= 36
    return s or "0"


if __name__ == "__main__":
    main()
