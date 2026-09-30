# FBX fixtures

From ufbx's test data (https://github.com/ufbx/ufbx, `data/`), under the
accompanying UFBX-LICENSE.txt (MIT alternative):

- `blender_279_default_7400_binary.fbx` (v0.20.0)
- `maya_cube_7400_binary.fbx`, `maya_cube_big_endian_7400_binary.fbx`,
  `maya_zero_end_7400_binary.fbx`, `maya_cube_6100_binary.fbx`,
  `maya_cube_6100_ascii.fbx`, `maya_cube_7500_ascii.fbx`: one cube in the
  encodings the reader must agree on.

Ours:

- `transforms_7500_ascii.fbx`: the transform stack (pivots, offsets, pre- and
  post-rotation, rotation orders, RotationActive, inherit types, geometric
  transforms, sibling names). tests/scene_checks.lucb holds the matrices ufbx
  computes for it.

`tests/generate_fixtures.py` writes the compressed/uncompressed 7.4/7.5
variants and the corrupt and truncated files at test time. No ufbx code is
linked or shipped; the comparison against ufbx runs locally.
