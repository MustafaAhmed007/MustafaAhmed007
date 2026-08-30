from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont, ImageOps

from config import ASSET_DIR, CACHE_DIR, CONTRIBUTIONS, DESIGN, OUTPUT_DIR, PREVIEW_DIR, PROFILE, README_MARKER_END, README_MARKER_START, README_PATH, THEMES

SVG_NS = "http://www.w3.org/2000/svg"


def esc(value: object) -> str:
    return ("" if value is None else str(value)).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")


def deterministic_id(prefix: str) -> str:
    digest = hashlib.sha256(f"{PROFILE['github_username']}:{PROFILE['theme']}:{prefix}".encode()).hexdigest()[:12]
    return f"{prefix}_{digest}"


def ensure_dirs() -> None:
    for d in (OUTPUT_DIR, ASSET_DIR, CACHE_DIR, PREVIEW_DIR):
        d.mkdir(parents=True, exist_ok=True)


def theme() -> dict:
    name = PROFILE.get("theme", "cyber_cyan")
    if name not in THEMES:
        raise ValueError(f"Unknown theme: {name}")
    return THEMES[name]


def warn(msg: str) -> None:
    print(f"WARNING: {msg}")


def make_fallback_avatar(path: Path, size: int = 512) -> None:
    im = Image.new("RGB", (size, size), "#0d1117")
    px = im.load()
    seed = int(hashlib.sha256(PROFILE["github_username"].encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    for y in range(size):
        for x in range(size):
            dx, dy = x - size / 2, y - size / 2
            r = math.sqrt(dx * dx + dy * dy) / (size / 2)
            if r < 0.92:
                v = int(max(0, 120 - r * 80 + rng.random() * 10))
                px[x, y] = (v // 3, min(220, v), min(255, v + 25))
    draw = ImageDraw.Draw(im)
    letter = (PROFILE["display_name"] or "P").strip()[:1].upper()
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 190)
    except OSError:
        font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), letter, font=font)
    draw.text(((size - (bbox[2] - bbox[0])) / 2, (size - (bbox[3] - bbox[1])) / 2 - 20), letter, fill="#f4f7fb", font=font)
    im.save(path)


def fetch_avatar(username: str) -> Path:
    ensure_dirs()

    local_avatar = ASSET_DIR / "avatar.png"

    if local_avatar.exists() and local_avatar.stat().st_size > 0:
        return local_avatar

    warn("assets/avatar.png not found; using deterministic fallback")

    fallback = CACHE_DIR / "avatar_fallback.png"

    if not fallback.exists():
        make_fallback_avatar(fallback)

    return fallback


def avatar_to_ascii(path: Path) -> list[str]:
    density = max(24, min(150, int(DESIGN.get("ascii_density", 92))))
    ramp = DESIGN.get("ascii_ramp", "@#S%?*+;:,. ")
    # Leading/trailing whitespace in a character ramp is meaningful, so preserve it.
    ramp = ramp if ramp else "@#S%?*+;:,."
    im = Image.open(path).convert("L")
    width, height = density, max(16, int(density * 0.52))
    im = ImageOps.fit(im, (width, height), method=Image.Resampling.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.35)
    im = ImageEnhance.Brightness(im).enhance(1.03)
    rows = []
    for y in range(im.height):
        row = []
        for x in range(im.width):
            v = im.getpixel((x, y))
            idx = int((255 - v) / 255 * (len(ramp) - 1))
            row.append(ramp[max(0, min(len(ramp) - 1, idx))])
        rows.append("".join(row))
    return rows


def contribution_matrix() -> list[list[int]]:
    matrix = CONTRIBUTIONS.get("matrix")
    if isinstance(matrix, list) and len(matrix) == 53 and all(isinstance(c, list) and len(c) == 7 for c in matrix):
        return [[max(0, min(4, int(v))) for v in col] for col in matrix]
    rng = random.Random(int(CONTRIBUTIONS.get("seed", 20260831)))
    out = []
    for week in range(53):
        col = []
        for day in range(7):
            wave = math.sin((week / 53) * math.pi * 4 + day * 0.8)
            p = rng.random()
            level = 0 if p < .34 else 1 if p < .58 else 2 if p < .80 else 3 if p < .94 else 4
            if wave > .65 and rng.random() < .45:
                level = min(4, level + 1)
            col.append(level)
        out.append(col)
    return out


