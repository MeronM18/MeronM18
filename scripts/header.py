"""Animated header: name, tagline and a constellation of projects (desktop + phone)."""

from __future__ import annotations

from brand import (ASSETS, INK, LINE, MUTED, SOFT, TEXT, VIOLET, VOLT, esc, font_css, measure, stars,
                   write)

NAME = "Meron Matti"
ROLE = "FULL-STACK · INDIE DEVELOPER"
TAG_A = "I build things for fun, "
TAG_B = "then I ship them."
META = "OAKLAND UNIVERSITY · B.S. COMPUTER SCIENCE · MAY 2027 · MICHIGAN"
NOW = "NOW BUILDING"
NOW_ITEMS = "EasyMail · StayDue"

# Constellation nodes: (label, x, y, bright, label anchor, label dx, label dy), in a 340x300 box.
NODES = [
    ("Imperium", 170, 40, True, "start", 16, 5),
    ("Ledger.m", 40, 118, False, "start", -4, -16),
    ("Cosmo", 300, 104, True, "end", -16, -12),
    ("Dummy Peptides", 104, 212, True, "start", -40, 30),
    ("StayDue", 256, 222, False, "start", 16, 5),
    ("EasyMail", 196, 292, False, "start", 16, 5),
]
EDGES = [(0, 1), (0, 2), (1, 3), (2, 4), (3, 4), (4, 5), (3, 5), (0, 3)]

# Twinkles and a slow orbit. Every element is fully drawn without CSS; motion only
# dims and brightens it, so a frozen frame is complete.
MOTION = (
    "@keyframes tw{0%,100%{opacity:1}50%{opacity:.3}}"
    ".tw{animation:tw 3.6s ease-in-out infinite}"
    "@keyframes spin{to{transform:rotate(360deg)}}"
    ".orbit{animation:spin 80s linear infinite}"
    "@keyframes pulse{0%,100%{opacity:.9}50%{opacity:.35}}"
    ".pulse{animation:pulse 2.4s ease-in-out infinite}"
    "@media (prefers-reduced-motion:reduce){.tw,.orbit,.pulse{animation:none}}"
)


def fonts() -> str:
    return font_css(
        display=NAME + "Meron Matti.",
        serif=TAG_A + TAG_B,
        monobold=ROLE + NOW,
        mono=META + NOW_ITEMS + "".join(n[0] for n in NODES).upper(),
    )


def background(w: int, h: int, seed: int) -> str:
    field = ""
    for i, (x, y, r, o) in enumerate(stars(90, w, h, seed)):
        twinkle = f' class="tw" style="animation-delay:{(i % 7) * 0.5:.1f}s"' if i % 5 == 0 else ""
        field += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" opacity="{o * 0.6:.2f}"{twinkle}/>'
    return f"""
<defs>
  <radialGradient id="g1" cx="0.86" cy="0.12" r="0.75">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.26"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </radialGradient>
  <radialGradient id="g2" cx="0.02" cy="1.05" r="0.6">
    <stop offset="0" stop-color="#6B58D6" stop-opacity="0.18"/><stop offset="1" stop-color="#6B58D6" stop-opacity="0"/>
  </radialGradient>
  <pattern id="rules" width="{w}" height="44" patternUnits="userSpaceOnUse">
    <line x1="0" y1="43.5" x2="{w}" y2="43.5" stroke="#fff" stroke-opacity="0.022"/>
  </pattern>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="28"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="{INK}"/>
  <rect width="{w}" height="{h}" fill="url(#g1)"/>
  <rect width="{w}" height="{h}" fill="url(#g2)"/>
  <rect width="{w}" height="{h}" fill="url(#rules)"/>
  {field}
</g>
<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="27.25" fill="none" stroke="{LINE}" stroke-width="1.5"/>"""


