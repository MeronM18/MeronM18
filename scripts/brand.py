"""Shared palette, fonts and helpers for every generated asset (see DESIGN.md)."""

from __future__ import annotations

import base64
import io
import random
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
SCRIPTS = ROOT / "scripts"
FONTS = SCRIPTS / "fonts"
ICONS = SCRIPTS / "icons"
SHOTS = SCRIPTS / "shots"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Midnight surfaces, cool text, one ultraviolet accent and one "volt" signal color.
INK = "#0A0A10"
PANEL = "#12121A"
RAISED = "#1A1A25"
LINE = "#272733"
TEXT = "#F3F1F8"
SOFT = "#C7C3D4"
MUTED = "#8E8A9E"
VIOLET = "#A994FF"
VIOLET_DIM = "#6B58D6"
VIOLET_DEEP = "#5A3FD9"  # violet that holds 4.5:1+ on white
VOLT = "#D4FF4F"
LIGHT_TEXT = "#1B1830"
LIGHT_MUTED = "#6A6680"
LIGHT_LINE = "#E2DEF0"

FAMILIES = {
    "display": "MM Display",     # Bricolage Grotesque 800, opsz 96
    "body": "MM Body",           # Bricolage Grotesque 400, opsz 14
    "bodybold": "MM Body Bold",  # Bricolage Grotesque 600, opsz 14
    "serif": "MM Serif",         # Instrument Serif Italic
    "mono": "MM Mono",           # JetBrains Mono 500
    "monobold": "MM Mono Bold",  # JetBrains Mono 700
}


def font_css(**texts: str) -> str:
    """@font-face rules that embed only the glyphs each string needs.

    Images on GitHub can't load web fonts, so every SVG carries its own subset:
    font_css(display="Meron Matti", mono="CS '27") -> CSS text.
    """
    from fontTools import subset
    from fontTools.ttLib import TTFont

    rules = []
    for key, text in texts.items():
        font = TTFont(FONTS / f"{key}.ttf")
        opts = subset.Options()
        opts.flavor = "woff"
        opts.layout_features = ["kern", "liga", "calt"]
        sub = subset.Subsetter(opts)
        sub.populate(text=text + " ")
        sub.subset(font)
        buf = io.BytesIO()
        font.save(buf)
        data = base64.b64encode(buf.getvalue()).decode()
        rules.append(f"@font-face{{font-family:'{FAMILIES[key]}';src:url(data:font/woff;base64,{data}) format('woff')}}")
    return "".join(rules)


_metrics: dict[str, tuple] = {}


def measure(text: str, key: str, size: float, tracking: float = 0) -> float:
    """Advance width of `text` in px, set in font `key` at `size` with `tracking` px letter-spacing."""
    from fontTools.ttLib import TTFont

    if key not in _metrics:
        f = TTFont(FONTS / f"{key}.ttf")
        _metrics[key] = (f.getBestCmap(), f["hmtx"], f["head"].unitsPerEm)
    cmap, hmtx, upm = _metrics[key]
    units = sum(hmtx[cmap.get(ord(c), cmap[ord("?")])][0] for c in text)
    return units * size / upm + tracking * len(text)


def font_files_css() -> str:
    """@font-face rules pointing at the local font files, for HTML rendered in Chrome."""
    return "".join(
        f"@font-face{{font-family:'{fam}';src:url('{(FONTS / f'{key}.ttf').as_uri()}')}}"
        for key, fam in FAMILIES.items()
    )


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def icon_path(name: str) -> str:
    """The <path d> of a Simple Icons SVG (CC0), drawn on a 24x24 grid."""
    svg = (ICONS / f"{name}.svg").read_text()
    return svg.split(' d="', 1)[1].split('"', 1)[0]


def stars(n: int, width: float, height: float, seed: int, avoid: tuple[float, float, float, float] | None = None):
    """Deterministic starfield: (x, y, radius, opacity) tuples."""
    rng = random.Random(seed)
    out = []
    while len(out) < n:
        x, y = rng.uniform(0, width), rng.uniform(0, height)
        if avoid and avoid[0] < x < avoid[2] and avoid[1] < y < avoid[3]:
            continue
        r = rng.choice([0.6, 0.8, 0.8, 1.0, 1.2, 1.6])
        out.append((x, y, r, rng.uniform(0.25, 0.8)))
    return out


def render(html: str, out: Path, width: int, height: int, scale: int = 2, quality: int = 88) -> None:
    """Screenshot `html` in headless Chrome at width x height CSS px and save as WebP.

    The page background is transparent, so rounded card corners blend into either
    GitHub theme.
    """
    from PIL import Image

    with tempfile.TemporaryDirectory() as tmp:
        page = Path(tmp) / "page.html"
        png = Path(tmp) / "shot.png"
        page.write_text(html)
        subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
             f"--force-device-scale-factor={scale}", f"--window-size={width},{height}",
             "--default-background-color=00000000", "--virtual-time-budget=2000",
             f"--screenshot={png}", page.as_uri()],
            check=True, capture_output=True,
        )
        img = Image.open(png).convert("RGBA").crop((0, 0, width * scale, height * scale))
        out.parent.mkdir(parents=True, exist_ok=True)
        img.save(out, "WEBP", quality=quality, method=6)
    print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


def write(out: Path, content: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content)
    print(f"wrote {out.relative_to(ROOT)} ({len(content) // 1024} KB)")
