# FBX and GeometrySet

How `Fbx.load` turns an FBX scene into a luce-geocore `GeometrySet` (the
code is in `src/luce_fbx/convert/`), and how `Fbx.save` writes one back
([Writing](#writing), `src/luce_fbx/writer/`).

## Models and meshes

Every model's mesh (a Geometry of subclass Mesh connected to it; FBX 6 keeps
the mesh in the Model itself) is a *use* of that mesh. A GeometrySet holds one
component per family, so uses are merged, as luce-usd merges prims:

- **Merge** (the default): every use's points are placed by its model's world
  matrix times the model's geometric transform, in f64, over the mesh's origin,
  and its faces join one mesh. Each face keeps its model's path in the text
  attribute `path` ("/Parent/Child"; a name repeated among siblings takes
  "_2", "_3" in file order).
- **Instancing** (on by default): a mesh several models share (with the same
  materials) is loaded once as a prototype, in its own space, and each model
  is an instance row placing it.
- **Keep hierarchy**: every model's mesh is an instance row placing its own
  prototype (shared ones shared when Instancing is on).

A row is a translation, an XYZ rotation and a scale, and its model's path
is the row attribute `path`. A model whose matrix shears (non-uniform scale
under rotation) cannot be a row; its mesh is merged instead. Nulls, bones, cameras and lights have no geometry here.

A mirroring matrix (negative determinant) reverses each face's corners after
the first. Faces of fewer than 3 corners are dropped, with a warning; faces of
any larger size stay as they are.

## Layer elements

| Layer element | Attribute |
|---|---|
| `Vertices`, `PolygonVertexIndex` | points and faces (a face ends at a negative ~index) |
| Normal | `N` (role normal); later sets `N2`, `N3`, ... |
| Tangent / Binormal | `tangentu` / `tangentv` |
| UV | `uv`, `uv2`, ... (sets in their element order) |
| Color | `Cd` (RGB, role color) and `Alpha`; later sets `Cd2`/`Alpha2`, ... |
| Smoothing by polygon | face i32 `smoothing_group` |
| Smoothing by edge | edge group `sharp` (edges whose smoothing is 0) |
| EdgeCrease | edge `crease`, x10 (FBX 1 is infinitely sharp, geocore 10) |
| VertexCrease | point `corner_sharpness`, x10 |
| Hole | face group `hole` |
| Visibility by edge | edge group `hidden` (edges whose visibility is 0) |
| Material | face text `material`: the name of the model's n-th connected material |

The domain follows the mapping: ByPolygonVertex is the corner domain,
ByVertex the point domain, ByPolygon and AllSame the face domain, ByEdge the
edge domain (through the mesh's `Edges` array). When merged meshes map one
attribute differently, the corner domain holds them all. Meshes without an
attribute leave their elements zero.

As ufbx reads them: IndexToDirect values go through their index; an index
past the values (or a value array shorter than its mapping) clamps to the last
value; a ByPolygon layer with a value per polygon vertex is read by polygon
vertex.

## Curves

- A `Line` geometry's `Points` joined by `PointsIndex` runs are poly curves.
- A `NurbsCurve` keeps its order, its knot vector (as custom knots) and its
  weights (`w`). A closed curve repeats its first point after its last, a
  periodic one its first order - 1 points, so it evaluates as the same open
  curve over the knots' inner range.
- Each curve's model path is its `path`.

## Animation and deformers

With a `time` (seconds) or `frame` (at the file's frame rate), the first
AnimationStack is evaluated there, as ufbx evaluates it:

- keys and tangents decode as ufbx decodes them: constant (previous or next),
  linear and cubic keys; automatic (with bias, time-independent and
  clamp-progressive), TCB and user tangents; weighted tangents; ASCII files'
  attribute bits from FBX 7.2 on;
- a cubic segment is a Bezier in time and value, solved for its time;
- before and after the keys, curves hold, extend their slope, repeat, repeat
  relative or mirror, as many times as their Repetition says;
- layers combine in order: the first replaces the property's value, later
  ones override, blend by their weight (animated in the layer itself) or add;
  rotations and scales compose as rotations (quaternion slerp) and products
  where the layer's accumulation mode asks;
- every transform property of a model animates: translation, rotation,
  scaling, pre- and post-rotation, pivots and offsets.

Without a time, the file's property values are read as they are. In both
cases (and unless `deform` is off) deformers apply:

- **Blend shapes**: each BlendShapeChannel's shapes are keyframes at their
  FullWeights; the two around its DeformPercent share it linearly (in-between
  shapes), and their offsets are added to the mesh's points. Blender's binary
  exporter writes FullWeights as per-offset weights, which are applied so.
- **Skins**: each cluster maps the mesh to its bone (Transform, the geometric
  transform, the bone's world matrix; TransformLink or the bind pose when
  Transform is missing). A point takes its clusters' matrices averaged by
  weight, dual quaternions for dual quaternion skins, or both by BlendWeights
  for blended ones, normalized by its total weight; a point without weights
  keeps the mesh's world transform. A skinned mesh is placed in world space,
  never instanced, and its normals and tangents turn with each point's skin
  matrix.

The details record `fbx.time` when a time is given.

## Scene settings

The set's detail attributes record `fbx.upAxis` and `fbx.frontAxis` ("+Y",
"-Z", ...), `fbx.metersPerUnit` (UnitScaleFactor / 100) and `fbx.frameRate`.
With `convert_units`, the scene is turned from its axes to Y-up, +Z front,
right-handed and scaled to meters, and the details say +Y and 1.

## What is left out

- Animation beyond one time: one pose is imported.
- FBX 6 takes (a known gap, legacy): FBX 6.1 files keep their animation in
  a Takes section this reader does not decode. Such a file imports at its
  rest values with the warning "FBX 6 takes (animation) are not read"; FBX 7
  animation is read in full. These files are the animated mismatches in
  PARITY.md.
- Skeletons as data: bones place skinned points but are not imported.
- Cameras, lights, constraints and other node attributes.
- Material properties and textures (only the material name).
- NURBS surfaces and patches.
- User data layers and custom properties.
- FBX 5 and older, and FBX 8.

## Writing

`Fbx.save(set, path, version, deflate)` writes binary FBX: 7400 by default
(7500 when asked, or when the file needs 64-bit offsets), laid out as
Blender's exporter writes it (header, FBXHeaderExtension with a fixed 1970
timestamp so saves are reproducible, GlobalSettings, Documents, References,
Definitions, Objects, Connections, Takes). Arrays over 128 bytes are
deflated (zlib level 1) one pool task each, a large one by luce-compress in
1 MiB segments on several threads (one stream, which luce-compress also
inflates in parallel); `deflate = false` stores them raw.

- **Meshes.** Faces are grouped by their `path` text. Each group is one
  Geometry and one Model at that path (its names split at `/`; missing
  ancestors are Null models); faces without a path go to a model named
  `mesh`. Points are written in world space (f64, the mesh origin added
  back), so models have identity transforms; a mesh of one group keeps its
  point order (unused points too). `PolygonVertexIndex` ends each face with
  ~index; `Edges`, each edge's first polygon vertex, is written when an
  edge layer needs it.
- **Layer elements**, the reverse of the table above, their values f32
  whatever the attribute holds (what FBX consumers keep; half the bytes of
  f64): `N*` Normal, `tangentu*`/`tangentv*` Tangent/Binormal, `uv*` UV and
  `Cd*` with `Alpha*` Color (RGBA), all Direct,
  `smoothing_group` or else `sharp` Smoothing (a mesh with neither and no
  normals is written flat, as geocore shows it), `crease` and
  `corner_sharpness` EdgeCrease and VertexCrease (/ 10), `hole` Hole,
  `hidden` Visibility. The mapping follows the domain (point ByVertice,
  corner ByPolygonVertex, face ByPolygon, edge ByEdge). Set k of each goes
  in Layer k.
- **Materials.** Each distinct `material` text is one Material (Phong,
  grey), connected to the models using it in the order their layer indexes
  them (AllSame when a model uses one). Faces without a material text use
  one named `default`; a model whose faces have none gets no material.
- **Instances.** A prototype set is written once. Each row is a Model with
  its Lcl Translation, Lcl Rotation (geocore's XYZ angles turned into FBX's
  XYZ order, degrees) and Lcl Scaling, and Visibility 0 when hidden: the
  prototype's one mesh model itself when it has nothing else (sharing its
  Geometry, FBX's own instancing), else a Null holding the prototype's
  models. A row with a `path` row attribute is that model, under its
  ancestors' models (Nulls, or rows placed earlier, relative to which it is
  then placed); rows are placed before geometry, and geometry under a
  placed row takes the row's inverse placement (when that is not a
  translation, rotation and scale, it goes under the root by its last
  name). A row without a path is named after its prototype's.
