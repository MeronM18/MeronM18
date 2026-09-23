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

# Graphite surfaces, bone text, one cold steel accent. Near-monochrome on purpose.
INK = "#0A0A0A"
PANEL = "#111111"
RAISED = "#171717"
LINE = "#262626"
TEXT = "#ECE9E2"
SOFT = "#B3AFA7"
MUTED = "#86827A"
ACCENT = "#A9B4C0"       # steel: taglines, eyebrows, the one thing to look at
ACCENT_DIM = "#5D6772"
ACCENT_DEEP = "#3F4955"  # steel that holds 4.5:1+ on white
SIGNAL = "#F4F0E6"       # status only: live or running now (always with a label)
LIGHT_TEXT = "#111111"
LIGHT_MUTED = "#5E5A54"
LIGHT_LINE = "#DAD6CF"

FAMILIES = {
    "script": "MM Script",       # Imperial Script (the hero name, drawn as paths)
    "display": "MM Display",     # Bodoni Moda 500, opsz 96
    "serif": "MM Serif",         # Bodoni Moda Italic 400, opsz 96
    "body": "MM Body",           # Switzer 400 (never embedded in an SVG; see outline())
    "bodybold": "MM Body Bold",  # Switzer 500
    "mono": "MM Mono",           # IBM Plex Mono 400
    "monobold": "MM Mono Bold",  # IBM Plex Mono 600
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


def shape(text: str, key: str, size: float, tracking: float = 0) -> tuple[list, float]:
    """HarfBuzz-shaped glyphs of `text`: ([(glyph name, x offset, y offset)], advance width), in px."""
    import uharfbuzz as hb
    from fontTools.ttLib import TTFont

    path = FONTS / f"{key}.ttf"
    face = hb.Face(path.read_bytes())
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {"kern": True, "liga": True, "calt": True})
    order = TTFont(path).getGlyphOrder()
    k = size / face.upem
    out, x = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        out.append((order[info.codepoint], x + pos.x_offset * k, pos.y_offset * k))
        x += pos.x_advance * k + tracking
    return out, x - tracking


def outline_d(text: str, key: str, size: float, x: float, y: float, tracking: float = 0,
              anchor: str = "start") -> tuple[str, float]:
    """SVG path data for shaped `text` with its baseline at (x, y), and its width."""
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont

    font = TTFont(FONTS / f"{key}.ttf")
    glyphs, upm = font.getGlyphSet(), font["head"].unitsPerEm
    run, width = shape(text, key, size, tracking)
    x0 = x - {"start": 0, "middle": width / 2, "end": width}[anchor]
    k = size / upm
    pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
    for name, gx, gy in run:
        glyphs[name].draw(TransformPen(pen, (k, 0, 0, -k, x0 + gx, y - gy)))
    return pen.getCommands(), width


def outline(text: str, key: str, size: float, x: float, y: float, fill: str, tracking: float = 0,
            anchor: str = "start", opacity: float = 1) -> str:
    """`text` as one SVG <path>, for fonts whose license forbids embedding them as fonts (Switzer)."""
    d, _ = outline_d(text, key, size, x, y, tracking, anchor)
    return f'<path fill="{fill}" opacity="{opacity}" d="{d}"/>'


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
