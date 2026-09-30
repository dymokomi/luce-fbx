# FBX and GeometrySet

How `Fbx.load` turns an FBX scene into a luce-geocore `GeometrySet`. The code
is in `src/luce_fbx/convert/`.

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

A row is a translation, an XYZ rotation and a scale. A model whose matrix
shears (non-uniform scale under rotation) cannot be a row; its mesh is merged
instead. Nulls, bones, cameras and lights have no geometry here.

A mirroring matrix (negative determinant) reverses each face's corners after
the first. Faces of fewer than 3 corners are dropped; faces of more than 256
corners are triangulated (geocore's current limit), both with a warning.

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

## Scene settings

The set's detail attributes record `fbx.upAxis` and `fbx.frontAxis` ("+Y",
"-Z", ...), `fbx.metersPerUnit` (UnitScaleFactor / 100) and `fbx.frameRate`.
With `convert_units`, the scene is turned from its axes to Y-up, +Z front,
right-handed and scaled to meters, and the details say +Y and 1.

## What is left out

- Animation, blend shapes and skins (the rest pose is imported).
- Cameras, lights, constraints and other node attributes.
- Material properties and textures (only the material name).
- NURBS surfaces and patches.
- User data layers and custom properties.
- FBX 5 and older, and FBX 8.
