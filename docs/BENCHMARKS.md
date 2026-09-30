# Benchmarks

`bench/run.py [FILES...]` builds bench/main.lucb with `--native --opt 3` and
prints each case's best of three: geocore's .prism codec on the grid as the
reference, luce-fbx writing and reading the grid, and the load of any FBX
files named (from bytes in memory, file read excluded). The grid is
geocore's verb benchmark grid, 837×837 quads (702,244 points, 700,569 faces)
with a corner `uv`.

On the M-series Mac, Luce 0.8.24, luce-compress 0.3.0 (2026-09-30):

| Case | Time | Count | Target |
|---|---:|---:|---:|
| Reference: save the grid with uv to .prism (bytes) | 8.3 ms | 84,089,051 | |
| Reference: load that .prism (faces) | 17.9 ms | 700,569 | |
| write: the grid, deflated (bytes) | 32.0 ms | 11,117,548 | ≤ 60 ms |
| read: that file, deflated (faces) | 64.1 ms | 700,569 | ≤ 35 ms |
| write: the grid, raw arrays (bytes) | 17.7 ms | 53,287,596 | ≤ 25 ms |
| read: that file, raw arrays (faces) | 26.8 ms | 700,569 | ≤ 25 ms |
| read: grid_837.fbx, Blender 5.1's grid with f64 corner normals (faces) | 66.7 ms | 700,569 | ≤ 60 ms |
| read: tentacle_big.fbx, 512k faces skinned (faces) | 106.7 ms | 512,000 | ≤ 80 ms |
| read: robot_big.fbx (faces) | 58.1 ms | 353,490 | |

ufbx 0.20 (C, 8 threads) loads Blender's grid in 26 ms and the tentacle,
with its skin evaluated, in 805 ms.

The writes meet their targets: layer values go out as f32, UV and colors
Direct (no index), Edges only for edge layers, the arrays' pieces deflated
and copied into the file in parallel. The reads do not yet:

- A deflated read waits for its largest array to inflate on one core:
  flate inflates at about 600 MB/s against zlib's 1,350 MB/s, and the
  difference is code generation (the loop is libdeflate's shape; reported
  to the compiler).
- The rest is mostly luce-geocore's per-face work (normals and triangles),
  bound by calls the compiler does not yet inline; cross-module inlining
  is coming in Luce 0.8.25.