def svg_header(width: int, height: int, title: str, desc: str) -> str:
    return f'<svg xmlns="{SVG_NS}" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="title desc"><title id="title">{esc(title)}</title><desc id="desc">{esc(desc)}</desc>'


def defs(t: dict, prefix: str) -> str:
    gid = deterministic_id(prefix)
    blur = 7 if DESIGN.get("glow", True) else 0
    filter_body = f'<filter id="{gid}_glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{blur}" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>' if blur else ""
    return f'''<defs>
<linearGradient id="{gid}_bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{t["panel"]}"/><stop offset="1" stop-color="{t["panel2"]}"/></linearGradient>
<linearGradient id="{gid}_edge" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{t["cyan"]}" stop-opacity=".55"/><stop offset=".5" stop-color="{t["purple"]}" stop-opacity=".28"/><stop offset="1" stop-color="{t["green"]}" stop-opacity=".45"/></linearGradient>
<pattern id="{gid}_scan" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="1" fill="{t["white"]}" opacity=".035"/></pattern>
{filter_body}</defs>'''


def card_base(w: int, h: int, t: dict, title: str, prefix: str) -> str:
    gid = deterministic_id(prefix)
    return f'''<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{DESIGN["card_radius"]}" fill="url(#{gid}_bg)" stroke="{t["border"]}" stroke-width="1.5"/>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{DESIGN["card_radius"]}" fill="none" stroke="url(#{gid}_edge)" stroke-opacity=".35"/>
<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{DESIGN["card_radius"]}" fill="url(#{gid}_scan)" opacity=".25"/>
<text x="26" y="30" fill="{t["muted"]}" font-family="{esc(DESIGN["font_mono"])}" font-size="11" letter-spacing="2.4">{esc(title.upper())}</text>'''


