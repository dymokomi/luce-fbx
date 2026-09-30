# luce-fbx

FBX for Luce, in **Luce Base**: binary and ASCII FBX files read into
luce-geocore `GeometrySet`s, and GeometrySets written as binary FBX.

```luce
from fbx import Fbx

let scene = Fbx.load("character.fbx")
let merged = Fbx.load("city.fbx", instancing = false, convert_units = true)
print(Fbx.warnings())
Fbx.save(scene, "copy.fbx")
```

`Fbx.load(path, keep_hierarchy, instancing, convert_units, normals)`:

- every model's mesh is merged into one mesh in world space, each face's model
  path in the text attribute `path` and its material in `material`;
- a mesh several models share becomes one prototype with an instance row per
  model (`instancing`, on by default);
- with `keep_hierarchy`, every model's mesh stays in its own space, placed by
  an instance row;
- `convert_units` turns the file Y-up and scales it to meters;
- `normals` imports the file's normals as `N`;
- `time` (seconds) or `frame` evaluates the first animation stack there;
- `deform` applies blend shapes and skins.

`Fbx.info(path)` summarizes a file: version, axes, units, frame rate, the
animation's time span and object counts.

`Fbx.save(set, path, version, deflate)` writes binary FBX 7.4 (or 7.5): the
mesh split by `path` into models with its layers and materials, instances as
models sharing their prototype's geometry, curves as lines and NURBS curves,
and the `fbx.*` details as the file's settings. Blender and ufbx read what it
writes; MAPPING.md's [Writing](docs/MAPPING.md#writing) has the details.

[docs/MAPPING.md](docs/MAPPING.md) states the whole mapping and what is left
out. [docs/PARITY.md](docs/PARITY.md) records the comparison with ufbx.

## What it reads

- Binary FBX 6.1 to 7.7 (32- and 64-bit records, big-endian files, raw and
  zlib arrays) and ASCII FBX 6.1 and 7.x. FBX 5 and older is refused.
- The object graph, property templates and global settings (axes, units,
  frame rate).
- The model hierarchy with FBX's full transform stack, matched to ufbx:
  translation, rotation offset and pivot, pre- and post-rotation, the six
  rotation orders, RotationActive, scaling offset and pivot, the three inherit
  types and geometric transforms.
- Meshes with every layer element (normals, tangents, binormals, UV sets,
  color sets, smoothing, edge and vertex creases, holes, edge visibility,
  materials) in every mapping and reference mode.
- Line and NURBS curves, as geocore curves.
- Animation at a time: curves with every interpolation, tangent and
  extrapolation mode, and layers; blend shapes with in-betweens; linear, dual
  quaternion and blended skins.

Known gap: FBX 6 takes (legacy animation) are not read; such files import at
their rest values with a warning (docs/MAPPING.md, "What is left out").

## How it is built

- `document/`: one flat node table for both encodings; arrays are recorded, not
  decoded, and every array an import needs decodes in one parallel batch
  (zlib per array, raw arrays in slices, ASCII in counted pieces) on
  luce-geocore's pool.
- `scene/`: objects, connections, templates, settings, the hierarchy and its
  transforms.
- `convert/`: the GeometrySet: meshes merged in parallel passes, layers as
  attributes, instances, curves.
- `writer/`: a GeometrySet as a node tree (meshes by path, layers,
  materials, models, instances, curves), then encoded with its arrays
  deflated in parallel.

Every size a file declares is checked against the bytes that hold it (a zlib
array against what its stream can inflate to) and the whole load against
physical memory; there is no fixed cap. Malformed files fail with an error,
never a trap.

## Tests

`./test.sh` runs the Base checks (tests/main.lucb, native at opt 0 and 2 and
through C) under a heap that counts live blocks and fails each allocation in
turn, then the Luce API tests (tests/api). They cover the fixtures in
tests/fixtures (ufbx's test files under its MIT license, and ours), one cube
in six encodings, every truncation of a file, a byte-corruption sweep through
the import, the transform stack against ufbx's matrices, and the conversion
against ufbx's counts and sums, and saves read back (bit-exact points,
layers, materials, curves, instance rows, 7500 and raw arrays, a
1000-corner n-gon). `tools/fbxdump` prints what luce-fbx reads in the form
the local ufbx parity oracle prints; `--save` also writes it, for the local
round-trip checks against ufbx and Blender.

Apache-2.0 or MIT.
