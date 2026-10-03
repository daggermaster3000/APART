# Lemgrubenstrasse 8 · L08.02 — 3D model

To-scale 3D model of the 3½-room ground-floor apartment L08.02 (94 m² net, 76.3 m² Sitzplatz),
built from the brochure floor plan in `source/floorplan_L08.02.pdf`.

| File | What it is |
| --- | --- |
| `index.html` | Self-contained 3D viewer (model embedded). Open in a browser: orbit, plan view, eye-level view, adjustable section cut, click-to-measure. |
| `model/apartment.glb` | glTF binary for Blender, SketchUp, online viewers. Metres, Y up. |
| `model/apartment.obj` + `material.mtl` | Same model as Wavefront OBJ. |
| `model/apartment.json` | Rooms with plan area (BF) vs. measured model area. |
| `build_model.py` | Regenerates everything from the PDF. |

## How it is to scale

Walls (black fills) and room floors (blue fills) are read straight from the PDF's vector
paths. The scale comes from the plan's own 0–10 m scale bar (15.566 pt per metre).
Measured floor areas against the areas printed on the plan:

| Room | Plan BF m² | Model m² |
| --- | ---: | ---: |
| Zimmer 1 | 16.0 | 16.04 |
| Zimmer 2 | 12.4 | 12.10 |
| Korridor | 10.1 | 10.79 |
| Bad | 4.3 | 4.47 |
| Reduit | 3.3 | 3.34 |
| Wohnen / Essen | 47.9 | 48.17 |
| **Total** | **94** | **94.91** |

The corridor includes the niche in front of the Reduit (with the tall cabinet), which the plan's
figure appears to exclude.

## Assumptions (the plan has no heights)

- Clear room height 2.50 m, slab 0.25 m
- Door heads 2.10 m, window sill 0.90 m (Zimmer 1), full-height glazing heads 2.30 m
- Door leaves are omitted; openings are shown as clear gaps with lintels
- Fixtures (kitchen, bath, washer, lift car) are simple blocks placed from the plan symbols
- Plan north points to the page's left, which is −x in the model

## Rebuild

```sh
pip install pymupdf shapely trimesh mapbox_earcut numpy
python3 build_model.py
```
