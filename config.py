from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"
ASSET_DIR = ROOT / "assets"
CACHE_DIR = ROOT / ".cache"
PREVIEW_DIR = ROOT / "preview"

PROFILE = {
    "github_username": "MustafaAhmed007",
    "display_name": "Mustafa Ahmed",
    "bio": "AI Systems Architect · Automation Engineer",
    "location": "",
    "website": "",
    "theme": "cyber_cyan",
    "skills": [
        "AI Systems",
        "Automation",
        "Python",
        "SQL",
        "Data Analysis",
        "Product Engineering",
        "Developer Experience",
    ],
    "technologies": [
        "Python",
        "SQL",
        "GitHub",
        "AI",
        "Automation",
        "Data Science",
    ],
    "achievements": [
        "System-first engineering",
        "Automation workflows",
        "Product engineering",
    ],
    "current_projects": [
        "AI automation systems",
        "Developer tooling",
        "Intelligent products",
    ],
    "contact": "engrmustafa0007@gmail.com",
    "status": "BUILDING",
}

# Public proof-of-work registry.
# Add a project only when its implementation, artifact, demo, or case study
# is actually inspectable. This prevents the profile from becoming a claim list.
PROJECTS = [
    {
        "name": "Developer Command Center",
        "type": "FLAGSHIP SYSTEM",
        "problem": "A GitHub profile should communicate identity, capability, and proof—not just a bio.",
        "built": "A deterministic Python + SVG generation pipeline for a configurable developer profile.",
        "outcome": "Versionable, reproducible profile presentation with reusable visual modules.",
        "repo": "https://github.com/MustafaAhmed007/MustafaAhmed007",
        "status": "SHIPPED",
    },
]

CONTRIBUTIONS = {"seed": 20260831, "matrix": None}

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

THEMES = {
    "cyber_cyan": {
        "bg": "#0d1117", "panel": "#111923", "panel2": "#0b121a", "border": "#263445",
        "white": "#f4f7fb", "muted": "#8b9aaa", "cyan": "#22d3ee", "green": "#39d353",
        "orange": "#ff9f43", "purple": "#a78bfa", "blue": "#60a5fa", "red": "#ff5f57",
        "yellow": "#ffbd2e", "grid0": "#161b22", "grid1": "#0e4429", "grid2": "#006d32",
        "grid3": "#26a641", "grid4": "#39d353",
    },
    "emerald_terminal": {
        "bg": "#07110d", "panel": "#0b1812", "panel2": "#07130e", "border": "#1e3a2b",
        "white": "#eafff2", "muted": "#80a18d", "cyan": "#52e0b0", "green": "#39d353",
        "orange": "#f3b562", "purple": "#8fbea7", "blue": "#73c9a9", "red": "#ff6b61",
        "yellow": "#e0c35a", "grid0": "#0d2117", "grid1": "#103d25", "grid2": "#126b3b",
        "grid3": "#25a64d", "grid4": "#52e07c",
    },
    "violet_future": {
        "bg": "#0d0b16", "panel": "#151126", "panel2": "#0e0b1a", "border": "#31264d",
        "white": "#f8f5ff", "muted": "#9f96b5", "cyan": "#6ee7f9", "green": "#6ee7b7",
        "orange": "#ffad66", "purple": "#b794f4", "blue": "#7aa2ff", "red": "#ff6b7a",
        "yellow": "#ffd166", "grid0": "#1a1524", "grid1": "#243b2d", "grid2": "#3d5b37",
        "grid3": "#5b7b42", "grid4": "#82d66a",
    },
    "titanium_minimal": {
        "bg": "#0d1117", "panel": "#15191f", "panel2": "#101318", "border": "#30363d",
        "white": "#f0f3f6", "muted": "#8b949e", "cyan": "#9bdcff", "green": "#8bd49a",
        "orange": "#f0b86b", "purple": "#c7b5ff", "blue": "#9bbcff", "red": "#ff8a80",
        "yellow": "#f3d477", "grid0": "#161b22", "grid1": "#263329", "grid2": "#3b5141",
        "grid3": "#57735d", "grid4": "#7fa888",
    },
}

README_PATH = ROOT / "README.md"
README_MARKER_START = "<!-- PROFILE-AUTO-GENERATED:START -->"
README_MARKER_END = "<!-- PROFILE-AUTO-GENERATED:END -->"
