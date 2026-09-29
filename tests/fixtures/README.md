# FBX fixtures

`blender_279_default_7400_binary.fbx` comes from
https://github.com/ufbx/ufbx/blob/v0.20.0/data/blender_279_default_7400_binary.fbx
under the accompanying UFBX-LICENSE.txt (MIT alternative). It verifies a real
binary FBX mesh with the Base reader. No ufbx implementation is linked or shipped.

`tests/generate_fixtures.py` writes the original compressed/uncompressed
7.4/7.5 variants and the corrupt and truncated files at test time.
