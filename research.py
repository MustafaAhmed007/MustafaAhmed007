from __future__ import annotations

import argparse
from pathlib import Path

from core.research import DEFAULT_ASPECTS, research


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run evidence-preserving multi-aspect research with local, URL, and optional cloud sources."
    )
    parser.add_argument("topic", help="Research topic")
    parser.add_argument("--aspect", action="append", dest="aspects", help="Research aspect; repeat as needed")
    parser.add_argument("--local", action="append", default=[], help="Local file or directory; repeat as needed")
    parser.add_argument("--url", action="append", default=[], help="Direct URL source; repeat as needed")
    parser.add_argument("--cloud-endpoint", help="Optional HTTP JSON research endpoint")
    parser.add_argument("--out", default="preview/research.md", help="Markdown output path")
    parser.add_argument("--json-out", help="Optional JSON output path")
    args = parser.parse_args()

    result = research(
        args.topic,
        aspects=args.aspects or DEFAULT_ASPECTS,
        local_paths=args.local,
        urls=args.url,
        cloud_endpoint=args.cloud_endpoint,
    )

    output = Path(args.out)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(result.to_markdown(), encoding="utf-8")

    if args.json_out:
        import json

        json_output = Path(args.json_out)
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")

    print(f"RESEARCH: wrote {output}")
    print(f"RESEARCH: sources={len(result.sources)} cloud={'enabled' if result.cloud_result else 'disabled'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