def terminal_svg() -> str:
    t = theme()
    w = int(DESIGN["terminal_width"])
    h = int(DESIGN["terminal_height"])

    rows = avatar_to_ascii(fetch_avatar(PROFILE["github_username"]))

    out = [
        svg_header(
            w,
            h,
            f"{PROFILE['display_name']} terminal portrait",
            "ASCII portrait rendered as a terminal-style identity command center.",
        ),
        defs(t, "terminal"),
        card_base(w, h, t, "terminal / identity", "terminal"),
    ]

    # Window chrome
    out.append(f"""
      <circle cx="28" cy="49" r="5" fill="{t["red"]}"/>
      <circle cx="45" cy="49" r="5" fill="{t["yellow"]}"/>
      <circle cx="62" cy="49" r="5" fill="{t["green"]}"/>

      <text x="{w/2}" y="52"
            text-anchor="middle"
            fill="{t["muted"]}"
            font-family="{esc(DESIGN["font_mono"])}"
            font-size="10">
        command-center://identity
      </text>

      <line x1="24" y1="66" x2="{w-24}" y2="66"
            stroke="{t["border"]}" opacity=".8"/>
    """)

    # ------------------------------------------------------------
    # LEFT: ASCII PORTRAIT
    # ------------------------------------------------------------
    portrait_x = 28
    portrait_y = 82
    portrait_w = 292
    portrait_h = 238

    source_cols = max(1, len(rows[0]))
    source_rows = max(1, len(rows))

    # Fit the ASCII image into the dedicated portrait region.
    # SVG monospace glyphs are approximately 0.6× font-size wide.
    font_size = min(
        8.2,
        portrait_h / max(1, source_rows) * 1.35,
    )

    char_width = font_size * 0.60

    scale_x = min(
        1.0,
        portrait_w / max(1, source_cols * char_width),
    )

    scale_y = min(
        1.0,
        portrait_h / max(1, source_rows * font_size * 1.05),
    )

    out.append(
        f'<g transform="translate({portrait_x},{portrait_y}) '
        f'scale({scale_x:.4f},{scale_y:.4f})">'
    )

    for i, row in enumerate(rows):
        delay = i * 0.022

        out.append(
            f'<text x="0" y="{(i + 1) * font_size:.2f}" '
            f'fill="{t["cyan"]}" '
            f'font-family="{esc(DESIGN["font_mono"])}" '
            f'font-size="{font_size:.2f}" '
            f'xml:space="preserve" opacity=".92">'
            f'{esc(row)}'
            f'<animate attributeName="opacity" '
            f'from="0" to=".92" dur=".22s" '
            f'begin="{delay:.3f}s" fill="freeze"/>'
            f'</text>'
        )

        # Lightweight cursor sweep
        cursor_width = max(2.5, char_width * 1.25)

        out.append(
            f'<rect x="0" '
            f'y="{i * font_size + 1:.2f}" '
            f'width="{cursor_width:.2f}" '
            f'height="{font_size:.2f}" '
            f'fill="{t["white"]}" opacity="0">'
            f'<animate attributeName="x" '
            f'from="0" '
            f'to="{max(1, len(row)) * char_width:.2f}" '
            f'dur=".18s" '
            f'begin="{delay:.3f}s" '
            f'fill="freeze"/>'
            f'<animate attributeName="opacity" '
            f'values="0;.8;0" '
            f'dur=".18s" '
            f'begin="{delay:.3f}s" '
            f'fill="freeze"/>'
            f'</rect>'
        )

    out.append("</g>")

    # Portrait divider
    out.append(
        f'<line x1="342" y1="84" x2="342" y2="318" '
        f'stroke="{t["border"]}" opacity=".7"/>'
    )

    # ------------------------------------------------------------
    # RIGHT: COMMAND CENTER INFORMATION
    # ------------------------------------------------------------
    info_x = 366

    display_name = PROFILE.get("display_name", "")
    bio = PROFILE.get("bio", "")
    status = PROFILE.get("status", "ONLINE")

    out.append(
        f'''
        <text x="{info_x}" y="101"
              fill="{t["white"]}"
              font-family="{esc(DESIGN["font_sans"])}"
              font-size="22"
              font-weight="700">
          {esc(display_name)}
        </text>

        <text x="{info_x}" y="123"
              fill="{t["cyan"]}"
              font-family="{esc(DESIGN["font_mono"])}"
              font-size="9.5"
              letter-spacing="1.5">
          AI SYSTEMS / AUTOMATION
        </text>

        <line x1="{info_x}" y1="137" x2="{w-28}" y2="137"
              stroke="{t["border"]}" opacity=".65"/>
        '''
    )

    # Status
    out.append(
        f'''
        <circle cx="{info_x + 5}" cy="158" r="4"
                fill="{t["green"]}">
          <animate attributeName="opacity"
                   values=".45;1;.45"
                   dur="2.2s"
                   repeatCount="indefinite"/>
        </circle>

        <text x="{info_x + 17}" y="162"
              fill="{t["green"]}"
              font-family="{esc(DESIGN["font_mono"])}"
              font-size="9"
              letter-spacing="1.2">
          {esc(status)}
        </text>
        '''
    )

    # Bio
    bio_line_1 = bio[:43]
    bio_line_2 = bio[43:86]

    out.append(
        f'''
        <text x="{info_x}" y="190"
              fill="{t["muted"]}"
              font-family="{esc(DESIGN["font_sans"])}"
              font-size="10.5">
          {esc(bio_line_1)}
        </text>

        <text x="{info_x}" y="207"
              fill="{t["muted"]}"
              font-family="{esc(DESIGN["font_sans"])}"
              font-size="10.5">
          {esc(bio_line_2)}
        </text>
        '''
    )

    # Capability rows
    capabilities = [
        ("SYSTEM", "AI + Automation"),
        ("BUILD", "Products + Developer Tools"),
        ("MODE", "Execution-first"),
    ]

    y = 220

    for label, value in capabilities:
        out.append(
            f'''
            <text x="{info_x}" y="{y}"
                  fill="{t["orange"]}"
                  font-family="{esc(DESIGN["font_mono"])}"
                  font-size="8.5"
                  letter-spacing="1.2">
              {esc(label)}
            </text>

            <text x="{info_x + 70}" y="{y}"
                  fill="{t["white"]}"
                  font-family="{esc(DESIGN["font_sans"])}"
                  font-size="10.5">
              {esc(value)}
            </text>
            '''
        )
        y += 25

    # Terminal prompt
    out.append(
        f'''
        <text x="{info_x}" y="306"
              fill="{t["green"]}"
              font-family="{esc(DESIGN["font_mono"])}"
              font-size="10">
          $ whoami
        </text>

        <text x="{info_x + 67}" y="306"
              fill="{t["white"]}"
              font-family="{esc(DESIGN["font_mono"])}"
              font-size="10">
          {esc(display_name)}
        </text>

        <rect x="{info_x + 67 + len(display_name) * 6.1:.1f}"
              y="297"
              width="6"
              height="12"
              fill="{t["white"]}"
              opacity=".8">
          <animate attributeName="opacity"
                   values=".8;0;.8"
                   dur="1.05s"
                   repeatCount="indefinite"/>
        </rect>
        '''
    )

    # Footer
    out.append(
        f'''
        <text x="28" y="{h-18}"
              fill="{t["muted"]}"
              font-family="{esc(DESIGN["font_mono"])}"
              font-size="8.5">
          identity module / local asset / deterministic
        </text>
        '''
    )

    out.append("</svg>")

    return "".join(out)


