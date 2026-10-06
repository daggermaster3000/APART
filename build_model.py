"""Build a to-scale 3D model of apartment L08.02 (Lemgrubenstrasse 8, ground floor)
from the vector floor plan in source/floorplan_L08.02.pdf.

Walls and room floors are read directly from the PDF's vector paths; openings,
fixtures and terraces are placed from coordinates measured on the same plan.
Scale comes from the plan's own 0-10 m scale bar.

Outputs (in model/):
  apartment.glb   - glTF binary, metres, Y up
  apartment.obj   - Wavefront OBJ (+ .mtl), metres, Y up
  apartment.json  - room list with plan areas vs. measured areas
and index.html (self-contained three.js viewer with the model embedded).

Coordinate system: x = east-west across the page (page right = +x),
z = page down (+z), y = up. Origin = scale-bar "0" tick / top of wall line.
North on the plan points to page-left (-x).
"""
import base64
import json
import pathlib

import numpy as np
import pymupdf
import shapely
import trimesh
from shapely.geometry import Polygon, box
from shapely.ops import unary_union

ROOT = pathlib.Path(__file__).parent
PDF = ROOT / "source" / "floorplan_L08.02.pdf"
OUT = ROOT / "model"

# --- scale: scale bar runs from x=144.32pt ("0") to x=299.98pt ("10m") -------
PT_PER_M = (299.98 - 144.32) / 10.0  # 15.566 pt per metre
X0, Y0 = 144.32, 257.75  # plan origin in PDF points

WALL_H = 2.50   # clear room height (assumed; typical Swiss new build)
SLAB = 0.25     # floor slab thickness under the apartment
DOOR_H = 2.10   # door head height
GLAZE_H = 2.30  # head height of full-height glazing
SILL_H = 0.90   # window sill height (assumed)


def m(x, y):
    return ((x - X0) / PT_PER_M, (y - Y0) / PT_PER_M)


def mbox(x0, y0, x1, y1):
    a, b = m(x0, y0)
    c, d = m(x1, y1)
    return box(a, b, c, d)


# --- read vector paths ------------------------------------------------------
doc = pymupdf.open(PDF)
page = doc[0]
drawings = page.get_drawings()
# Raster used to keep only paths that are actually visible (the PDF contains
# other apartments' geometry hidden behind clip paths / white overpaint).
DPI = 600
pix = page.get_pixmap(dpi=DPI)
img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[..., :3]


def rendered_rgb(x, y):
    s = DPI / 72.0
    return img[int(y * s), int(x * s)].astype(float) / 255.0


def path_polys(d):
    """Turn a PyMuPDF drawing into a list of shapely polygons (one per subpath)."""
    polys, cur = [], []
    for it in d["items"]:
        if it[0] == "re":
            r = it[1]
            polys.append(box(r.x0, r.y0, r.x1, r.y1))
        elif it[0] == "qu":
            q = it[1]
            polys.append(Polygon([(p.x, p.y) for p in (q.ul, q.ur, q.lr, q.ll)]))
        elif it[0] in ("l", "c"):
            a, b = it[1], it[-1]
            if cur and (abs(cur[-1][0] - a.x) > 0.01 or abs(cur[-1][1] - a.y) > 0.01):
                polys.append(Polygon(cur)) if len(cur) >= 3 else None
                cur = []
            if not cur:
                cur.append((a.x, a.y))
            cur.append((b.x, b.y))
    if len(cur) >= 3:
        polys.append(Polygon(cur))
    return [p.buffer(0) for p in polys if p.is_valid or p.buffer(0).area > 0]


def visible(poly, rgb):
    """True if most of the polygon renders in its own fill colour (labels and
    fixtures drawn on top of a room fill only cover a small fraction)."""
    minx, miny, maxx, maxy = poly.bounds
    pts = [shapely.Point(x, y) for x in np.linspace(minx, maxx, 9)[1:-1]
           for y in np.linspace(miny, maxy, 9)[1:-1]]
    pts = [p for p in pts if poly.contains(p)] or [poly.representative_point()]
    hits = sum(np.abs(rendered_rgb(p.x, p.y) - np.array(rgb)).max() < 0.08 for p in pts)
    return hits >= 0.5 * len(pts)


