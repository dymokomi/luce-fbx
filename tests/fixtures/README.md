# FBX fixtures

From ufbx's test data (https://github.com/ufbx/ufbx, `data/`), under the
accompanying UFBX-LICENSE.txt (MIT alternative):

- `blender_279_default_7400_binary.fbx` (v0.20.0)
- `maya_cube_7400_binary.fbx`, `maya_cube_big_endian_7400_binary.fbx`,
  `maya_zero_end_7400_binary.fbx`, `maya_cube_6100_binary.fbx`,
  `maya_cube_6100_ascii.fbx`, `maya_cube_7500_ascii.fbx`: one cube in the
  encodings the reader must agree on.
- `blender_293_instancing_7400_binary.fbx` (eight models sharing a mesh),
  `blender_279_color_sets_7400_binary.fbx`,
  `blender_293x_subsurf_max_crease_7400_binary.fbx`,
  `max_edge_visibility_7500_binary.fbx`, `max_curve_line_7500_ascii.fbx`,
  `max_nurbs_curve_rational_7500_ascii.fbx`: the conversion checks;
  `blender_279_nested_meshes_7400_binary.fbx` (meshes nested three deep):
  the writer's hierarchy round trip.
- `maya_anim_extrapolation_7700_binary.fbx`, `maya_anim_layers_7500_binary.fbx`,
  `maya_auto_clamp_7700_ascii.fbx`, `maya_blend_inbetween_7500_binary.fbx`,
  `maya_dq_weights_7500_binary.fbx`: the animation checks (ufbx's values in
  tests/anim_checks.lucb).

Ours:

- `transforms_7500_ascii.fbx`: the transform stack (pivots, offsets, pre- and
  post-rotation, rotation orders, RotationActive, inherit types, geometric
  transforms, sibling names). tests/scene_checks.lucb holds the matrices ufbx
  computes for it.

`tests/generate_fixtures.py` writes a triangle under a Model in compressed
and uncompressed 7.4/7.5 variants, and corrupt and truncated copies, at test
time. No ufbx code is
linked or shipped; the comparison against ufbx runs locally.
