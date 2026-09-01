from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

OUTPUT_DIR = Path("output")
ASSETS = (
    "terminal-card.svg",
    "info-card.svg",
    "github-contribution-animation.svg",
)


def validate_svg(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
        root = ET.fromstring(text)
    except Exception as exc:
        return [f"XML parse failure: {exc}"]

    issues: list[str] = []
    ids = re.findall(r'\bid="([^"]+)"', text)
    duplicates = sorted({value for value in ids if ids.count(value) > 1})
    if duplicates:
        issues.append("duplicate IDs: " + ", ".join(duplicates[:10]))

    if root.tag.split("}")[-1] != "svg":
        issues.append("root element is not SVG")

    for attribute in ("viewBox", "width", "height"):
        if not root.get(attribute):
            issues.append(f"missing SVG {attribute}")

    if len(text.encode("utf-8")) > 700_000:
        issues.append(f"large SVG: {len(text.encode('utf-8')) / 1024:.0f} KiB")

    lowered = text.lower()
    if "<script" in lowered or "javascript:" in lowered:
        issues.append("script/javascript detected")

    return issues


def main() -> int:
    failures = False
    for name in ASSETS:
        path = OUTPUT_DIR / name
        issues = ["missing file"] if not path.exists() else validate_svg(path)
        print(f"{name}: {'PASS' if not issues else 'FAIL'}")
        for issue in issues:
            print(f"  - {issue}")
        failures |= bool(issues)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
