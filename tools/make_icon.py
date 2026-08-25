"""Render the elsewhere app icon: the globe at dusk, from the app's own data.

Needs pillow + numpy, and the map sources next to it:
  world110.json            Natural Earth 110m countries
  Koeppen-Geiger-ASCII.txt Kottek et al. 2006

Writes icon-512.png, icon-192.png, icon-maskable-512.png,
apple-touch-icon.png into the app root. The view is the Atlantic
hemisphere — Africa, Europe, South America — with the terminator and its
twilight band falling across the middle, the periwinkle halo around the
limb, on the app's near-black.
"""
import json, math, os
from collections import Counter

import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_W = os.path.join(HERE, "world110.json")
SRC_K = os.path.join(HERE, "Koeppen-Geiger-ASCII.txt")
OUT = os.path.join(HERE, "..")

BG = (18, 18, 18)
SEA = (26, 32, 44)
LAND = (36, 39, 44)
HALO = (150, 162, 208)
HUES = {  # koeppen -> biome hue, as in the app
    "trf": "#2e6b4f", "sav": "#9c8a4a", "des": "#ac7a4e", "steppe": "#8a8a72",
    "med": "#93824b", "subtrop": "#6d7f52", "toce": "#55795d", "tfor": "#5c7a52",
    "bor": "#4e7368", "tundra": "#7e8a8a", "ice": "#9fb0bd",
}


def kg_biome(cls):
    if cls in ("Af", "Am"):
        return "trf"
    if cls[0] == "A" or cls == "BSh":
        return "sav"
    if cls == "BWh":
        return "des"
    if cls[0] == "B":
        return "steppe"
    if cls[0] == "C" and cls[1] == "s":
        return "med"
    if cls in ("Cfa", "Cwa"):
        return "subtrop"
    if cls[0] == "C":
        return "toce"
    if cls[0] == "D":
        return "bor" if cls[2] >= "c" else "tfor"
    return "tundra" if cls == "ET" else "ice"


def mix(hue, base, a=0.55):
    r, g, b = (int(hue[i:i + 2], 16) for i in (1, 3, 5))
    return tuple(int(base[i] * (1 - a) + c * a) for i, c in enumerate((r, g, b)))


def equirect(w=2880, h=1440):
    img = Image.new("RGB", (w, h), SEA)
    d = ImageDraw.Draw(img)
    fc = json.load(open(SRC_W))
    X = lambda lon: (lon + 180) / 360 * w
    Y = lambda lat: (90 - lat) / 180 * h
    polys = []
    for f in fc["features"]:
        if f["properties"].get("NAME") == "Antarctica":
            continue
        geom = f["geometry"]
        rings = [geom["coordinates"][0]] if geom["type"] == "Polygon" \
            else [p[0] for p in geom["coordinates"]]
        for ring in rings:
            pts = [(X(p[0]), Y(p[1])) for p in ring]
            if len(pts) >= 3:
                polys.append(pts)
                d.polygon(pts, fill=LAND)
    # koeppen tints at 1 degree, clipped to land by redrawing over a mask
    mask = Image.new("L", (w, h), 0)
    dm = ImageDraw.Draw(mask)
    for pts in polys:
        dm.polygon(pts, fill=255)
    tint = img.copy()
    dt = ImageDraw.Draw(tint)
    cells = {}
    with open(SRC_K) as f:
        next(f)
        for line in f:
            p = line.split()
            if len(p) >= 3:
                key = (math.floor(float(p[1]) + 180), math.floor(float(p[0]) + 90))
                cells.setdefault(key, []).append(p[2])
    for (gx, gy), lst in cells.items():
        cls = Counter(lst).most_common(1)[0][0]
        c = mix(HUES[kg_biome(cls)], LAND)
        x0, y0 = gx / 360 * w, (179 - gy) / 180 * h
        dt.rectangle([x0, y0, x0 + w / 360 + 1, y0 + h / 180 + 1], fill=c)
    img.paste(tint, (0, 0), mask)
    return np.asarray(img, dtype=np.float32)


def globe(tex, size, r_frac, lam0=-20.0, phi0=8.0):
    th, tw = tex.shape[:2]
    c = size / 2
    R = size * r_frac
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    dx = (xx - c) / R
    dy = (c - yy) / R
    d2 = dx * dx + dy * dy
    inside = d2 <= 1.0
    z = np.sqrt(np.clip(1 - d2, 0, 1))
    sp, cp = math.sin(math.radians(phi0)), math.cos(math.radians(phi0))
    sin_lat = np.clip(z * sp + dy * cp, -1, 1)
    lat = np.arcsin(sin_lat)
    lon = math.radians(lam0) + np.arctan2(dx, z * cp - dy * sp)
    tx = ((np.degrees(lon) + 180) / 360 * tw).astype(np.int64) % tw
    ty = np.clip(((90 - np.degrees(lat)) / 180 * th).astype(np.int64), 0, th - 1)
    px = tex[ty, tx]
    # limb + terminator with the twilight band (sun over the west atlantic)
    lam_s = math.radians(lam0 - 40)
    cosz = sin_lat * 0.0 + np.cos(lat) * np.cos(lon - lam_s)
    sh = 0.9 + 0.1 * z
    night = np.where(cosz < -0.09, 0.62,
                     np.where(cosz < 0.05, 0.62 + 0.38 * (cosz + 0.09) / 0.14, 1.0))
    px = np.clip(px * 1.16, 0, 255) * (sh * night)[..., None]
    band = (cosz > -0.22) & (cosz < 0.22)
    tb = np.clip((cosz + 0.22) / 0.44, 0, 1)
    wgt = np.where(band, np.sin(tb * math.pi) * 0.36, 0)
    tw_col = np.stack([150 + 105 * tb, 132 + 62 * tb, 196 - 52 * tb], axis=-1)
    px = px + (tw_col - px) * wgt[..., None]
    # compose over bg with halo
    out = np.zeros((size, size, 3), np.float32)
    out[:] = BG
    d = np.sqrt(d2)
    halo = (d > 1) & (d < 1.15)
    u = np.clip(1 - (d - 1) / 0.15, 0, 1)
    ha = (u * u * 0.5)[..., None]
    out = np.where(halo[..., None], out * (1 - ha) + np.array(HALO) * ha, out)
    out[inside] = px[inside]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


def main():
    tex = equirect()
    globe(tex, 1024, 0.46).resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "icon-512.png"))
    globe(tex, 1024, 0.46).resize((192, 192), Image.LANCZOS).save(os.path.join(OUT, "icon-192.png"))
    globe(tex, 1024, 0.38).resize((512, 512), Image.LANCZOS).save(os.path.join(OUT, "icon-maskable-512.png"))
    globe(tex, 1024, 0.44).resize((180, 180), Image.LANCZOS).save(os.path.join(OUT, "apple-touch-icon.png"))
    print("wrote icon-512 / icon-192 / icon-maskable-512 / apple-touch-icon")


if __name__ == "__main__":
    main()
