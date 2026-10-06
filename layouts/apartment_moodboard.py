"""Apartment-wide moodboard 'Sage & Oak, with water and books' applied to the shared layout.

Reads the current layout (one JSON file per piece, as exported from the artifact database),
keeps every existing piece, tidies a few stray ones, and adds the moodboard pieces.
Usage: python3 apartment_moodboard.py <current-dir> <out.json>
Coordinates in metres (x east, z south; z < 0 is the east garden; north is -x), rot in degrees.
"""
import copy, glob, json, os, sys

cur = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(os.path.join(sys.argv[1], "*.json"))}
T0 = 1791400000000
out, new = {}, []
SEARCH = "https://www.ikea.com/ch/de/search/?q="

def add(id, family, desc, type, w, d, h, x, z, rot, colour, zone, **kw):
    it = dict(id="mb-" + id, family=family, desc=desc, type=type, w=w, d=d, h=h, x=round(x, 3), z=round(z, 3), rot=rot,
              colour=colour, chaise=0, src=kw.pop("src", "manual"), createdAt=T0 + len(new), note=f"Apartment moodboard · {zone}")
    it.update(kw)
    new.append(it)

def move(id, **kw):
    d = copy.deepcopy(cur[id]); d.update(kw); out[id] = d

# palette
SAGE, OAT, OAK, TAUPE, CHAR, LAKE, WHITE, CREAM = "#7c8b74", "#e8dfd0", "#c9a26b", "#8b7765", "#2f3133", "#3e7c82", "#f1f0ec", "#ece4d6"

# ---------------------------------------------------------------- tidy existing pieces
# dining for six: the five HAUGA chairs go back round the MÖRBYLÅNGA table (x 12.67-13.67, z 1.92-4.12)
move("05250dee-d621-42a7-804b-da40b79e5a47", x=12.405, z=3.55, rot=90)
move("783506ff-45f1-4051-a4e9-86db0753f111", x=12.405, z=2.50, rot=90)
move("1913ed46-1c2c-4288-be2f-b7f0802b1546", x=13.935, z=2.50, rot=270)
move("d6c87231-2f2b-4494-bfab-2e0ae753cd2c", x=13.935, z=3.55, rot=270)
move("075eea61-ce93-4690-af55-2c6c01bd6bb8", x=13.17, z=1.655, rot=0)
hauga = copy.deepcopy(cur["075eea61-ce93-4690-af55-2c6c01bd6bb8"])
hauga.update(id="mb-hauga-6", x=13.17, z=4.385, rot=180, createdAt=T0 - 1, addedBy=None, by=None, note="Apartment moodboard · Dining (sixth chair)")
new.append(hauga)
# KALLAX TV bench: open side towards the room
move("d3b0de4b-8dd1-4a20-a530-7efa1311b195", rot=270)
# KALLAX room divider becomes part of the library: filled with books
k = cur["49be7dc5-3c09-4098-9c90-927a8f9d452c"]
move("49be7dc5-3c09-4098-9c90-927a8f9d452c", style={**k.get("style", {}), "books": True})
# strays: keyboard back on the desk, gallery frame back on the Zimmer 2 wall
move("z2-keyboard", x=9.56, z=2.02, rot=90, mount="surface", elev=73)
move("z2-frame-4", x=10.903, z=2.47, rot=270, mount="custom", elev=128)

# ---------------------------------------------------------------- Wohnen: library & aquarium (z 4.8-8.4)
for i, z in enumerate([5.25, 6.05, 6.85, 7.65]):
    add(f"billy-{i+1}", "BILLY", "Bücherregal, Eichenfurnier", "shelving", 80, 28, 202, 14.732, z, 270, OAK, "Library",
        slug="billy-bookcase-oak", url=SEARCH + "billy", style={"material": "wood", "books": True})
add("aquarium", "Aquarium", "120 l on an oak cabinet", "aquarium", 120, 50, 130, 11.318, 6.95, 90, OAK, "Library",
    colour2=CHAR, slug="aquarium-120", style={"material": "wood"})
add("strandmon", "STRANDMON", "Ohrensessel, Salbeigrün", "armchair", 82, 96, 101, 13.6, 7.1, 270, SAGE, "Library",
    colour2="#3b2a20", slug="strandmon-wing-chair", url=SEARCH + "strandmon", src="catalog")
add("reading-lamp", "Floor lamp", "linen shade, brass", "lamp", 40, 40, 155, 14.25, 7.85, 0, OAT, "Library",
    colour2="#b08d57", slug="floor-lamp", style={"material": "fabric", "shade": "drum"})