BLACK = (0.0, 0.0, 0.0)
ROOMBLUE = (0.698, 0.757, 0.801)
wall_parts, floor_parts = [], []
PLAN_AREA = box(140, 255, 390, 470)
ELEVATOR_ICON = box(181, 356, 205, 390)  # wheelchair pictogram inside the lift
for d in drawings:
    if d["type"] != "f" or d["fill"] is None:
        continue
    fill = tuple(d["fill"])
    for poly in path_polys(d):
        if poly.is_empty or not PLAN_AREA.contains(poly):
            continue
        if np.allclose(fill, BLACK) and poly.area > 0.5 and not ELEVATOR_ICON.contains(poly) and visible(poly, BLACK):
            wall_parts.append(poly)
        elif np.allclose(fill, ROOMBLUE, atol=0.01) and poly.area > 20 and visible(poly, ROOMBLUE):
            floor_parts.append(poly)


def to_m(poly):
    return shapely.transform(poly, lambda c: np.column_stack(m(c[:, 0], c[:, 1])))


walls = to_m(unary_union(wall_parts).buffer(0.01).buffer(-0.01))
floors = to_m(unary_union(floor_parts).buffer(0.005).buffer(-0.005))

# --- rooms: split the blue floor by label position --------------------------
LABELS = {  # plan label -> (stated area BF m², label position in pt)
    "Zimmer 1": (16.0, (238, 300)),
    "Zimmer 2": (12.4, (292, 300)),
    "Korridor": (10.1, (260, 341)),
    "Bad": (4.3, (232, 372)),
    "Reduit": (3.3, (298, 377)),
    "Wohnen / Essen": (47.9, (346, 400)),
}
# Room cells separated by walls; the open corridor/living junction is split at
# the living-room wall line (x=316.6pt), corridor/reduit at y=361pt.
CELLS = {
    "Zimmer 1": mbox(209.7, 263.5, 268.0, 330.21),
    "Zimmer 2": mbox(270.3, 263.5, 314.27, 330.21),
    "Korridor": mbox(209.7, 330.21, 316.6, 361.06),
    "Bad": mbox(216.0, 351.24, 253.0, 394.0),
    "Reduit": mbox(276.0, 363.4, 316.6, 394.0),
    "Wohnen / Essen": mbox(314.27, 255, 380, 460),
}
rooms = []
for name, (bf, (lx, ly)) in LABELS.items():
    geom = floors.intersection(CELLS[name]).difference(walls)
    geom = max(getattr(geom, "geoms", [geom]), key=lambda g: g.area)
    rooms.append({"name": name, "plan_area_m2": bf, "model_area_m2": round(geom.area, 2),
                  "label": list(m(lx, ly)), "poly": geom})

# --- non-apartment surfaces --------------------------------------------------
stair_floor = mbox(144.72, 261.17, 209.7, 355.0).difference(walls)
terrace_n = mbox(206.06, 160.55, 382.4, 257.75)      # Sitzplatz N, 61.3 m²
terrace_n_tiles = mbox(315.8, 165.0, 379.0, 257.75)   # paved part, 19.48 m²
terrace_s = mbox(318.0, 460.95, 379.2, 516.7)         # Sitzplatz S, 15.0 m²
edge_n = mbox(206.06, 160.55, 382.4, 168.9)           # grey edge band (planter / kerb)

