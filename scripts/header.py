"""Animated hero: a signature that writes itself, and a typing line that cycles through what I build."""

from __future__ import annotations

from brand import (ACCENT, ASSETS, INK, LINE, MUTED, SIGNAL, SOFT, TEXT, esc, font_css, measure, outline,
                   outline_d, shape, write)

NAME = "Meron Matti"
ROLE = "FULL-STACK · INDIE DEVELOPER"
COORDS = "42.67° N · 83.22° W"
PREFIX = "› I build "
PHRASES = [
    "things for fun, then I ship them.",
    "agents that run my Mac from my phone.",
    "finance apps wired to real bank accounts.",
    "storefronts that ship real orders.",
    "iOS apps with paid subscriptions.",
]
ABOUT = "Computer Science at Oakland University, class of 2027."
NOW = "NOW BUILDING"
NOW_ITEMS = "EASYMAIL · STAYDUE"  # replaced by the live list when built with --live (see now.py)

# Typing rhythm, in seconds.
TYPE, HOLD, DELETE, GAP = 0.055, 2.4, 0.022, 0.4

MOTION = (
    # Signature: each glyph's outline is drawn, then filled with ink, left to right.
    "@keyframes draw{from{stroke-dashoffset:1;fill-opacity:0}70%{fill-opacity:0}to{stroke-dashoffset:0;fill-opacity:1}}"
    ".sig{stroke-dasharray:1;animation:draw 1.5s cubic-bezier(.55,0,.35,1) both}"
    "@keyframes rule{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
    ".rule{transform-box:fill-box;transform-origin:left;animation:rule 1.4s cubic-bezier(.6,0,.2,1) 2.4s both}"
    "@keyframes blink{0%,49%{opacity:1}50%,100%{opacity:0}}.caret{animation:blink 1.05s step-end infinite}"
    "@keyframes pulse{0%,100%{opacity:.9}50%{opacity:.3}}.pulse{animation:pulse 2.4s ease-in-out infinite}"
    "@media (prefers-reduced-motion:reduce){.caret,.pulse,.sig,.rule{animation:none}}"
)


def fonts() -> str:
    return font_css(
        monobold=ROLE + NOW,
        mono=COORDS + PREFIX + "".join(PHRASES) + NOW_ITEMS,
    )


def backdrop(w: int, h: int) -> str:
    ticks = "".join(
        f'<path d="M{x} {y + dy * 16}V{y}H{x + dx * 16}" fill="none" stroke="#3A3A3A" stroke-width="1.5"/>'
        for x, y, dx, dy in ((24, 24, 1, 1), (w - 24, 24, -1, 1), (24, h - 24, 1, -1), (w - 24, h - 24, -1, -1))
    )
    return f"""
<defs>
  <radialGradient id="spot" cx="0.1" cy="-0.15" r="0.95">
    <stop offset="0" stop-color="#fff" stop-opacity="0.085"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="steel" cx="1.05" cy="1.1" r="0.7">
    <stop offset="0" stop-color="{ACCENT}" stop-opacity="0.08"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
  </radialGradient>
  <pattern id="rules" width="{w}" height="40" patternUnits="userSpaceOnUse">
    <line x1="0" y1="39.5" x2="{w}" y2="39.5" stroke="#fff" stroke-opacity="0.016"/>
  </pattern>
  <linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="-420" y1="0" x2="-120" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/>
    <stop offset="0.5" stop-color="#fff" stop-opacity="0.75"/>
    <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="0 0;{w + 600} 0;{w + 600} 0"
      keyTimes="0;0.4;1" dur="8s" begin="3.4s" repeatCount="indefinite"/>
  </linearGradient>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="28"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="{INK}"/>
  <rect width="{w}" height="{h}" fill="url(#spot)"/>
  <rect width="{w}" height="{h}" fill="url(#steel)"/>
  <rect width="{w}" height="{h}" fill="url(#rules)"/>
</g>
{ticks}
<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="27.25" fill="none" stroke="{LINE}" stroke-width="1.5"/>"""


