#!/usr/bin/env python3
"""luce-fbx's gate: the Base module checks (tests/main.lucb) at native
optimization levels and through the C backend, then the Luce API tests
(tests/api/main.luc) native and through C. They run in a scratch directory
holding tests/fixtures and the generated fixtures."""
import argparse
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
EXE = ".exe" if os.name == "nt" else ""


def prepare(work):
    fixtures = work / "tests/fixtures"
    shutil.copytree(ROOT / "tests/fixtures", fixtures)
    spec = importlib.util.spec_from_file_location("generate_fixtures", ROOT / "tests/generate_fixtures.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.write_fixtures(fixtures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, default=Path(os.environ.get("LUCE_BASE", ROOT.parent / f"luce-base/build/luce-base{EXE}")))
    parser.add_argument("--luce", type=Path, default=Path(os.environ.get("LUCE", ROOT.parent / f"luce/build/luce{EXE}")))
    parser.add_argument("--opt", type=int, choices=range(4), help="one native level (default: 0 and 2) and C in release")
    args = parser.parse_args()
    levels = [args.opt] if args.opt is not None else [0, 2]
    modes = [["--native", "--opt", str(level)] for level in levels]
    modes += [["--backend=c"] + (["--release"] if args.opt is None or args.opt >= 2 else [])]
    with tempfile.TemporaryDirectory(prefix="luce-fbx-tests-") as temporary:
        work = Path(temporary)
        prepare(work)
        env = dict(os.environ, LUCE_BASE=str(args.base.resolve()), LUCE_CACHE=str(work / "cache"))
        binary = work / f"checks{EXE}"
        for flags in modes:
            print("TEST checks", " ".join(flags), flush=True)
            subprocess.run([str(args.base.resolve()), "build", str(ROOT / "tests/main.lucb"), *flags, "-o", str(binary)],
                           check=True, env=env, timeout=900)
            subprocess.run([str(binary)], check=True, timeout=900, cwd=work)
        for flags in (["--native", "--opt", str(levels[-1])], ["--backend=c"]):
            print("TEST api", " ".join(flags), flush=True)
            subprocess.run([str(args.luce.resolve()), "build", str(ROOT / "tests/api/main.luc"), *flags, "-o", str(binary)],
                           check=True, env=env, timeout=900)
            subprocess.run([str(binary)], check=True, timeout=600, cwd=work)
    print("PASS luce-fbx", flush=True)


if __name__ == "__main__":
    main()
