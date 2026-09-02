"""One-command quality gate for the Developer Command Center.

The gate intentionally exercises the real build path instead of only testing
individual helpers. A clean git diff after generation is the reproducibility
contract for checked-in generated assets.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    print(f"\n$ {' '.join(args)}")
    subprocess.run(args, cwd=ROOT, check=True)


def main() -> int:
    python = sys.executable
    run(python, "-m", "compileall", "-q", "config.py", "generator.py", "validate_assets.py", "scripts", "tests")
    run(python, "-m", "pytest", "-q")
    run(python, "generator.py")
    run(python, "validate_assets.py")
    run(python, "generator.py", "--validate")

    # Generated SVGs and the README auto-section are source-controlled
    # artifacts. A fresh build must not introduce an uncommitted diff.
    run("git", "diff", "--exit-code", "--", "README.md", "output", "preview")
    print("\nQUALITY GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
