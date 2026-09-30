#!/usr/bin/env python3
"""luce-fbx's benchmark: builds bench/main.lucb with --native --opt 3, runs
it and prints a Markdown table (case, milliseconds, count). Pass --runs N to
keep each case's best of N runs, and FBX files to time their loads too."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXE = ".exe" if os.name == "nt" else ""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path(os.environ.get("LUCE_BASE", ROOT.parent / f"luce-base/build/luce-base{EXE}")))
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("files", nargs="*", type=Path, help="FBX files whose loads are timed as well")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="luce-fbx-bench-") as temporary:
        binary = Path(temporary) / f"bench{EXE}"
        env = dict(os.environ, LUCE_CACHE=str(Path(temporary) / "cache"))
        subprocess.run([str(args.base.resolve()), "build", str(ROOT / "bench/main.lucb"), "--native", "--opt", "3", "-o", str(binary)],
                       check=True, env=env, timeout=900)
        best = {}
        order = []
        for _ in range(args.runs):
            output = subprocess.run([str(binary), *[str(f.resolve()) for f in args.files]], check=True, capture_output=True, text=True, timeout=900).stdout
            for line in output.splitlines():
                name, milliseconds, count = line.split("\t")[:3]
                if name not in best:
                    order.append(name)
                    best[name] = (float(milliseconds), count)
                elif float(milliseconds) < best[name][0]:
                    best[name] = (float(milliseconds), count)
    print("| Case | Time | Count |\n|---|---:|---:|")
    for name in order:
        milliseconds, count = best[name]
        print(f"| {name} | {milliseconds:.1f} ms | {int(count):,} |")


if __name__ == "__main__":
    main()