# --- openings: (name, kind, rect in pt) --------------------------------------
# kind: window = sill+head+glass, glazing = head + floor-to-head glass,
#       door = head only (leaf left out so the plan is readable), open = nothing
OPENINGS = [
    ("Zimmer 1 window",          "window",  (230.12, 257.75, 266.58, 263.51)),
    ("Zimmer 2 terrace door",    "glazing", (284.97, 257.75, 314.27, 263.51)),
    ("Living N glazing",         "glazing", (316.60, 258.60, 375.82, 263.51)),
    ("Living S glazing",         "glazing", (318.01, 455.18, 375.82, 459.60)),
    ("Stair N glazing",          "glazing", (148.62, 258.60, 205.81, 263.98)),
    ("Stair W entrance",         "glazing", (144.72, 334.73, 148.62, 349.06)),
    ("Stair S door",             "door",    (159.68, 351.24, 174.02, 355.11)),
    ("Elevator door",            "door",    (180.87, 351.24, 205.81, 354.05)),
    ("Apartment entrance",       "door",    (205.81, 334.73, 209.70, 349.06)),
    ("Zimmer 1 door",            "door",    (220.14, 330.21, 233.85, 332.54)),
    ("Zimmer 2 door",            "door",    (281.23, 330.21, 294.94, 332.54)),
    ("Bad door",                 "door",    (220.14, 351.24, 233.85, 353.97)),
    ("Reduit door",              "door",    (297.90, 361.06, 311.62, 363.40)),
]

# --- fixtures: (name, rect pt, z0, z1, material) ----------------------------
FIXTURES = [
    ("Kitchen counter",  (316.6, 266.9, 326.0, 332.6), 0.0, 0.90, "counter"),
    ("Kitchen tall units", (316.6, 266.9, 326.0, 285.4), 0.0, 2.10, "cabinet"),
    ("Kitchen wall units", (316.6, 285.4, 323.0, 332.6), 1.45, 2.10, "cabinet"),
    ("Cooktop",          (317.5, 297.0, 325.0, 305.0), 0.90, 0.92, "dark"),
    ("Sink",             (317.5, 316.0, 325.0, 322.0), 0.88, 0.92, "steel"),
    ("Bathtub",          (219.2, 378.0, 246.4, 390.4), 0.0, 0.55, "sanitary"),
    ("WC",               (240.0, 357.6, 246.4, 364.1), 0.0, 0.42, "sanitary"),
    ("Washbasin",        (240.0, 366.0, 246.4, 375.6), 0.80, 0.90, "sanitary"),
    ("Washer/dryer",     (285.6, 380.7, 294.7, 390.0), 0.0, 0.85, "sanitary"),
    ("Corridor cabinet", (281.0, 351.5, 290.2, 360.4), 0.0, 2.10, "cabinet"),
    ("Elevator car",     (182.0, 355.5, 205.0, 384.0), 0.0, 2.20, "steel"),
]
STAIR = (149.3, 286.4, 167.8, 330.8)  # lower flight, rising towards page-top
RISER = 0.175

COLORS = {
    "wall": (0.93, 0.92, 0.89, 1), "wall_cap": (0.20, 0.20, 0.22, 1),
    "slab": (0.55, 0.55, 0.55, 1), "floor_room": (0.80, 0.69, 0.53, 1),
    "floor_wet": (0.83, 0.85, 0.86, 1), "floor_stair": (0.66, 0.66, 0.64, 1),
    "terrace_tiles": (0.72, 0.70, 0.66, 1), "lawn": (0.47, 0.62, 0.38, 1),
    "edge": (0.60, 0.60, 0.58, 1), "glass": (0.62, 0.80, 0.90, 0.35),
    "frame": (0.30, 0.30, 0.32, 1), "counter": (0.85, 0.85, 0.83, 1),
    "cabinet": (0.97, 0.97, 0.95, 1), "dark": (0.10, 0.10, 0.10, 1),
    "steel": (0.70, 0.72, 0.74, 1), "sanitary": (1.0, 1.0, 1.0, 1),
}