def info_svg() -> str:
    t = theme(); w, h = int(DESIGN["info_width"]), int(DESIGN["info_height"])
    out = [svg_header(w, h, f"{PROFILE['display_name']} information card", "Structured developer identity, expertise and project information."), defs(t, "info"), card_base(w, h, t, "system / profile", "info")]
    sections = []
    if PROFILE.get("bio"): sections.append(("ABOUT", PROFILE["bio"], t["white"]))
    if PROFILE.get("skills"): sections.append(("STACK", " · ".join(PROFILE["skills"]), t["cyan"]))
    if PROFILE.get("technologies"): sections.append(("BUILD", " · ".join(PROFILE["technologies"]), t["blue"]))
    if PROFILE.get("achievements"): sections.append(("HIGHLIGHTS", " · ".join(PROFILE["achievements"]), t["orange"]))
    if PROFILE.get("current_projects"): sections.append(("CURRENTLY", " · ".join(PROFILE["current_projects"]), t["green"]))
    contact = PROFILE.get("website") or PROFILE.get("contact")
    if contact: sections.append(("CONTACT", contact, t["purple"]))
    y = 65
    for i, (label, value, value_color) in enumerate(sections[:6]):
        delay = i * 0.06
        status = f'<circle cx="{w-36}" cy="{y-4}" r="4" fill="{t["green"]}"><animate attributeName="opacity" values=".45;1;.45" dur="2s" repeatCount="indefinite"/></circle>' if label == "CURRENTLY" else ''
        out.append(f'<g opacity="1"><text x="28" y="{y}" fill="{t["orange"]}" font-family="{esc(DESIGN["font_mono"])}" font-size="9.5" letter-spacing="1.7">{esc(label)}</text>{status}<text x="28" y="{y+17}" fill="{value_color}" font-family="{esc(DESIGN["font_sans"])}" font-size="12.5">{esc(value[:86])}</text><line x1="28" y1="{y+28}" x2="{w-28}" y2="{y+28}" stroke="{t["border"]}" opacity=".48"/><animateTransform attributeName="transform" type="translate" from="0 8" to="0 0" dur=".35s" begin="{delay:.2f}s" fill="freeze"/><animate attributeName="opacity" from="0" to="1" dur=".35s" begin="{delay:.2f}s" fill="freeze"/></g>')
        y += 43
        if y > h - 20: break
    out.append('</svg>'); return ''.join(out)


def contribution_svg() -> str:
    t = theme(); w, h = int(DESIGN["graph_width"]), int(DESIGN["graph_height"]); size, gap = int(DESIGN["cell_size"]), int(DESIGN["cell_gap"])
    matrix = contribution_matrix(); gid = deterministic_id("contrib"); levels = [t["grid0"], t["grid1"], t["grid2"], t["grid3"], t["grid4"]]
    total_w = 53 * size + 52 * gap; start_x = max(28, (w - total_w) / 2); start_y = 58
    out = [svg_header(w, h, "Contribution activity", "Deterministic GitHub-style 53 by 7 contribution activity field."), defs(t, "contrib"), card_base(w, h, t, "activity / contribution field", "contrib")]
    for x in range(53):
        for y in range(7):
            level = matrix[x][y]; cx = start_x + x * (size + gap); cy = start_y + y * (size + gap); delay = (x + (6-y)) * .018
            glow = f' filter="url(#{gid}_glow)"' if level >= 3 and DESIGN.get("glow", True) else ''
            out.append(f'<rect x="{cx:.2f}" y="{cy:.2f}" width="{size}" height="{size}" rx="3" fill="{levels[level]}"{glow}><animate attributeName="opacity" from="0" to="1" dur=".26s" begin="{delay:.3f}s" fill="freeze"/><animate attributeName="fill" values="{levels[level]};{t["white"]};{levels[level]}" dur=".18s" begin="{delay+.08:.3f}s" fill="freeze"/></rect>')
    lx, ly = w - 220, h - 23
    out.append(f'<text x="{lx-55}" y="{ly+4}" fill="{t["muted"]}" font-family="{esc(DESIGN["font_mono"])}" font-size="8">LESS</text>')
    for i, color in enumerate(levels): out.append(f'<rect x="{lx+i*20}" y="{ly-6}" width="12" height="12" rx="3" fill="{color}"/>')
    out.append(f'<text x="{lx+105}" y="{ly+4}" fill="{t["muted"]}" font-family="{esc(DESIGN["font_mono"])}" font-size="8">MORE</text></svg>')
    return ''.join(out)


