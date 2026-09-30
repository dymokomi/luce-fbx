# Parity with ufbx

ufbx (Samuli Raivio, MIT) is a thorough C FBX loader and luce-fbx's reference.
A local oracle (kept outside this repository) loads each file of a corpus with
ufbx and prints a summary: settings, every node's world matrix, and for each
mesh its faces, corners, the world positions of the points its faces use, each
attribute summed over the corners, faces per material, and curve point
counts. `tools/fbxdump` prints the same for luce-fbx, and a script compares
them with a tolerance for f32 rounding.

The corpus is ufbx's `data/` (691 files from Maya, 3ds Max, Blender,
MotionBuilder, ZBrush, Revit and synthetic cases, FBX 2000 to 8000, ASCII and
binary) and Blender's FBX import tests (96 files).

2026-09-30. Meshes as ufbx loads them (blend shapes and skins applied at the
file's pose), world matrices and placed points:

| Outcome | Files |
|---|---:|
| match | 752 |
| mismatch | 8 |
| both reject | 8 |
| ufbx reads, luce-fbx rejects | 13 |
| luce-fbx reads, ufbx rejects | 5 |

- **luce-fbx rejects:** FBX 5 and older, and FBX 8, as intended (12 files);
  one synthetic file of garbage numbers.
- **Mismatches:**
  - synthetic edge cases (duplicate object ids, broken NURBS, invalid UTF-8
    axes, quotes in names);
  - one node kind (a Blender armature's root: ours "bone", ufbx "null").
- **luce-fbx reads, ufbx rejects:** synthetic files ufbx refuses on purpose
  (cycles, depth limits), which luce-fbx reads.

At time 1 s (the first animation stack evaluated, deformers applied), node
matrices and placed points: 711 of 787 files match. Every FBX 7 file with
animation matches (curves, extrapolation, layers, blend shape in-betweens,
linear, dual quaternion and blended skins); the mismatches are FBX 6 files,
whose takes luce-fbx does not read, and the synthetic and n-gon files above.

Attribute sums are compared too, except normals of skinned meshes: ufbx
reports a mesh's file normals, luce-fbx turns them with the skin.

## Writing

The local round-trip script (roundtrip.py beside the parity oracle) loads
each corpus file with fbxdump, saves it with `--save`, and has ufbx and
luce-fbx read the saved file: their mesh, pos, attr (N, UV and color sets;
luce-fbx also tangents and creases), mat and curve lines must equal
fbxdump's dump of the source. All 765 files that load match, at 7400 and
at 7500; saved with instances or Keep hierarchy, their faces, corners and
position sums match overall. Blender 5.1 (blender_roundtrip.py, headless)
imports 755 of the saved files with the same faces, corners and positions;
the 10 others hold NaN points or degenerate faces Blender drops.
