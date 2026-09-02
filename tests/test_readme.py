from pathlib import Path

from config import README_MARKER_END, README_MARKER_START, README_PATH


def test_readme_generated_section_is_well_formed() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    assert text.count(README_MARKER_START) == 1
    assert text.count(README_MARKER_END) == 1
    start = text.index(README_MARKER_START)
    end = text.index(README_MARKER_END)
    assert start < end
    generated = text[start:end]
    assert "terminal-card.svg" in generated
    assert "info-card.svg" in generated
    assert "github-contribution-animation.svg" in generated


def test_readme_links_generated_assets_with_relative_paths() -> None:
    text = README_PATH.read_text(encoding="utf-8")
    for asset in (
        "output/terminal-card.svg",
        "output/info-card.svg",
        "output/github-contribution-animation.svg",
    ):
        assert asset in text
        assert Path(asset).exists()