def signature(text: str, x: float, y: float, size: float, start: float = 0.2, sheen: bool = True) -> str:
    """The name in Imperial Script, one path per glyph so they can be written in order.

    Without CSS every glyph is filled bone, so a frozen frame shows the whole name.
    A copy on top catches a light band that sweeps across after the name is written.
    """
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.transformPen import TransformPen
    from fontTools.ttLib import TTFont

    from brand import FONTS

    font = TTFont(FONTS / "script.ttf")
    glyphs, k = font.getGlyphSet(), size / font["head"].unitsPerEm
    run, _ = shape(text, "script", size)
    parts, delay = [], start
    for name, gx, gy in run:
        pen = SVGPathPen(glyphs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        glyphs[name].draw(TransformPen(pen, (k, 0, 0, -k, x + gx, y - gy)))
        d = pen.getCommands()
        if not d:  # the space
            delay += 0.12
            continue
        parts.append(f'<path class="sig" style="animation-delay:{delay:.2f}s" pathLength="1" d="{d}"/>')
        delay += 0.16
    glyphs_g = f'<g fill="{TEXT}" stroke="{TEXT}" stroke-width="1.1" stroke-linejoin="round">{"".join(parts)}</g>'
    if not sheen:
        return glyphs_g
    whole, _ = outline_d(text, "script", size, x, y)
    return glyphs_g + f'<path d="{whole}" fill="url(#sheen)" aria-hidden="true"/>'


def typing(x: float, y: float, size: float, uid: str) -> str:
    """Each phrase types in, holds, deletes; SMIL steps a clip rect one character at a time.

    Without SMIL the first phrase is fully shown with the caret at its end, so a
    frozen frame still reads as a finished sentence.
    """
    cw = measure("M", "mono", size)
    spans, t = [], 0.0
    for p in PHRASES:
        n = len(p)
        events = [(t + k * TYPE, k * cw) for k in range(1, n + 1)]
        t_del = t + n * TYPE + HOLD
        events += [(t_del + j * DELETE, (n - j) * cw) for j in range(1, n + 1)]
        spans.append(events)
        t = t_del + n * DELETE + GAP
    total = t

    def animate(attr: str, events: list[tuple[float, float]], base: float) -> str:
        pts = [(0.0, base)] + [(et / total, v) for et, v in events]
        return (f'<animate attributeName="{attr}" calcMode="discrete" dur="{total:.2f}s" repeatCount="indefinite" '
                f'keyTimes="{";".join(f"{k:.5f}" for k, _ in pts)}" values="{";".join(f"{v:.1f}" for _, v in pts)}"/>')

    out, defs = [], []
    for i, (p, events) in enumerate(zip(PHRASES, spans)):
        full = len(p) * cw if i == 0 else 0
        defs.append(f'<clipPath id="{uid}{i}"><rect x="{x}" y="{y - size * 1.05:.1f}" width="{full:.1f}" '
                    f'height="{size * 1.5:.1f}">{animate("width", events, 0)}</rect></clipPath>')
        out.append(f'<text x="{x}" y="{y}" font-family="MM Mono" font-size="{size}" fill="{TEXT}" '
                   f'clip-path="url(#{uid}{i})">{esc(p)}</text>')
    caret_events = sorted((et, x + v) for events in spans for et, v in events)
    caret_x = x + len(PHRASES[0]) * cw
    out.append(f'<rect class="caret" x="{caret_x + 3:.1f}" y="{y - size * 0.82:.1f}" width="{size * 0.5:.1f}" '
               f'height="{size * 1.02:.1f}" fill="{ACCENT}">{animate("x", [(et, v + 3) for et, v in caret_events], x + 3)}</rect>')
    return f"<defs>{''.join(defs)}</defs>" + "".join(out)


def now_chip(x: float, y: float, size: float, anchor_end: bool = False, max_w: float = 1e9) -> str:
    label_w = measure(NOW, "monobold", size, 2.4)
    items = NOW_ITEMS
    if 26 + label_w + 16 + measure(items, "mono", size, 2.4) > max_w:  # too long: keep the latest repo only
        items = items.split(" · ")[0]
    items_w = measure(items, "mono", size, 2.4)
    w = 26 + label_w + 16 + items_w
    x0 = x - w if anchor_end else x
    cy = y - size * 0.36
    return (f'<circle cx="{x0 + 6}" cy="{cy:.1f}" r="{size * 0.85:.1f}" fill="{SIGNAL}" opacity="0.16" class="pulse"/>'
            f'<circle cx="{x0 + 6}" cy="{cy:.1f}" r="{size * 0.3:.1f}" fill="{SIGNAL}"/>'
            f'<text x="{x0 + 26:.1f}" y="{y}" font-family="MM Mono Bold" font-size="{size}" letter-spacing="2.4" '
            f'fill="{TEXT}">{NOW}</text>'
            f'<text x="{x0 + 26 + label_w + 16:.1f}" y="{y}" font-family="MM Mono" font-size="{size}" '
            f'letter-spacing="2.4" fill="{ACCENT}">{esc(items)}</text>')


def svg(w: int, h: int, body: str) -> str:
    now = " and ".join(n.title() for n in NOW_ITEMS.split(" · "))
    desc = (f"Meron Matti, full-stack and indie developer. I build {PHRASES[0]} Also: "
            + "; ".join(p.rstrip(".") for p in PHRASES[1:]) + f". {ABOUT} Now building {now}.")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="t d"><title id="t">Meron Matti</title><desc id="d">{esc(desc)}</desc>'
            f"<style>{fonts()}{MOTION}</style>{backdrop(w, h)}{body}</svg>")