def extrude(poly, z0, z1):
    """Extrude a shapely (multi)polygon in plan (x, z_page) to a Y-up mesh."""
    meshes = []
    for p in getattr(poly, "geoms", [poly]):
        if p.area < 1e-6:
            continue
        mesh = trimesh.creation.extrude_polygon(p, z1 - z0)
        mesh.apply_translation((0, 0, z0))
        # plan (x, y, height) -> world (x, height, y)
        mesh.apply_transform(np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]))
        meshes.append(mesh)
    return trimesh.util.concatenate(meshes) if meshes else None


scene = trimesh.Scene()


def add(name, mesh, color):
    if mesh is None:
        return
    mat = trimesh.visual.material.PBRMaterial(
        name=color, baseColorFactor=COLORS[color], metallicFactor=0.0, roughnessFactor=0.9,
        alphaMode="BLEND" if COLORS[color][3] < 1 else "OPAQUE")
    mesh.visual = trimesh.visual.TextureVisuals(material=mat)
    scene.add_geometry(mesh, node_name=name, geom_name=name)


# walls with openings cut out between sill and head
opening_polys = {n: mbox(*r) for n, k, r in OPENINGS}
all_open = unary_union(list(opening_polys.values()))
solid = walls.difference(all_open)
add("walls", extrude(solid, 0, WALL_H), "wall")
for n, kind, r in OPENINGS:
    o = opening_polys[n].intersection(walls.buffer(0.05)).envelope if kind != "glazing" else opening_polys[n]
    if kind == "open":
        continue
    head = {"door": DOOR_H, "window": DOOR_H, "glazing": GLAZE_H}[kind]
    add(f"lintel {n}", extrude(o, head, WALL_H), "wall")
    if kind == "window":
        add(f"sill {n}", extrude(o, 0, SILL_H), "wall")
    if kind in ("window", "glazing"):
        z0 = SILL_H if kind == "window" else 0.0
        # thin pane along the long axis of the opening, centred in the wall
        minx, miny, maxx, maxy = o.bounds
        if maxx - minx > maxy - miny:
            cy = (miny + maxy) / 2
            pane = box(minx, cy - 0.015, maxx, cy + 0.015)
            frame = box(minx, cy - 0.04, maxx, cy + 0.04)
        else:
            cx = (minx + maxx) / 2
            pane = box(cx - 0.015, miny, cx + 0.015, maxy)
            frame = box(cx - 0.04, miny, cx + 0.04, maxy)
        add(f"glass {n}", extrude(pane, z0 + 0.05, head - 0.05), "glass")
        add(f"frame-bottom {n}", extrude(frame, z0, z0 + 0.05), "frame")
        add(f"frame-top {n}", extrude(frame, head - 0.05, head), "frame")

footprint = unary_union([walls, floors, stair_floor]).buffer(0.02).buffer(-0.02)
add("slab", extrude(footprint, -SLAB, -0.01), "slab")
for r in rooms:
    wet = r["name"] in ("Bad", "Reduit")
    add(f"floor {r['name']}", extrude(r["poly"], -0.01, 0.0), "floor_wet" if wet else "floor_room")
add("floor Treppenhaus", extrude(stair_floor, -0.01, 0.0), "floor_stair")
add("terrace N lawn", extrude(terrace_n.difference(terrace_n_tiles).difference(edge_n), -0.20, -0.18), "lawn")
add("terrace N paving", extrude(terrace_n_tiles.difference(edge_n), -0.20, -0.16), "terrace_tiles")
add("terrace N edge", extrude(edge_n, -0.20, 0.25), "edge")
add("terrace S paving", extrude(terrace_s, -0.20, -0.16), "terrace_tiles")
for n, r, z0, z1, mat in FIXTURES:
    add(n, extrude(mbox(*r), z0, z1), mat)
# stair: risers rising towards page-top (north-west corner of the stairwell)
sx0, sy0, sx1, sy1 = STAIR
steps = 12
for i in range(steps):
    ya = sy1 - (sy1 - sy0) * (i + 1) / steps
    add(f"stair step {i + 1}", extrude(mbox(sx0, ya, sx1, sy1 - (sy1 - sy0) * i / steps), 0, RISER * (i + 1)), "floor_stair")