add("side-table", "GLADOM", "Tablett-Tisch, rund", "table", 45, 45, 53, 13.6, 6.35, 0, CHAR, "Library",
    slug="gladom-tray-table", url=SEARCH + "gladom", style={"material": "metal", "top": "round", "legs": "metal", "topThick": 2})
add("side-book", "Books", "the current read", "box", 22, 16, 5, 13.6, 6.35, 20, TAUPE, "Library", mount="surface", elev=53, slug="books")
add("library-rug", "Rug", "round, wool, 160 cm", "rug", 160, 160, 1, 13.35, 6.95, 0, OAT, "Library", style={"material": "fabric"}, slug="rug-round")
add("library-plant", "Plant", "fiddle-leaf fig", "plant", 45, 45, 150, 14.45, 4.55, 0, CREAM, "Library",
    style={"material": "ceramic", "foliage": "leafy"}, slug="plant")

# ---------------------------------------------------------------- Wohnen: dining (east end, by the glass to the garden)
for i, z in enumerate([2.47, 3.57]):
    add(f"dining-pendant-{i+1}", "Pendant", "rattan dome", "pendant", 45, 45, 28, 13.17, z, 0, "#b08a5a", "Dining",
        colour2=CHAR, mount="ceiling", drop=90, slug="pendant-rattan", style={"material": "rattan", "shade": "dome"})
add("dining-plant", "Plant", "olive tree by the glass", "plant", 50, 50, 160, 14.5, 0.6, 0, OAT, "Dining",
    style={"material": "ceramic", "foliage": "bushy"}, slug="plant")

# ---------------------------------------------------------------- Wohnen: lounge (west end, by the terrace)
add("tv", "TV", "55 inch", "monitor", 124, 25, 78, 14.68, 10.56, 270, CHAR, "Lounge", mount="surface", elev=39, slug="tv")
add("coffee-table", "LACK", "Couchtisch, Eiche", "table", 90, 55, 45, 13.1, 10.75, 90, OAK, "Lounge",
    slug="lack-coffee-table", url=SEARCH + "lack+couchtisch", style={"material": "wood", "legs": "square", "top": "rect", "topThick": 5, "apron": False})
add("lounge-rug", "Rug", "wool, oat, 200×300 cm", "rug", 300, 200, 1, 13.0, 10.6, 90, OAT, "Lounge", style={"material": "fabric"}, slug="rug")
add("lounge-lamp", "Floor lamp", "arc, black", "lamp", 40, 40, 160, 11.45, 12.45, 0, CHAR, "Lounge",
    colour2=CHAR, slug="floor-lamp", style={"material": "metal", "shade": "dome"})
add("lounge-plant", "Plant", "monstera", "plant", 50, 50, 120, 14.45, 12.4, 0, SAGE, "Lounge",
    style={"material": "ceramic", "foliage": "leafy"}, slug="plant")
add("guitar", "Guitar", "acoustic, on a stand", "guitar", 40, 35, 105, 14.6, 9.5, 270, "#d8b27a", "Lounge",
    colour2="#6b3f22", slug="acoustic-guitar", style={"material": "wood"})
add("lounge-candles", "Candles", "on the coffee table", "deco", 12, 12, 15, 13.1, 10.95, 0, CREAM, "Lounge",
    mount="surface", elev=45, style={"material": "ceramic", "profile": "cylinder"}, slug="candle")

# ---------------------------------------------------------------- Zimmer 1: bedroom
add("z1-gladom", "GLADOM", "Tablett-Tisch, schwarz", "table", 45, 55, 50, 7.72, 1.35, 0, "#ffffff", "Bedroom",
    slug="gladom-table", url=SEARCH + "gladom", style={"material": "plastic", "legs": "block", "top": "rect", "topThick": 3})
add("z1-lamp", "Table lamp", "ceramic, linen shade", "tablelamp", 22, 22, 45, 7.72, 1.35, 0, OAT, "Bedroom",
    colour2=SAGE, mount="surface", elev=50, slug="table-lamp", style={"material": "ceramic", "shade": "drum"})
for i, z in enumerate([1.3, 2.3]):
    add(f"z1-pax-{i+1}", "PAX", "Kleiderschrank 100×58×201, weiss", "storage", 100, 58, 201, 4.49, z, 90, WHITE, "Bedroom",
        slug="pax-wardrobe", url=SEARCH + "pax", src="catalog")
