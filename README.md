# Lemgrubenstrasse 8 · L08.02 — 3D model

To-scale 3D model of the 3½-room ground-floor apartment L08.02 (94 m² net, 76.3 m² Sitzplatz),
built from the brochure floor plan in `source/floorplan_L08.02.pdf`.

| File | What it is |
| --- | --- |
| `index.html` | Self-contained 3D viewer and furniture planner (model embedded). Orbit, plan view, eye-level view, adjustable section cut, click-to-measure, IKEA furniture placement. |
| `model/apartment.glb` | glTF binary for Blender, SketchUp, online viewers. Metres, Y up. |
| `model/apartment.obj` + `material.mtl` | Same model as Wavefront OBJ. |
| `model/apartment.json` | Rooms with plan area (BF) vs. measured model area. |
| `build_model.py` | Regenerates everything from the PDF. |

## Furniture planner

Paste an IKEA product link (any country site, any colour variant) into **Furnish → Add IKEA furniture**.
The page reads the product name, article number and colour from the link and builds a to-scale
block model of it (sofa with optional chaise, armchair, bed, table, desk, chair, cabinet, open
shelving, rug, floor lamp, table lamp, pendant lamp, plant, decoration, or a plain block).

- **Sizes.** The page cannot open ikea.com (its network access is blocked), so sizes come from, in order:
  a built-in list of common products checked against IKEA's measurements (VIMLE, KIVIK, MALM, STRANDMON,
  POÄNG, EKEDALEN, LACK, MICKE, HEMNES, BRIMNES, BILLY, KALLAX, PAX); sizes written in the link
  (e.g. `160x200`); an estimate from Claude when the page runs inside claude.ai; or a typical size for
  the shape. The source is shown on each item; every size can be edited.
- **Grid.** Off / 5 / 10 / 25 cm. Footprint edges snap to grid lines aligned with the living room's
  walls, and optionally flush against the nearest wall.
- **Fit check.** Each item reports *Fits*, *Hits a wall*, *Hits a fixture* (kitchen, bath, WC, washer)
  or *Overlaps furniture*, and turns red when it doesn't fit.
- **Style from the product photo.** The page can't load ikea.com, so the photo comes from you: on the
  IKEA page right-click the main photo, *Copy image*, and paste it into the piece's card (or drop or pick
  a saved image). The page takes the main colours from the photo straight away, then asks Claude (with
  your permission, on your Claude usage) to read the style: material (fabric, velvet, leather, wood,
  painted, metal, glass, rattan, ceramic…), legs (block, tapered, turned, metal, hairpin, sled,
  pedestal, plinth), arms, back and cushions for sofas, headboard, table-top shape, cabinet fronts and
  handles, lamp shade, vase shape, plant foliage. The 3D model is rebuilt to match, and a small
  thumbnail of the photo is kept with the piece so collaborators see it too. Everything is editable
  under *Style*. Catalogue products start with a matching style preset.
- **Measurements from the IKEA plans.** Paste the product's *Measurements* list (English, German or
  French) into a piece's *Measurements* section and it is read on the spot: width, depth, height, chaise
  depth, seat height and depth, armrest width and height, backrest height, free height under the
  furniture, head- and footboard height, tabletop thickness, shade size, pot height. Or paste the
  measurement drawing (the image with dimension lines) next to the photo. Where Claude can look at
  images it reads the drawing directly. Everywhere else the page reads the drawing's numbers itself with
  OCR (tesseract.js, bundled in `vendor/ocr/`, horizontal and vertical text), then either Claude matches
  them to dimensions from their positions (text only, and only numbers that are really in the drawing
  are accepted) or you click a number and then the box it belongs to. The builders use these numbers for the model's proportions; VIMLE, KIVIK and MALM carry their
  published measurements already.
- **More shapes.** Daybed (HEMNES), pegboard (SKÅDIS), wall shelf, curtain, office chair and monitor,
  next to sofas, beds, tables, desks, chairs, storage, shelving, rugs, lamps, plants and decorations.
- **View from the door.** In *Rooms*, the eye button next to a room puts the camera in its doorway at
  eye height. Tables and desks count only their top in the fit check, so chairs and drawer units can
  stand underneath.
- **Height.** Each piece has a placement: *On the floor*, *On whatever is below it* (rests on the
  table, sideboard, bed, sofa seat or kitchen counter under it, or the floor if there's nothing),
  *At a set height* (cm above the floor), or *Hanging from the ceiling* (cable length from the
  2.50 m ceiling). Decorations, plants and table lamps default to resting on what's below; pendant
  lamps hang. Things resting on a piece move and turn with it, and drop to what's beneath when it is
  removed. Fit checks only compare pieces that overlap in height, so a vase on a table or a lamp above
  it doesn't count as a clash.
- **Editing.** Click to select, drag to move, `R` rotate 90°, arrow keys nudge, `PgUp`/`PgDn` raise or
  lower by 5 cm (`Shift` for 1 cm), `Del` remove.

## Working together

Opened on claude.ai, the planner is shared: everyone with access sees one layout and changes it live.

- **Sharing.** Invite people with the page's **Share** menu. Contributors and Editors can add and move
  furniture; Viewers can look around (the page switches to view-only for them).
- **Live.** Each change saves on its own (one document per piece in the artifact's database). Other
  people's pointers, selections and in-progress drags show in the model in their colour; a piece someone
  is dragging can't be grabbed until they drop it. Each piece shows who moved it last.
- **Saved layouts.** *Share & save → Save this layout* stores a named copy of the arrangement. Anyone with
  edit access can load one (it replaces the current furniture for everyone, after a confirmation) or
  delete it. The link icon copies a link straight to a saved layout (`…#layout-<id>`).
- Opened as a local file, the same page works on its own and saves in the browser.

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
