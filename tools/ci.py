"""Local CI: every quality gate, run on this machine. No hosted CI service is used.

Usage:
    uv run python tools/ci.py            # fast gates: tests, docs, lint, dependency audit
    uv run python tools/ci.py --full     # also the end-to-end checks with real shells (vim, throughput, resize)
    uv run python tools/ci.py --linux    # on Windows: also run the gates on Linux through WSL

Exit code 0 means every gate passed. A summary table is printed at the end.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUFF_RULES = ["--select", "E,F,W,B,S", "--ignore", "S101,S110,S603,S604,S607,S311,E501"]


def run(name: str, cmd: list[str], results: list, env: dict | None = None) -> bool:
    print(f"\n=== {name}\n$ {' '.join(cmd)}", flush=True)
    start = time.monotonic()
    proc = subprocess.run(cmd, cwd=ROOT, env=env)
    ok = proc.returncode == 0
    results.append((name, ok, time.monotonic() - start))
    return ok


def audit(results: list) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        req = Path(tmp) / "requirements.txt"
        exported = subprocess.run(["uv", "export", "--no-dev", "--no-hashes", "--no-emit-project", "-q", "-o", str(req)],
                                  cwd=ROOT)
        if exported.returncode != 0:
            results.append(("dependency audit", False, 0.0))
            return
        run("dependency audit (pip-audit)", ["uvx", "pip-audit", "-r", str(req)], results)


def linux(results: list, full: bool) -> None:
    """Copy the project into the WSL home folder (Linux file system, Linux virtual environment) and run there."""
    if sys.platform != "win32" or not shutil.which("wsl.exe"):
        results.append(("linux (WSL)", False, 0.0))
        print("WSL is not available", file=sys.stderr)
        return
    drive, rest = ROOT.drive.rstrip(":").lower(), ROOT.as_posix().split(":", 1)[1]
    script = f"/mnt/{drive}{rest}/tools/ci_linux.sh"
    run("linux (WSL): all gates", ["wsl.exe", "bash", script, *(["--full"] if full else [])], results)


def main() -> int:
    args = set(sys.argv[1:])
    full, with_linux, with_audit = "--full" in args, "--linux" in args, "--no-audit" not in args
    env = dict(os.environ)
    env.pop("VIRTUAL_ENV", None)
    results: list[tuple[str, bool, float]] = []

    run("unit, screen and app tests", ["uv", "run", "pytest", "-q"], results, env)
    run("reference docs match the code", ["uv", "run", "python", "tools/gen_docs.py", "--check"], results, env)
    run("lint and security rules (ruff)", ["uvx", "ruff", "check", "src", "tests", "tools", *RUFF_RULES], results, env)
    if with_audit:
        audit(results)
    if full:
        out = tempfile.mkdtemp(prefix="mindas-terminal-e2e-")
        run("end-to-end with real shells", ["uv", "run", "python", "spike/check.py", out], results, env)
    if with_linux:
        linux(results, full)

    print(f"\n{'gate':<42} {'result':<8} time")
    for name, ok, seconds in results:
        print(f"{name:<42} {'PASS' if ok else 'FAIL':<8} {seconds:6.1f}s")
    failed = [n for n, ok, _ in results if not ok]
    print("\nall gates passed" if not failed else f"\nFAILED: {', '.join(failed)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