add("z1-dresser", "HEMNES", "Kommode mit 8 Schubladen, Eiche", "storage", 160, 50, 95, 6.85, 4.405, 180, OAK, "Bedroom",
    slug="hemnes-8-drawer-dresser", url=SEARCH + "hemnes+kommode", src="catalog")
add("z1-mirror", "Mirror", "oak frame", "deco", 60, 3, 80, 6.85, 4.64, 180, OAK, "Bedroom",
    mount="custom", elev=115, style={"material": "wood", "profile": "frame"}, slug="mirror-frame")
add("z1-dresser-plant", "Plant", "pothos", "plant", 18, 18, 30, 7.4, 4.42, 0, CREAM, "Bedroom",
    mount="surface", elev=95, style={"material": "ceramic", "foliage": "bushy"}, slug="plant")
add("z1-rug", "Rug", "sage wool, 170×240 cm", "rug", 240, 170, 1, 6.45, 2.57, 0, SAGE, "Bedroom", style={"material": "fabric"}, slug="rug")
for i, x in enumerate([5.75, 7.62]):
    add(f"z1-curtain-{i+1}", "Curtain", "linen, floor length", "curtain", 45, 10, 240, x, 0.45, 0, CREAM, "Bedroom", slug="curtain")
for i, (z, e, w, h) in enumerate([(2.05, 105, 30, 40), (2.57, 100, 40, 50), (3.09, 105, 30, 40)]):
    add(f"z1-frame-{i+1}", "Frame", f"{w}×{h} cm, botanical print", "deco", w, 3, h, 7.929, z, 270, "#4b3a2e", "Bedroom",
        mount="custom", elev=e, style={"material": "wood", "profile": "frame"}, slug="frame")
add("z1-plant", "Plant", "snake plant", "plant", 35, 35, 90, 4.5, 3.45, 0, OAT, "Bedroom",
    style={"material": "ceramic", "foliage": "upright"}, slug="plant")

# ---------------------------------------------------------------- Korridor: arrival
add("hall-shoes", "HEMNES", "Schuhschrank, weiss", "storage", 89, 30, 127, 6.3, 4.955, 0, WHITE, "Hall",
    slug="hemnes-shoe-cabinet", url=SEARCH + "hemnes+schuhschrank", style={"material": "painted", "fronts": "doors", "handles": "knob", "legs": "plinth"})
add("hall-mirror", "Mirror", "round-cornered, oak", "deco", 50, 3, 70, 6.3, 4.82, 0, OAK, "Hall",
    mount="custom", elev=140, style={"material": "wood", "profile": "frame"}, slug="mirror-frame")
add("hall-bench", "Bench", "oak, by the door", "table", 100, 35, 46, 7.65, 4.985, 0, OAK, "Hall",
    slug="bench", style={"material": "wood", "legs": "square", "top": "rect", "topThick": 4, "apron": False})
add("hall-hooks", "Coat rail", "oak with hooks", "wallshelf", 100, 12, 3, 7.65, 4.865, 0, OAK, "Hall",
    colour2=CHAR, mount="custom", elev=170, slug="wall-shelf")
add("hall-runner", "Rug", "runner, 80×300 cm", "rug", 300, 80, 1, 7.6, 5.42, 0, TAUPE, "Hall", style={"material": "fabric"}, slug="rug")
for i, x in enumerate([6.2, 6.7]):
    add(f"hall-frame-{i+1}", "Frame", "travel print", "deco", 35, 3, 45, x, 5.985, 180, CHAR, "Hall",
        mount="custom", elev=135, style={"material": "wood", "profile": "frame"}, slug="frame")
add("hall-plant", "Plant", "kentia palm", "plant", 40, 40, 130, 10.75, 5.1, 0, OAT, "Hall",
    style={"material": "ceramic", "foliage": "leafy"}, slug="plant")

# ---------------------------------------------------------------- Bad & Reduit
add("bath-mat", "Bath mat", "cotton, sage", "rug", 80, 50, 1, 5.55, 7.55, 0, SAGE, "Bathroom", style={"material": "fabric"}, slug="rug")
add("reduit-shelf", "Shelf", "brewing supplies: malt, hops, bottles", "shelving", 80, 40, 180, 10.648, 8.1, 270, "#9aa0a6", "Reduit",
    slug="shelving-unit", style={"material": "metal", "books": True})

# ---------------------------------------------------------------- Garden east: beer garden, brewing, raised beds
add("biertisch", "Beer table", "220×50 cm, spruce", "table", 220, 50, 77, 12.3, -3.3, 90, "#c8a173", "Garden",
    colour2=CHAR, slug="beer-table", style={"material": "wood", "legs": "metal", "top": "rect", "topThick": 3, "apron": False})
