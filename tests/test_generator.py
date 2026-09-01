from pathlib import Path
import tempfile

import config
import generator


def test_theme_is_valid():
    assert config.PROFILE["theme"] in config.THEMES


def test_contribution_matrix_shape_and_range():
    matrix = generator.contribution_matrix()
    assert len(matrix) == 53
    assert all(len(column) == 7 for column in matrix)
    assert all(0 <= value <= 4 for column in matrix for value in column)


def test_escape_xml():
    assert generator.esc('<hello & "world">') == '&lt;hello &amp; &quot;world&quot;&gt;'


def test_generated_svgs_are_valid_xml():
    import xml.etree.ElementTree as ET

    with tempfile.TemporaryDirectory() as tmp:
        original = generator.OUTPUT_DIR
        try:
            generator.OUTPUT_DIR = Path(tmp)
            generator.ensure_dirs()
            for name, builder in (
                ("terminal-card.svg", generator.terminal_svg),
                ("info-card.svg", generator.info_svg),
                ("github-contribution-animation.svg", generator.contribution_svg),
            ):
                content = builder()
                path = Path(tmp) / name
                path.write_text(content, encoding="utf-8")
                ET.parse(path)
        finally:
            generator.OUTPUT_DIR = original
