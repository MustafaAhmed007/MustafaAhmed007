from pathlib import Path

from core.research import DEFAULT_ASPECTS, research


def test_local_multi_aspect_research(tmp_path: Path) -> None:
    source = tmp_path / "notes.md"
    source.write_text("Architecture evidence and implementation notes.", encoding="utf-8")

    result = research("developer tooling", local_paths=[tmp_path])

    assert result.aspects == list(DEFAULT_ASPECTS)
    assert len(result.sources) == 1
    assert "Architecture evidence" in result.sources[0].content
    assert result.cloud_result is None


def test_markdown_output_preserves_source_metadata(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    source.write_text("Primary source content.", encoding="utf-8")

    result = research("test", local_paths=[source], aspects=["technical"])
    markdown = result.to_markdown()

    assert "## Sources" in markdown
    assert "Type: `local`" in markdown
    assert "Primary source content." in markdown
    assert "## Evidence Rule" in markdown
