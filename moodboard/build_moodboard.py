"""Builds moodboard/index.html from the model geometry (model/apartment.json) and a layout file.
Usage: python3 build_moodboard.py <layout.json>   (a JSON list of pieces, as the planner stores them)"""
import json, math, pathlib, sys, html

ROOT = pathlib.Path(__file__).resolve().parent.parent
INFO = json.loads((ROOT / "model" / "apartment.json").read_text())
items = json.loads(pathlib.Path(sys.argv[1]).read_text())

# ---- plan: north up. World x runs south, world z runs west (north is -x on the brochure plan).
S = 38  # px per metre
U0, V0 = -17.2, 3.4
def P(x, z): return ((-z - U0) * S, (x - V0) * S)
def path(pts): return "M" + " L".join(f"{u:.1f},{v:.1f}" for u, v in (P(x, z) for x, z in pts)) + " Z"

def rects(it):
    w, d, c, s = it["w"] / 100, it["d"] / 100, math.cos(math.radians(it.get("rot", 0))), math.sin(math.radians(it.get("rot", 0)))
    out = []
    D = max(d, (it.get("chaise") or 0) / 100) if it["type"] == "sofa" else d
    loc = [[-w / 2, -D / 2, w / 2, D / 2]]
    if it["type"] == "sofa" and D > d + 0.05:   # L-shaped: main seat + chaise
        side = -1 if it.get("chaiseSide") == "left" else 1
        cw = min(0.98, w * 0.42)
        xa, xb = (w / 2 - cw, w / 2) if side > 0 else (-w / 2, -w / 2 + cw)
        loc = [[-w / 2, -D / 2, w / 2, -D / 2 + d], [xa, -D / 2 + d, xb, D / 2]]
    for x0, z0, x1, z1 in loc:
        out.append([(it["x"] + lx * c + lz * s, it["z"] - lx * s + lz * c) for lx, lz in [(x0, z0), (x1, z0), (x1, z1), (x0, z1)]])
    return out

ZONE_OF = lambda it: (it.get("note") or "").split("·")[-1].strip() if "moodboard" in (it.get("note") or "") else ""
FILL = {"rug": "var(--oat)", "plant": "var(--sage-l)", "raisedbed": "var(--oak)", "aquarium": "var(--lake)",
        "brewkettle": "var(--steel)", "fermenter": "var(--paper)", "shelving": "var(--oak)", "daybed": "var(--sage)",
        "sofa": "var(--taupe-l)", "armchair": "var(--sage)", "bed": "var(--oat)"}
svg = []
W, H = (6.6 - U0) * S + 20, (16.9 - V0) * S
for g in INFO["grounds"][::-1]:
    x0, z0, x1, z1 = g["rect"]
    col = {"Lawn": "var(--lawn)", "Kerb": "var(--kerb)"}.get(g["name"], "var(--paving)")
    svg.append(f'<path d="{path([(x0, z0), (x1, z0), (x1, z1), (x0, z1)])}" fill="{col}"/>')
for r in INFO["rooms"]:
    x0, z0, x1, z1 = r["bounds"]
    svg.append(f'<path d="{path([(x0, z0), (x1, z0), (x1, z1), (x0, z1)])}" fill="var(--floor)"/>')
for poly in INFO["obstacles"]["fixtures"]:
    svg.append(f'<path d="{path(poly[0])}" fill="var(--fixture)"/>')
for it in sorted(items, key=lambda i: 0 if i["type"] == "rug" else (2 if i.get("mount") in ("custom", "ceiling") else 1)):
    if it["type"] in ("curtain", "box") or it.get("mount") == "ceiling" or (it.get("mount") == "custom" and it["type"] == "deco"): continue
    for q in rects(it):
        f = FILL.get(it["type"], "var(--piece)")
        op = ' fill-opacity="0.55"' if it["type"] == "rug" else ""
        svg.append(f'<path d="{path(q)}" fill="{f}"{op} stroke="var(--ink)" stroke-width="0.8"/>')
for poly in INFO["obstacles"]["walls"]:
    d = " ".join(path(ring) for ring in poly)
    svg.append(f'<path d="{d}" fill="var(--ink)" fill-rule="evenodd"/>')
LABELS = [("Library & aquarium", 12.95, 6.5), ("Dining", 13.2, 1.0), ("Lounge", 13.6, 11.8), ("Bedroom", 6.1, 0.9),
          ("Work & guest", 9.5, 4.25), ("Hall", 8.5, 5.9), ("Bath", 5.8, 8.25), ("Reduit", 9.9, 8.3),
          ("Beer garden & brewing", 13.0, -5.3), ("Kitchen garden", 7.5, -5.0), ("Bistro terrace", 13.1, 16.2)]
for name, x, z in LABELS:
    u, v = P(x, z)
    svg.append(f'<text x="{u:.0f}" y="{v:.0f}" class="lbl">{html.escape(name)}</text>')
u0, v0 = 20, H - 18
svg.append(f'<path d="M{u0},{v0} h{S*2} M{u0},{v0-5} v10 M{u0+S},{v0-4} v8 M{u0+2*S},{v0-5} v10" stroke="var(--ink)" stroke-width="1.5" fill="none"/>'
           f'<text x="{u0}" y="{v0-10}" class="lbl small">0</text><text x="{u0+2*S-12}" y="{v0-10}" class="lbl small">2 m</text>')
svg.append(f'<g transform="translate({W-44},40)"><circle r="16" fill="none" stroke="var(--ink)"/><path d="M0,-13 L5,3 L0,0 L-5,3 Z" fill="var(--ink)"/><text y="-22" text-anchor="middle" class="lbl small">N</text></g>')
PLAN = f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="Floor plan with every piece of furniture at its real size">{"".join(svg)}</svg>'

