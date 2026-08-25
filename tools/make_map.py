"""Build compact embedded map data for elsewhere from us-states.json.

Outputs map_data.js: quantized, delta-encoded state polygons (drawing +
point-in-state) and a classified coastline (pacific / atlantic-gulf / great
lakes) resampled to ~0.12 deg for distance-to-coast queries.
"""
import json, math

SRC = "us-states.json"
OUT = "map_data.js"
SKIP = {"Alaska", "Hawaii", "Puerto Rico"}
TOL = 0.035          # Douglas-Peucker tolerance, degrees
MIN_RING = 0.05      # drop rings with bbox smaller than this (tiny islands)
Q = 100              # quantize to 0.01 deg
COAST_STEP = 0.12    # resample coast every ~0.12 deg


def dp(points, tol):
    """Douglas-Peucker on [(x,y)] (keeps first/last)."""
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


# ---- coast classification rules (rough boxes; only flavor, not precision) --
def coast_type(lon, lat):
    """'p' pacific, 'a' atlantic, 'g' gulf, 'l' great lakes, None = land border."""
    # canada land border (west + the 45th parallel-ish east chunk)
    if lat > 48.9 and -124.8 < lon < -88:
        return None
    # great lakes boxes
    for lo1, la1, lo2, la2 in ((-92.3, 46.3, -84.2, 49.0),   # superior
                               (-88.1, 41.5, -84.6, 46.3),   # michigan
                               (-84.9, 43.0, -82.3, 46.3),   # huron
                               (-83.6, 41.2, -78.8, 43.0),   # erie + st clair
                               (-79.9, 43.1, -76.0, 44.4)):  # ontario
        if lo1 <= lon <= lo2 and la1 <= lat <= la2:
            return "l"
    if lon <= -116.9 and lat < 49.1:
        return "p"
    # mexico land border
    if lat < 32.8 and -117 < lon < -97.6:
        return None
    # canada east (NY/VT/NH/ME north borders)
    if lat > 45.15 and lon > -77:
        return None
    # gulf of mexico
    if lat < 31.2 and -97.7 < lon < -80.6:
        # florida split: peninsula west side is gulf
        if lon > -82.0 and not (lat > 25.2 and lon < -80.9):
            return "a"
        return "g"
    # atlantic seaboard
    if lon > -81.8 and lat < 45.15:
        return "a"
    return None


def main():
    fc = json.load(open(SRC))
    states = []
    all_edges = {}
    for f in fc["features"]:
        name = f["properties"]["name"]
        if name in SKIP:
            continue
        rings = []
        for ring in rings_of(f["geometry"]):
            xs = [p[0] for p in ring]; ys = [p[1] for p in ring]
            if max(xs) - min(xs) < MIN_RING and max(ys) - min(ys) < MIN_RING:
                continue
            # collect full-res edges for the union-outline (before simplify)
            for i in range(len(ring) - 1):
                a = (round(ring[i][0], 4), round(ring[i][1], 4))
                b = (round(ring[i + 1][0], 4), round(ring[i + 1][1], 4))
                if a == b:
                    continue
                k = (a, b) if a < b else (b, a)
                all_edges[k] = all_edges.get(k, 0) + 1
            simp = dp([(p[0], p[1]) for p in ring], TOL)
            if len(simp) >= 4:
                rings.append(simp)
        if rings:
            states.append((name, rings))

    # outline = edges used once (not shared between two states)
    outline = [k for k, c in all_edges.items() if c == 1]
    shared = sum(1 for c in all_edges.values() if c > 1)
    print(f"edges: {len(all_edges)} total, {shared} shared, {len(outline)} outline")

    # classified coast points, resampled along outline edges
    coast = []
    for (a, b) in outline:
        t = coast_type(*a) or coast_type(*b)
        if not t:
            continue
        d = math.hypot(b[0] - a[0], b[1] - a[1])
        n = max(1, int(d / COAST_STEP))
        for i in range(n + 1):
            u = i / n
            coast.append((a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1]), t))
    # dedupe on quantized grid
    seen, cpts = set(), []
    for x, y, t in coast:
        k = (round(x * 8), round(y * 8), t)
        if k not in seen:
            seen.add(k)
            cpts.append((x, y, t))
    from collections import Counter
    print("coast points:", len(cpts), Counter(t for _, _, t in cpts))

    # ---- emit: delta-encoded quantized ints ----
    def enc_ring(ring):
        out, px, py = [], 0, 0
        for x, y in ring:
            qx, qy = round(x * Q), round(y * Q)
            out.extend((qx - px, qy - py)); px, py = qx, qy
        return out

    js_states = [{"n": name, "r": [enc_ring(r) for r in rings]}
                 for name, rings in states]
    js_coast = {"p": [], "a": [], "g": [], "l": []}
    for x, y, t in cpts:
        js_coast[t].extend((round(x * Q), round(y * Q)))

    npts = sum(len(r) // 2 for s in js_states for r in s["r"])
    print(f"states: {len(js_states)}, polygon points: {npts}")
    with open(OUT, "w") as f:
        f.write("const MAP_STATES=" + json.dumps(js_states, separators=(",", ":"))
                + ";\nconst MAP_COAST=" + json.dumps(js_coast, separators=(",", ":"))
                + ";\n")
    import os
    print(f"wrote {OUT}: {os.path.getsize(OUT)} bytes")


if __name__ == "__main__":
    main()