- **Curves.** A path's poly curves share one Line (a cyclic curve closes on
  its first point). Every other curve is a NurbsCurve: NURBS keep their
  order, knots and weights (cyclic ones Periodic, their knots with the
  wrapped tail); Bezier and Catmull-Rom curves are written as the same cubic
  NURBS curve (Catmull-Rom tangents (next - previous) / 2).
- **Settings.** `fbx.upAxis`, `fbx.frontAxis`, `fbx.metersPerUnit` and
  `fbx.frameRate` details (as a load records them) become UpAxis, FrontAxis,
  CoordAxis (up x front), UnitScaleFactor (x 100), TimeMode and
  CustomFrameRate; without them the file is Y-up, +Z front, meters, 24 fps.

What does not survive: other attributes (a warning names each), point
clouds, volumes, SDFs and CAD (a warning per component), animation, skins
and blend shapes (a deformed load writes the deformed points), cameras,
lights and material properties.

Every file of the corpus that loads (765 of 786) saves and reads back the
same in ufbx and in luce-fbx: faces, corners, position sums, normals, UV
and color sets and materials per path, at 7400 and 7500; with instances or
Keep hierarchy, the same faces and positions overall, and the same model
paths in all but 2 (instances) and 6 (Keep hierarchy) files: sheared
models under placed rows, and duplicate ids. Blender 5.1 imports
755 of them the same (faces, corners, positions); the other 10 are
synthetic files with NaN points or degenerate faces Blender drops.
