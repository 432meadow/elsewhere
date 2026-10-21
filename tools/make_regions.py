"""Build the world's regions for elsewhere: names only, never drawn.

Input (fetched separately, public domain):
  admin1.geojson   Natural Earth 10m admin-1 states & provinces

Output regions_data.js:
  WORLD_RN   region names, index 0 = none
  WORLD_RG   quarter-degree raster of region indices, rows south->north,
             lon -180..180, run-length encoded: base36 index '.' base36 run,
             runs joined by ',', rows by '|'
"""
import json, os, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "admin1.geojson"
OUT = "regions_data.js"
STEP = 0.25
W, H = int(360 / STEP), int(180 / STEP)


def b36(n):
    s = ""
    while n:
        s = "0123456789abcdefghijklmnopqrstuvwxyz"[n % 36] + s
        n //= 36
    return s or "0"


def polys_of(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"]]
    return geom["coordinates"]


def main():
    fc = json.load(open(SRC))
    names, grid = [""], [0] * (W * H)
    lone = []   # regions too small to own a cell centre: placed afterwards
    feats = sorted(fc["features"], key=lambda f: -area_hint(f["geometry"]))
    for f in feats:
        p = f["properties"]
        name = (p.get("name") or p.get("name_en") or "").strip()
        if not name:
            continue
        idx = len(names); names.append(name)
        hit = False
        for poly in polys_of(f["geometry"]):
            rows = {}
            for ring in poly:   # outer + holes, even-odd per polygon
                for i in range(len(ring) - 1):
                    (x0, y0), (x1, y1) = ring[i][:2], ring[i + 1][:2]
                    if y0 == y1:
                        continue
                    lo, hi = min(y0, y1), max(y0, y1)
                    r0 = max(0, int((lo + 90) / STEP - 0.5) )
                    r1 = min(H - 1, int((hi + 90) / STEP + 0.5))
                    for r in range(r0, r1 + 1):
                        yc = -90 + (r + 0.5) * STEP
                        if (y0 > yc) != (y1 > yc):
                            rows.setdefault(r, []).append(x0 + (yc - y0) * (x1 - x0) / (y1 - y0))
            for r, xs in rows.items():
                xs.sort()
                for a, b in zip(xs[0::2], xs[1::2]):
                    c0 = max(0, int((a + 180) / STEP - 0.5 + 0.999999))
                    c1 = min(W - 1, int((b + 180) / STEP - 0.5))
                    for c in range(c0, c1 + 1):
                        grid[r * W + c] = idx; hit = True
        if not hit:
            lone.append((idx, f["geometry"]))
    for idx, geom in lone:
        pts = [q for poly in polys_of(geom) for q in poly[0]]
        x = sum(q[0] for q in pts) / len(pts); y = sum(q[1] for q in pts) / len(pts)
        c = min(W - 1, int((x + 180) / STEP)); r = min(H - 1, int((y + 90) / STEP))
        if not grid[r * W + c]:
            grid[r * W + c] = idx

    used = sorted(set(grid) - {0})
    remap = {old: i + 1 for i, old in enumerate(used)}
    out_names = [""] + [names[o] for o in used]
    rows = []
    for r in range(H):
        runs, cur, n = [], None, 0
        for c in range(W):
            v = remap.get(grid[r * W + c], 0)
            if v == cur:
                n += 1
            else:
                if cur is not None:
                    runs.append(b36(cur) + "." + b36(n))
                cur, n = v, 1
        runs.append(b36(cur) + "." + b36(n))
        rows.append(",".join(runs))
    rle = "|".join(rows)
    with open(OUT, "w") as f:
        f.write("const WORLD_RN=" + json.dumps(out_names, ensure_ascii=False, separators=(",", ":"))
                + ";\nconst WORLD_RG=" + json.dumps(rle) + ";\n")
    print(f"regions: {len(out_names) - 1} of {len(names) - 1}, rle {len(rle)} bytes, "
          f"wrote {OUT}: {os.path.getsize(OUT)} bytes")


def area_hint(geom):
    """bbox area, so small regions are filled last and win their cells"""
    xs = [q[0] for poly in polys_of(geom) for q in poly[0]]
    ys = [q[1] for poly in polys_of(geom) for q in poly[0]]
    return (max(xs) - min(xs)) * (max(ys) - min(ys))


if __name__ == "__main__":
    main()