for i, x in enumerate([11.75, 12.85]):
    add(f"bierbank-{i+1}", "Beer bench", "220×25 cm", "table", 220, 25, 47, x, -3.3, 90, "#c8a173", "Garden",
        colour2=CHAR, slug="beer-bench", style={"material": "wood", "legs": "metal", "top": "rect", "topThick": 3, "apron": False})
add("brew-bench", "Brewing bench", "stainless, 120×60 cm", "table", 120, 60, 90, 14.7, -3.3, 270, "#c8ccd0", "Brewing",
    colour2="#9aa0a6", slug="work-bench", style={"material": "metal", "legs": "metal", "top": "rect", "topThick": 3, "apron": False})
add("brew-kettle", "Brew kettle", "50 l on a gas burner", "brewkettle", 55, 55, 110, 14.6, -4.55, 0, "#c8ccd0", "Brewing",
    slug="brew-kettle", style={"material": "metal"})
add("brew-mill", "Grain mill", "on the bench", "box", 25, 25, 35, 14.7, -3.65, 0, "#9aa0a6", "Brewing", mount="surface", elev=90, slug="grain-mill")
add("brew-chiller", "Wort chiller", "copper coil", "deco", 30, 30, 20, 14.7, -3.0, 0, "#b87333", "Brewing",
    mount="surface", elev=90, style={"material": "metal", "profile": "cylinder"}, slug="chiller")
for i, x in enumerate([14.2, 14.65]):
    add(f"fermenter-{i+1}", "Fermenter", "30 l, airlock", "fermenter", 35, 35, 60, x, -1.95, 0, WHITE, "Brewing", slug="fermenter")
add("brew-crates", "Bottle crates", "two, stacked", "box", 40, 30, 60, 14.15, -4.05, 0, "#2f5d8a", "Brewing", slug="crate")
add("brew-gas", "Gas bottle", "propane, 10.5 kg", "deco", 30, 30, 58, 14.95, -5.15, 0, "#d9d9d9", "Brewing",
    mount="floor", style={"material": "metal", "profile": "cylinder"}, slug="gas-bottle")
for i, x in enumerate([6.3, 8.8]):
    add(f"raised-bed-{i+1}", "Raised bed", "larch, 200×80×70 cm", "raisedbed", 200, 80, 70, x, -3.4, 0, "#a77b4f", "Garden",
        slug="raised-bed", style={"material": "wood"})
add("rain-barrel", "Rain barrel", "300 l", "deco", 60, 60, 95, 10.3, -0.55, 0, "#3e5a6b", "Garden",
    style={"material": "plastic", "profile": "cylinder"}, slug="rain-barrel")
add("garden-tree", "Apple tree", "dwarf, in the lawn", "plant", 90, 90, 230, 4.9, -1.3, 0, "#6b4a32", "Garden",
    style={"material": "wood", "foliage": "bushy"}, slug="plant")
for i, x in enumerate([11.3, 13.4]):
    add(f"herb-pot-{i+1}", "Herbs", "hops in a pot", "plant", 45, 45, 110, x, -5.45, 0, "#a4593f", "Brewing",
        style={"material": "ceramic", "foliage": "upright"}, slug="plant")

# ---------------------------------------------------------------- Terrace west: bistro corner
add("bistro-table", "Bistro table", "round, 70 cm", "table", 70, 70, 74, 13.6, 14.6, 0, CHAR, "Terrace W",
    slug="bistro-table", style={"material": "metal", "top": "round", "legs": "pedestal", "topThick": 2})
for i, (z, r) in enumerate([(14.0, 0), (15.2, 180)]):
    add(f"bistro-chair-{i+1}", "Chair", "folding, acacia", "chair", 44, 50, 82, 13.6, z, r, "#8a6a45", "Terrace W",
        slug="chair-outdoor", style={"material": "wood", "legs": "square"})
for i, x in enumerate([11.55, 14.7]):
    add(f"terrace-plant-{i+1}", "Plant", "olive in terracotta", "plant", 55, 55, 140, x, 16.15, 0, "#a4593f", "Terrace W",
        style={"material": "ceramic", "foliage": "bushy"}, slug="plant")

for it in new:
    out[it["id"]] = it
json.dump({"changed": list(out.values()), "all": list({**cur, **out}.values())}, open(sys.argv[2], "w"), indent=1)
print(len(out), "pieces written,", len(new), "new;", len({**cur, **out}), "in total")