# --- export -----------------------------------------------------------------
OUT.mkdir(exist_ok=True)
glb = scene.export(file_type="glb")
(OUT / "apartment.glb").write_bytes(glb)
scene.export(OUT / "apartment.obj", file_type="obj")

def room_door(poly):
    """Centre of the door opening that leads into this room (for the eye-level view), or None."""
    best = None
    for n, kind, r in OPENINGS:
        if kind != "door":
            continue
        o = opening_polys[n]
        if o.distance(poly) < 0.05 and "Stair" not in n and "Elevator" not in n:
            c = o.centroid
            d = poly.exterior.distance(c)
            if best is None or d < best[0]:
                best = (d, [round(c.x, 3), round(c.y, 3)])
    return best[1] if best else None


minx, minz, maxx, maxz = footprint.bounds
info = {
    "name": "Lemgrubenstrasse 8 · Erdgeschoss · L08.02",
    "summary": "3½-Zimmerwohnung · 94 m² Nettowohnfläche · 76.3 m² Sitzplatz",
    "units": "metres", "up": "+y", "north": "-x (page left)",
    "scale_pt_per_m": round(PT_PER_M, 4),
    "wall_height_m": WALL_H, "door_head_m": DOOR_H, "sill_m": SILL_H,
    "extent_m": {"x": round(maxx - minx, 2), "z": round(maxz - minz, 2)},
    "rooms": [{**{k: v for k, v in r.items() if k != "poly"}, "bounds": [round(v, 3) for v in r["poly"].bounds],
               "door": room_door(r["poly"])} for r in rooms],
    "terraces": [
        {"name": "Sitzplatz N", "plan_area_m2": 61.3, "model_area_m2": round(terrace_n.area, 2),
         "label": list(terrace_n.centroid.coords[0])},
        {"name": "Sitzplatz S", "plan_area_m2": 15.0, "model_area_m2": round(terrace_s.area, 2),
         "label": list(terrace_s.centroid.coords[0])},
    ],
    "shared": [{"name": "Treppenhaus", "plan_area_m2": 18.4,
                "label": list(m(170, 342))}],
}
info["apartment_model_area_m2"] = round(sum(r["model_area_m2"] for r in rooms), 2)


def rings(poly):
    return [[[round(x, 3), round(z, 3)] for x, z in r.coords]
            for p in getattr(poly, "geoms", [poly]) for r in [p.exterior, *p.interiors]]


# Obstacles for the furniture planner: wall pieces at floor level (door and
# glazing openings left clear) plus fixtures standing on the floor.
living = next(r["poly"] for r in rooms if r["name"].startswith("Wohnen"))
info["grid_origin"] = [round(living.bounds[2], 3), round(living.bounds[1], 3)]  # east wall + north glazing faces
FLOOR_FIXTURES = ("Kitchen counter", "Bathtub", "WC", "Washer/dryer", "Corridor cabinet")
info["obstacles"] = {
    "walls": [rings(p.simplify(0.005)) for p in getattr(solid, "geoms", [solid])],
    "fixtures": [rings(mbox(*r)) for n, r, *_ in FIXTURES if n in FLOOR_FIXTURES],
    "fixture_tops": [z1 for n, r, z0, z1, _ in FIXTURES if n in FLOOR_FIXTURES],  # metres, same order
}
(OUT / "apartment.json").write_text(json.dumps(info, indent=2))

tpl = (ROOT / "viewer_template.html").read_text()
html = (tpl.replace("/*MODEL_INFO*/null", json.dumps(info))
           .replace("MODEL_GLB_BASE64", base64.b64encode(glb).decode()))
(ROOT / "index.html").write_text(html)

for r in info["rooms"]:
    print(f"{r['name']:16s} plan {r['plan_area_m2']:5.1f} m²   model {r['model_area_m2']:5.2f} m²")
print("apartment total", info["apartment_model_area_m2"], "m² (plan: 94)")
print("extent", info["extent_m"], "glb bytes", len(glb))
