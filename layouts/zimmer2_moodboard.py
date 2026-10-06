import json, time
# Zimmer 2 inner faces (m): west x=8.095, east x=10.918, north z=0.370, south z=4.655
W, E, N, S = 8.095, 10.918, 0.370, 4.655
U = "https://www.ikea.com/ch/de/p/"
t0 = 1791300000000
items = []
def add(id, family, desc, type, w, d, h, x, z, rot, colour, **kw):
    it = dict(id=id, family=family, desc=desc, type=type, w=w, d=d, h=h, x=round(x, 3), z=round(z, 3), rot=rot,
              colour=colour, chaise=0, src=kw.pop("src", "manual"), createdAt=t0 + len(items), note="Zimmer 2 moodboard")
    it.update(kw); items.append(it)
desk_h = 73
# --- daybed on the east wall, clear of the terrace door's swing (to z≈1.15)
add("z2-daybed", "HEMNES", "Tagesbett mit 3 Schubladen, weiss", "daybed", 209, 89, 83, E - 0.445, 2.25, 270, "#f1f0ec",
    colour2="#7c8b74", slug="hemnes-tagesbett-mit-3-schubladen-weiss", url=U + "hemnes-tagesbett-mit-3-schubladen-weiss/", src="catalog")
add("z2-basket", "Basket", "rattan, at the foot of the daybed", "deco", 40, 40, 40, E - 0.30, 3.62, 0, "#b08a5a",
    mount="surface", elev=0, style={"material": "rattan", "profile": "cylinder"}, slug="basket")
add("z2-plant-basket", "Plant", "monstera in the basket", "plant", 36, 36, 75, E - 0.30, 3.62, 40, "#b08a5a",
    mount="surface", elev=40, style={"material": "rattan", "foliage": "leafy"}, slug="plant")
# --- gallery wall + shelf above the daybed (east wall, facing west)
fx = E - 0.015
for i, (z, e, w, h) in enumerate([(1.55, 125, 30, 40), (1.55, 92, 25, 30), (2.02, 112, 40, 50), (2.47, 128, 30, 40), (2.47, 92, 25, 30)]):
    add(f"z2-frame-{i+1}", "Frame", f"{w}×{h} cm, nature print", "deco", w, 3, h, fx, z, 270, "#4b3a2e",
        mount="custom", elev=e, style={"material": "wood", "profile": "frame"}, slug="frame")
add("z2-shelf", "Wall shelf", "oak, above the daybed", "wallshelf", 80, 20, 3, E - 0.10, 2.95, 270, "#c9a26b",
    colour2="#2b2b2d", mount="custom", elev=178, slug="wall-shelf")
add("z2-shelf-plant", "Plant", "trailing pothos on the shelf", "plant", 16, 16, 28, E - 0.10, 2.78, 0, "#e8dfd0",
    mount="surface", elev=181, style={"material": "ceramic", "foliage": "bushy"}, slug="plant")
add("z2-books", "Books", "on the shelf", "box", 22, 16, 22, E - 0.10, 3.15, 270, "#d9cbb5",
    mount="surface", elev=181, slug="books")
# --- desk wall (west): oak top on an ALEX drawer unit and slim white legs, pegboard above
add("z2-desk", "Desk", "160×80 cm, oak top", "table", 160, 80, desk_h, W + 0.40, 2.10, 90, "#d2b48c",
    colour2="#f1f0ec", style={"material": "wood", "legs": "metal", "top": "rect", "topThick": 3, "apron": False}, slug="desk-160x80")
add("z2-alex", "ALEX", "Schubladenelement, weiss", "storage", 36, 58, 70, W + 0.31, 2.58, 90, "#f1f0ec",
    slug="alex-schubladenelement-weiss", url=U + "alex-schubladenelement-weiss-00473546/", src="catalog")
for i, e in enumerate([95, 151]):
    add(f"z2-skadis-{i+1}", "SKÅDIS", "Lochplatte 76×56 cm, weiss", "pegboard", 76, 4, 56, W + 0.02, 2.10, 90, "#f1f0ec",
        mount="custom", elev=e, slug="skadis-lochplatte-weiss", url=U + "skadis-lochplatte-weiss-10320803/", src="catalog")
add("z2-monitor", "Monitor", "27 inch", "monitor", 61, 20, 46, W + 0.20, 2.10, 90, "#2b2b2d", mount="surface", elev=desk_h, slug="monitor")
add("z2-keyboard", "Keyboard", "", "box", 44, 13, 2, W + 0.50, 2.10, 90, "#3a3d40", mount="surface", elev=desk_h, slug="keyboard")
add("z2-lamp", "Desk lamp", "black, warm light", "tablelamp", 18, 18, 45, W + 0.22, 1.50, 90, "#2b2b2d",
    mount="surface", elev=desk_h, style={"material": "metal", "shade": "cone"}, slug="desk-lamp")
add("z2-desk-plant", "Plant", "small, on the desk", "plant", 14, 14, 30, W + 0.20, 2.78, 0, "#f1f0ec",
    mount="surface", elev=desk_h, style={"material": "ceramic", "foliage": "upright"}, slug="plant")
add("z2-chair", "Office chair", "white frame, grey seat", "officechair", 65, 65, 100, W + 1.15, 2.00, 270, "#f1f0ec",
    colour2="#5a5d61", slug="office-chair")
# --- floor plant in the north-west corner, rug, curtains at the glass
add("z2-plant-corner", "Plant", "large, by the window", "plant", 40, 40, 100, W + 0.28, N + 0.30, 0, "#e8dfd0",
    style={"material": "ceramic", "foliage": "leafy"}, slug="plant")
add("z2-rug", "Rug", "jute look, 133×195 cm", "rug", 133, 195, 1, 9.47, 2.55, 0, "#cdb48e", style={"material": "fabric"}, slug="rug")
for i, x in enumerate([9.24, 10.62]):
    add(f"z2-curtain-{i+1}", "Curtain", "linen, floor length", "curtain", 40, 10, 240, x, N + 0.08, 0, "#ece4d6", slug="curtain")
json.dump(items, open(__import__("sys").argv[1], "w"), indent=1)
print(len(items), "items")
