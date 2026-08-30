"""Copy to config.py or use as a reference for customization."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
ASSET_DIR = ROOT / "assets"
CACHE_DIR = ROOT / ".cache"
PREVIEW_DIR = ROOT / "preview"

PROFILE = {
    "github_username": "your-username",
    "display_name": "Your Name",
    "bio": "AI Engineer · Automation Architect · System Builder",
    "location": "",
    "website": "https://example.com",
    "theme": "cyber_cyan",
    "skills": ["Python", "Systems", "Automation"],
    "technologies": ["Python", "SQL", "AI"],
    "achievements": ["Achievement one"],
    "current_projects": ["Project one"],
    "contact": "",
    "status": "BUILDING",
}

CONTRIBUTIONS = {
    "seed": 20260831,
    "matrix": None,  # Replace with a 53x7 matrix of values 0..4 for explicit data.
}

DESIGN = {
    "animation_speed": 1.0,
    "ascii_density": 92,
    "ascii_ramp": "@#S%?*+;:,. ",
    "terminal_width": 620,
    "terminal_height": 360,
    "info_width": 520,
    "info_height": 360,
    "graph_width": 1180,
    "graph_height": 190,
    "card_radius": 22,
    "cell_size": 13,
    "cell_gap": 4,
    "font_mono": "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace",
    "font_sans": "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif",
    "glow": True,
}

# Import THEMES and README constants from the production config after copying this file.