def by(zone):
    return [i for i in items if ZONE_OF(i) == zone or (zone == "Dining" and i.get("family") == "HAUGA")]
def li(it):
    size = f'{it["w"]}×{it["d"]}×{it["h"]}'
    return f'<li><span>{html.escape(it["family"])}</span> <em>{html.escape(it.get("desc") or "")}</em> <code>{size}</code></li>'

ZONES = [
 ("library", "Library & aquarium", "Wohnen, middle", "The middle of the long living room becomes a reading room: four oak BILLY bookcases fill the south wall, the KALLAX divider is stocked with books on the library side, and a 120-litre aquarium on an oak cabinet faces them from the north wall. A sage STRANDMON wing chair sits between the two, under a linen floor lamp.",
  "Library", ["aquarium"], ["Keep the lower BILLY shelves for oversized books and records", "A clip-on picture light over the aquarium for evenings", "Low-light plants in the tank: anubias, java fern, cryptocoryne", "One shelf per BILLY left half-empty for objects and plants"]),
 ("dining", "Dining for six", "Wohnen, garden end", "The MÖRBYLÅNGA table gets all six HAUGA chairs back round it, two rattan domes hang low over the table, and an olive tree stands by the glass to the garden.",
  "Dining", [], ["Linen runner in oat", "Pendants at 90 cm under the ceiling, about 1.3 m above the top"]),
 ("lounge", "Lounge", "Wohnen, terrace end", "VIMLE stays where it is. The KALLAX TV bench turns its open side to the room, with a 55-inch screen on top, an oak LACK coffee table, a 2×3 m oat wool rug, a black arc lamp and a monstera by the glass to the terrace.",
  "Lounge", [], ["Sage and oat cushions on VIMLE, one taupe velvet", "Wool throw over the chaise", "Candles on the coffee table, not on the TV bench"]),
 ("bedroom", "Bedroom", "Zimmer 1", "Your pine NEIDEN bed gets a second GLADOM bedside table and lamp, two white PAX wardrobes take the west wall, an oak HEMNES chest of drawers with a mirror sits by the door, a sage rug goes under the bed and linen curtains frame the window.",
  "Bedroom", [], ["Three botanical prints above the bed", "Snake plant in the corner, it tolerates the low light", "Warm 2700 K bulbs in both bedside lamps"]),
 ("zimmer2", "Work & guest room", "Zimmer 2", "Kept as you set it up from the first moodboard: desk, SKÅDIS pegboards, HEMNES daybed, gallery wall and shelf. Only the keyboard went back onto the desk and one stray frame back onto the wall.",
  "", [], []),
 ("hall", "Arrival", "Korridor", "A white HEMNES shoe cabinet with an oak mirror above it, an oak bench under a coat rail, a taupe runner the length of the corridor, two travel prints and a kentia palm where the corridor opens into the living room.",
  "Hall", [], ["Hooks at 170 cm, bench at 46 cm", "A tray on the shoe cabinet for keys"]),
 ("garden", "Kitchen garden & beer garden", "Garden (east)", "Two 200×80 cm larch raised beds on the lawn for vegetables and herbs, a dwarf apple tree and a 300-litre rain barrel by the house. On the paving, a classic beer-garden set (table and two benches) next to the brewing corner.",
  "Garden", ["brewing"], ["Raised beds at 70 cm: no bending, and room for a cold frame lid", "Hops climbing up the two tall pots by the kerb", "Rain barrel feeds the beds and the brew-day clean-up"]),
 ("brewing", "Brewing corner", "Garden, paving by the living room", "Brewing happens outside on the paving: a 50-litre kettle on a gas burner, a stainless bench with the grain mill and copper wort chiller, two 30-litre fermenters, bottle crates and the propane bottle at the far edge. Malt, hops and bottles live on a metal shelf in the Reduit, a few steps away.",
  "Brewing", [], ["Keep the burner 1 m from the house and the fermenters in the shade", "Hose connection near the bench for the chiller", "Fermenters move into the Reduit for steady temperatures"]),
 ("terrace", "Bistro terrace", "Terrace (west)", "A round charcoal bistro table with two acacia folding chairs and two olive trees in terracotta: a morning-coffee spot off the lounge.",
  "Terrace W", [], []),
]
def section(key, title, where, text, zone, extra, ideas):
    pieces = by(zone) if zone else []
    img = f'<figure class="shot"><img src="img/{key}.jpg" alt="3D view: {html.escape(title)}" loading="lazy"><figcaption>{html.escape(where)}</figcaption></figure>'
    more = "".join(f'<figure class="shot small"><img src="img/{e}.jpg" alt="3D view: {e}" loading="lazy"></figure>' for e in extra)
    lst = f'<ul class="pieces">{"".join(li(i) for i in pieces)}</ul>' if pieces else ""
    ide = f'<ul class="ideas">{"".join(f"<li>{html.escape(t)}</li>" for t in ideas)}</ul>' if ideas else ""
    return f'<section class="zone" id="{key}"><div class="pics">{img}{more}</div><div class="txt"><h3>{html.escape(title)}</h3><p>{html.escape(text)}</p>{ide}{lst}</div></section>'

ZONE_HTML = "\n".join(section(*z) for z in ZONES)
tpl = (ROOT / "moodboard" / "template.html").read_text(encoding="utf-8")
out = tpl.replace("{{PLAN}}", PLAN).replace("{{ZONES}}", ZONE_HTML).replace("{{COUNT}}", str(len(items)))
(ROOT / "moodboard" / "index.html").write_text(out, encoding="utf-8")
print("moodboard written:", len(out), "bytes")