def constellation(ox: float, oy: float, s: float) -> str:
    cx, cy = ox + 170 * s, oy + 160 * s
    out = [
        f'<g class="orbit" style="transform-origin:{cx:.0f}px {cy:.0f}px">'
        f'<ellipse cx="{cx:.0f}" cy="{cy:.0f}" rx="{215 * s:.0f}" ry="{215 * s:.0f}" fill="none" '
        f'stroke="{VIOLET}" stroke-opacity="0.16" stroke-dasharray="2 7"/>'
        f'<circle cx="{cx + 215 * s:.0f}" cy="{cy:.0f}" r="{3.5 * s:.1f}" fill="{VIOLET}"/></g>'
    ]
    for a, b in EDGES:
        x1, y1, x2, y2 = *NODES[a][1:3], *NODES[b][1:3]
        out.append(f'<line x1="{ox + x1 * s:.1f}" y1="{oy + y1 * s:.1f}" x2="{ox + x2 * s:.1f}" y2="{oy + y2 * s:.1f}" '
                   f'stroke="{VIOLET}" stroke-opacity="0.35" stroke-width="1.2"/>')
    for i, (label, x, y, bright, anchor, ldx, ldy) in enumerate(NODES):
        px, py = ox + x * s, oy + y * s
        r = (5.5 if bright else 4) * s
        out.append(f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{r * 3:.1f}" fill="{VIOLET}" opacity="0.14"/>')
        out.append(f'<circle class="tw" style="animation-delay:{i * 0.6:.1f}s" cx="{px:.1f}" cy="{py:.1f}" '
                   f'r="{r:.1f}" fill="{"#fff" if bright else VIOLET}"/>')
        out.append(f'<text x="{px + ldx * s:.1f}" y="{py + ldy * s:.1f}" text-anchor="{anchor}" font-family="MM Mono" '
                   f'font-size="{12.5 * s:.1f}" letter-spacing="{1.6 * s:.1f}" fill="{MUTED}">{esc(label.upper())}</text>')
    return '<g clip-path="url(#frame)">' + "\n".join(out) + "</g>"


def now_chip(x: float, y: float, size: float) -> str:
    label_w = measure(NOW, "monobold", size, 2.2)
    items_w = measure(NOW_ITEMS.upper(), "mono", size, 2.2)
    w = 46 + label_w + 18 + items_w + 22
    h = size * 2.9
    return f"""
<rect x="{x}" y="{y}" width="{w:.0f}" height="{h:.0f}" rx="{h / 2:.0f}" fill="#fff" fill-opacity="0.03" stroke="{LINE}" stroke-width="1.5"/>
<circle cx="{x + 24}" cy="{y + h / 2:.1f}" r="{size * 0.85:.1f}" fill="{VOLT}" opacity="0.18" class="pulse"/>
<circle cx="{x + 24}" cy="{y + h / 2:.1f}" r="{size * 0.36:.1f}" fill="{VOLT}"/>
<text x="{x + 46}" y="{y + h / 2 + size * 0.36:.1f}" font-family="MM Mono Bold" font-size="{size}" letter-spacing="2.2" fill="{TEXT}">{NOW}</text>
<text x="{x + 46 + label_w + 18:.0f}" y="{y + h / 2 + size * 0.36:.1f}" font-family="MM Mono" font-size="{size}" letter-spacing="2.2" fill="{VIOLET}">{esc(NOW_ITEMS.upper())}</text>"""


def svg(w: int, h: int, body: str) -> str:
    desc = (f"{NAME}, full-stack and indie developer. {TAG_A}{TAG_B} Oakland University, B.S. Computer Science, "
            f"May 2027, Michigan. Now building EasyMail and StayDue.")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="t d"><title id="t">{NAME}</title><desc id="d">{esc(desc)}</desc>'
            f"<style>{fonts()}{MOTION}</style>{body}</svg>")


def desktop() -> str:
    w, h = 1200, 500
    body = background(w, h, seed=7) + f"""
<text x="64" y="104" font-family="MM Mono Bold" font-size="16" letter-spacing="4" fill="{VIOLET}">{ROLE}</text>
<text x="60" y="236" font-family="MM Display" font-size="124" letter-spacing="-4.5" fill="{TEXT}">{NAME}<tspan fill="{VIOLET}">.</tspan></text>
<text x="64" y="304" font-family="MM Serif" font-size="46" fill="{SOFT}">{TAG_A}<tspan fill="{VIOLET}">{TAG_B}</tspan></text>
<text x="64" y="370" font-family="MM Mono" font-size="14.5" letter-spacing="2.4" fill="{MUTED}">{META}</text>
{now_chip(64, 400, 14)}
{constellation(810, 90, 1.0)}"""
    return svg(w, h, body)


def phone() -> str:
    w, h = 600, 820
    body = background(w, h, seed=9) + f"""
{constellation(250, 40, 0.92)}
<text x="44" y="96" font-family="MM Mono Bold" font-size="17" letter-spacing="3.4" fill="{VIOLET}">FULL-STACK</text>
<text x="44" y="122" font-family="MM Mono Bold" font-size="17" letter-spacing="3.4" fill="{VIOLET}">INDIE DEVELOPER</text>
<text x="38" y="420" font-family="MM Display" font-size="118" letter-spacing="-4" fill="{TEXT}">Meron</text>
<text x="38" y="524" font-family="MM Display" font-size="118" letter-spacing="-4" fill="{TEXT}">Matti<tspan fill="{VIOLET}">.</tspan></text>
<text x="44" y="592" font-family="MM Serif" font-size="40" fill="{SOFT}">{TAG_A.strip()}</text>
<text x="44" y="638" font-family="MM Serif" font-size="40" fill="{VIOLET}">{TAG_B}</text>
<text x="44" y="694" font-family="MM Mono" font-size="16" letter-spacing="2" fill="{MUTED}">OAKLAND UNIVERSITY · CS · MAY 2027</text>
{now_chip(44, 722, 15)}"""
    return svg(w, h, body)


def main() -> None:
    write(ASSETS / "header.svg", desktop())
    write(ASSETS / "header-phone.svg", phone())


if __name__ == "__main__":
    main()
