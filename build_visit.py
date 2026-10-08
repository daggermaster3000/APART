"""Build visit/index.html, the realistic walkthrough.

The furniture builders are sliced out of viewer_template.html so the walkthrough
always draws pieces exactly like the planner does. Furniture positions come from
visit/items.json, a snapshot of the planner's shared layout (refresh it, then rerun).
"""
import base64, json, pathlib

ROOT = pathlib.Path(__file__).parent
viewer = (ROOT / "viewer_template.html").read_text(encoding="utf-8")
tpl = (ROOT / "visit_template.html").read_text(encoding="utf-8")

def cut(start, end):
    a = viewer.index(start)
    return viewer[a:viewer.index(end, a)]

catalog = cut("const CATALOG = [", "const SHAPES = {")
builders = cut("const furnRoot = new THREE.Group();", "// ---- footprint geometry")
heights = cut("// ---- heights.", "const vRange")

KEEP = ["id", "slug", "family", "desc", "type", "w", "d", "h", "chaise", "chaiseSide", "mount", "elev", "drop",
        "style", "meas", "colour", "colour2", "rot", "x", "z"]
items = json.loads((ROOT / "visit" / "items.json").read_text(encoding="utf-8"))
items = [{k: it[k] for k in KEEP if k in it} for it in items]
items.sort(key=lambda it: it["id"])

info = json.loads((ROOT / "model" / "apartment.json").read_text(encoding="utf-8"))
glb = base64.b64encode((ROOT / "model" / "apartment.glb").read_bytes()).decode()

out = (tpl.replace("/*CATALOG*/", catalog).replace("/*BUILDERS*/", builders).replace("/*HEIGHTS*/", heights)
          .replace("/*MODEL_INFO*/null", json.dumps(info, separators=(",", ":")))
          .replace("/*ITEMS*/[]", json.dumps(items, separators=(",", ":"), ensure_ascii=False))
          .replace("MODEL_GLB_BASE64", glb))
(ROOT / "visit" / "index.html").write_text(out, encoding="utf-8")
print(f"visit/index.html: {len(out) / 1e6:.2f} MB, {len(items)} pieces")
