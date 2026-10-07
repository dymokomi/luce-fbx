"""Regenerate the generated_*.fbx files in tests/fixtures. Original tiny binary FBX fixtures; no external parser or SDK required: a
triangle Geometry under a Model, in FBX 7.4 and 7.5, arrays raw and zlib, plus
a corrupt and a truncated copy."""
from pathlib import Path
import struct
import zlib


def write_fixtures(directory):
    def array(kind, values, code, compressed):
        raw = struct.pack("<" + code * len(values), *values)
        payload = zlib.compress(raw) if compressed else raw
        return kind + struct.pack("<III", len(values), int(compressed), len(payload)) + payload

    def string(text):
        encoded = text.encode("latin-1")
        return b"S" + struct.pack("<I", len(encoded)) + encoded

    def long(value):
        return b"L" + struct.pack("<q", value)

    for version in (7400, 7500):
        for compressed in (False, True):
            wide = version >= 7500
            width = 25 if wide else 13
            null = bytes(width)

            def node(name, props, children, start):
                encoded = name.encode("ascii")
                header = width + len(encoded)
                body = b"".join(props)
                for child in children:
                    body += node(*child, start + header + len(body))
                if children:
                    body += null
                end = start + header + len(body)
                counts = struct.pack("<QQQ" if wide else "<III", end, len(props), sum(len(p) for p in props))
                return counts + bytes([len(encoded)]) + encoded + body

            vertices = array(b"d", [0, 0, 0, 1, 0, 0, 0, 1, 0], "d", compressed)
            indices = array(b"i", [0, 1, -3], "i", compressed)
            geometry = ("Geometry", [long(1), string("Triangle\x00\x01Geometry"), string("Mesh")],
                        [("Vertices", [vertices], []), ("PolygonVertexIndex", [indices], [])])
            model = ("Model", [long(2), string("Triangle\x00\x01Model"), string("Mesh")], [])
            objects = ("Objects", [], [geometry, model])
            connections = ("Connections", [], [("C", [string("OO"), long(1), long(2)], []),
                                               ("C", [string("OO"), long(2), long(0)], [])])
            header = b"Kaydara FBX Binary  \x00\x1a\x00" + struct.pack("<I", version)
            payload = header
            for top in (objects, connections):
                payload += node(*top, len(payload))
            payload += null
            (directory / f"generated_{version}_{int(compressed)}.fbx").write_bytes(payload)
            if version == 7400 and not compressed:
                corrupted = bytearray(payload)
                struct.pack_into("<I", corrupted, 27, 0x7fffffff)
                (directory / "generated_bad_offset.fbx").write_bytes(corrupted)
                (directory / "generated_truncated.fbx").write_bytes(payload[:40])


if __name__ == "__main__":
    write_fixtures(Path(__file__).resolve().parent / "fixtures")
