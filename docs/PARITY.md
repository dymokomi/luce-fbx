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

2026-09-30, meshes at rest (no skinning or blend shapes):

| Outcome | Files |
|---|---:|
| match | 749 |
| mismatch | 11 |
| both reject | 8 |
| ufbx reads, luce-fbx rejects | 13 |
| luce-fbx reads, ufbx rejects | 5 |

- **luce-fbx rejects:** FBX 5 and older, and FBX 8, as intended (12 files);
  one synthetic file of garbage numbers.
- **Mismatches:**
  - three files with faces of more than 256 corners, which luce-fbx
    triangulates;
  - synthetic edge cases (duplicate object ids, broken NURBS, invalid UTF-8
    axes, quotes in names);
  - one node kind (a Blender armature's root: ours "bone", ufbx "null").
- **luce-fbx reads, ufbx rejects:** synthetic files ufbx refuses on purpose
  (cycles, depth limits), which luce-fbx reads.
