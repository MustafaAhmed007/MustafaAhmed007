from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable


DEFAULT_ASPECTS = (
    "landscape",
    "technical",
    "implementation",
    "positioning",
    "discovery",
)


@dataclass
class Source:
    kind: str
    locator: str
    title: str
    content: str
    status: str = "ok"


@dataclass
class ResearchResult:
    topic: str
    aspects: list[str]
    sources: list[Source] = field(default_factory=list)
    cloud_result: str | None = None

    def to_dict(self) -> dict:
        return {
            "topic": self.topic,
            "aspects": self.aspects,
            "sources": [asdict(source) for source in self.sources],
            "cloud_result": self.cloud_result,
        }

    def to_markdown(self) -> str:
        lines = [f"# Auto Research: {self.topic}", "", "## Research Aspects", ""]
        lines.extend(f"- {aspect}" for aspect in self.aspects)
        lines.extend(["", "## Sources", ""])
        for source in self.sources:
            lines.extend(
                [
                    f"### {source.title}",
                    f"- Type: `{source.kind}`",
                    f"- Locator: `{source.locator}`",
                    f"- Status: `{source.status}`",
                    "",
                    source.content[:4000].strip(),
                    "",
                ]
            )
        if self.cloud_result:
            lines.extend(["## Optional Cloud Research", "", self.cloud_result.strip(), ""])
        lines.extend(
            [
                "## Evidence Rule",
                "",
                "Local and direct-URL material is preserved as inspectable source evidence. "
                "Cloud output is optional enrichment and must not be treated as verified fact "
                "without source evidence.",
            ]
        )
        return "\n".join(lines) + "\n"


class _HTMLTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self.skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            text = re.sub(r"\s+", " ", data).strip()
            if text:
                self.parts.append(text)


def _html_to_text(raw: str) -> str:
    parser = _HTMLTextParser()
    parser.feed(raw)
    return "\n".join(parser.parts)


def _read_local(path: Path) -> Source:
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        return Source("local", str(path), path.name, content)
    except OSError as exc:
        return Source("local", str(path), path.name, "", f"error: {exc}")


def _fetch_url(url: str, timeout: int = 15) -> Source:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "DeveloperCommandCenter/1.0 research-engine"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read(2_000_000).decode("utf-8", errors="replace")
            content_type = response.headers.get("Content-Type", "")
            content = _html_to_text(raw) if "html" in content_type.lower() else raw
            return Source("url", url, url, content)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return Source("url", url, url, "", f"error: {exc}")


def _cloud_research(topic: str, aspects: Iterable[str], endpoint: str, timeout: int = 30) -> str:
    payload = json.dumps({"topic": topic, "aspects": list(aspects)}).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "DeveloperCommandCenter/1.0 research-engine",
        },
        method="POST",
    )
    token = os.getenv("RESEARCH_CLOUD_TOKEN")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(1_000_000).decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return f"Cloud research unavailable: {exc}"


def research(
    topic: str,
    aspects: Iterable[str] | None = None,
    local_paths: Iterable[str | Path] = (),
    urls: Iterable[str] = (),
    cloud_endpoint: str | None = None,
) -> ResearchResult:
    selected_aspects = list(aspects or DEFAULT_ASPECTS)
    result = ResearchResult(topic=topic, aspects=selected_aspects)

    for raw_path in local_paths:
        path = Path(raw_path)
        if path.is_file():
            result.sources.append(_read_local(path))
        elif path.is_dir():
            for candidate in sorted(path.rglob("*")):
                if candidate.is_file() and candidate.suffix.lower() in {".md", ".txt", ".json", ".py", ".toml", ".yaml", ".yml"}:
                    result.sources.append(_read_local(candidate))

    for url in urls:
        result.sources.append(_fetch_url(url))

    endpoint = cloud_endpoint or os.getenv("RESEARCH_CLOUD_ENDPOINT")
    if endpoint:
        result.cloud_result = _cloud_research(topic, selected_aspects, endpoint)

    return result
