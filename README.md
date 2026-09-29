# luce-fbx

An original **Luce Base** static polygon geometry reader. Public export:
`fbx.Fbx.load(path)` and `fbx.Fbx.decode_ascii(text)` return `geocore.PolygonMesh`.

The current contract is **raw mesh-local geometry**, not a reconstructed FBX
scene. It reads positions and polygons from ASCII 7.x arrays and binary 7.x nodes,
including the 7.5+ 64-bit node headers and zlib-compressed numeric arrays. Deflate
uses `luce-compress`, itself Base code. Multiple geometry definitions are merged.

Scene hierarchy/instances, node/geometric transforms, axis/unit conversion,
normals/UVs/materials, animation, skinning and blend shapes are not implemented.
Consequently a multi-object scene may overlap at its mesh-local origins. The
File node labels this explicitly. This package is an import foundation, not
general FBX compatibility or an Autodesk SDK replacement.

Reads at most 32 MiB and enforces modeling mesh limits. Binary offsets, parent
bounds, array lengths/encodings and polygon indices are checked. ASCII 6.x legacy
arrays are not supported. No texture or referenced file is opened automatically.

`./test.sh` runs the Luce regressions in `tests/` native and through the C
backend: a pinned real Blender binary FBX fixture, generated
compressed/uncompressed 7.4/7.5 variants, corruption and truncation. CI pins the
compilers and sibling packages in `bootstrap/PACKAGES`. All runtime code is Base; donor C code remains outside the package.