def validate_svg(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8")
        ET.fromstring(text)
    except Exception as exc:
        return [f"XML parse failure: {exc}"]
    ids = re.findall(r'\bid="([^"]+)"', text)
    dupes = sorted({x for x in ids if ids.count(x) > 1})
    issues = []
    if dupes: issues.append("duplicate IDs: " + ", ".join(dupes[:10]))
    if not re.search(r'<svg[^>]*viewBox="[^"]+"[^>]*width="[^"]+"[^>]*height="[^"]+"', text): issues.append("missing SVG dimensions/viewBox")
    if len(text.encode()) > 700_000: issues.append(f"large SVG: {len(text.encode())/1024:.0f} KiB")
    if "<script" in text.lower() or "javascript:" in text.lower(): issues.append("script/javascript detected")
    return issues


def update_readme() -> None:
    generated = f'''{README_MARKER_START}

<table>
<tr>
<td width="54%" valign="top"><img src="output/terminal-card.svg" alt="Terminal-style ASCII portrait and identity card" width="100%"></td>
<td width="46%" valign="top"><img src="output/info-card.svg" alt="Developer command center profile information" width="100%"></td>
</tr>
</table>

<p align="center"><img src="output/github-contribution-animation.svg" alt="Generated GitHub-style contribution activity field" width="96%"></p>

{README_MARKER_END}'''
    current = README_PATH.read_text(encoding="utf-8") if README_PATH.exists() else f"# {esc(PROFILE['display_name'])}\n"
    pattern = re.compile(re.escape(README_MARKER_START) + r".*?" + re.escape(README_MARKER_END), re.S)
    updated = pattern.sub(generated, current, count=1) if pattern.search(current) else current.rstrip() + "\n\n" + generated + "\n"
    README_PATH.write_text(updated, encoding="utf-8")


def build(lite: bool = False) -> dict:
    ensure_dirs()
    if lite:
        DESIGN["ascii_density"] = min(int(DESIGN["ascii_density"]), 64); DESIGN["glow"] = False; DESIGN["animation_speed"] = max(1.5, float(DESIGN["animation_speed"]))
    outputs = {"terminal-card.svg": terminal_svg(), "info-card.svg": info_svg(), "github-contribution-animation.svg": contribution_svg()}
    for name, content in outputs.items(): (OUTPUT_DIR / name).write_text(content, encoding="utf-8")
    update_readme()
    matrix = contribution_matrix(); (Path(__file__).parent / "data" / "contributions.json").write_text(json.dumps({"weeks": matrix}, indent=2) + "\n", encoding="utf-8")
    results = {name: validate_svg(OUTPUT_DIR / name) for name in outputs}
    readme_text = README_PATH.read_text(encoding="utf-8")
    report = {"status": "PASS" if not any(results.values()) and readme_text.count(README_MARKER_START) == 1 and readme_text.count(README_MARKER_END) == 1 else "WARNING", "theme": PROFILE["theme"], "username": PROFILE["github_username"], "files": {k: {"status": "PASS" if not v else "WARNING", "issues": v} for k, v in results.items()}, "readme_markers": readme_text.count(README_MARKER_START) == 1 and readme_text.count(README_MARKER_END) == 1, "notes": ["GitHub can render SVG images but its documented SVG renderer does not support inline SVG animation.", "SMIL is included as progressive enhancement; static visual state is complete."]}
    (PREVIEW_DIR / "qa-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2)); return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the Personal Developer Command Center.")
    parser.add_argument("--lite", action="store_true")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args(); ensure_dirs()
    if args.validate:
        report = {n: validate_svg(OUTPUT_DIR / n) if (OUTPUT_DIR / n).exists() else ["missing file"] for n in ("terminal-card.svg", "info-card.svg", "github-contribution-animation.svg")}
        print(json.dumps(report, indent=2)); return 0 if not any(report.values()) else 1
    build(lite=args.lite); return 0


if __name__ == "__main__": raise SystemExit(main())
