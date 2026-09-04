from __future__ import annotations

import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def run(*args: str) -> None:
    print("+", " ".join(args))
    subprocess.check_call(args, cwd=ROOT)


def main() -> int:
    print("Developer Command Center bootstrap")
    print(f"Platform: {platform.system()} | Python: {sys.version.split()[0]}")

    if sys.version_info < (3, 10):
        print("ERROR: Python 3.10 or newer is required.")
        return 2

    if not PYTHON.exists():
        run(sys.executable, "-m", "venv", str(VENV))

    run(str(PYTHON), "-m", "pip", "install", "--upgrade", "pip")
    run(str(PYTHON), "-m", "pip", "install", "-r", "requirements.txt")
    run(str(PYTHON), "-m", "pip", "install", "-e", ".[test]")
    run(str(PYTHON), "scripts/quality_gate.py")

    print("\nBOOTSTRAP: PASS")
    print(f"Virtual environment: {VENV}")
    print("Run the generator with:")
    print(f"  {PYTHON} generator.py")
    print("Run research with:")
    print(f"  {PYTHON} research.py \"your topic\" --local .")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