def desktop() -> str:
    w, h, pad = 1200, 520, 72
    size = 206
    mono = 25
    base = 268
    rule_y = base + 44
    type_y = rule_y + 68
    prefix_w = measure(PREFIX, "mono", mono)
    body = f"""
<text x="{pad}" y="88" font-family="MM Mono Bold" font-size="14" letter-spacing="4" fill="{ACCENT}">{ROLE}</text>
<text x="{w - pad}" y="88" text-anchor="end" font-family="MM Mono" font-size="14" letter-spacing="2.4" fill="{MUTED}">{esc(COORDS)}</text>
{signature(NAME, pad - 6, base, size)}
<line class="rule" x1="{pad}" y1="{rule_y}.5" x2="{w - pad}" y2="{rule_y}.5" stroke="{LINE}" stroke-width="1.5"/>
<text x="{pad}" y="{type_y}" font-family="MM Mono" font-size="{mono}" fill="{MUTED}"><tspan fill="{ACCENT}">›</tspan>{esc(PREFIX[1:])}</text>
{typing(pad + prefix_w, type_y, mono, "tw")}
{outline(ABOUT, "body", 18, pad, h - 64, SOFT)}
{now_chip(w - pad, h - 64, 13.5, anchor_end=True, max_w=560)}"""
    return svg(w, h, body)


def phone() -> str:
    w, h, pad = 600, 820, 44
    size = 206
    mono = 19
    b1, b2 = 290, 440
    rule_y = b2 + 44
    body = f"""
<text x="{pad}" y="80" font-family="MM Mono Bold" font-size="16" letter-spacing="3.4" fill="{ACCENT}">FULL-STACK</text>
<text x="{pad}" y="106" font-family="MM Mono Bold" font-size="16" letter-spacing="3.4" fill="{ACCENT}">INDIE DEVELOPER</text>
<text x="{w - pad}" y="80" text-anchor="end" font-family="MM Mono" font-size="15" letter-spacing="1.6" fill="{MUTED}">42.67° N</text>
<text x="{w - pad}" y="106" text-anchor="end" font-family="MM Mono" font-size="15" letter-spacing="1.6" fill="{MUTED}">83.22° W</text>
{signature("Meron", pad - 4, b1, size)}
{signature("Matti", pad + 60, b2, size, start=1.1)}
<line class="rule" x1="{pad}" y1="{rule_y}.5" x2="{w - pad}" y2="{rule_y}.5" stroke="{LINE}" stroke-width="1.5"/>
<text x="{pad}" y="{rule_y + 58}" font-family="MM Mono" font-size="{mono + 2}" fill="{MUTED}"><tspan fill="{ACCENT}">›</tspan>{esc(PREFIX[1:])}</text>
{typing(pad, rule_y + 96, mono, "tp")}
{outline("Computer Science at Oakland University,", "body", 21, pad, h - 138, SOFT)}
{outline("class of 2027.", "body", 21, pad, h - 108, SOFT)}
{now_chip(pad, h - 58, 15, max_w=w - 2 * pad)}"""
    return svg(w, h, body)


def main(argv: list[str] | None = None) -> None:
    """--live pulls the "now building" repos from GitHub; --out DIR writes somewhere other than assets/."""
    from pathlib import Path

    global NOW_ITEMS
    argv = argv or []
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else ASSETS
    if "--live" in argv:
        from now import now_building
        NOW_ITEMS = " · ".join(now_building())
        print(f"now building: {NOW_ITEMS}")
    write(out / "header.svg", desktop())
    write(out / "header-phone.svg", phone())


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
