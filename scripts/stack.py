"""Toolkit grid: rows of icon tiles, one row per category (desktop + phone).

Motion: tiles rise in row by row on load, then a diagonal wave of steel light
passes through the grid every few seconds, lifting each logo as it goes. Without
CSS every tile is drawn and unlit.
"""

from __future__ import annotations

from brand import (ASSETS, INK, LINE, MUTED, PANEL, SOFT, TEXT, ACCENT, esc, font_css, icon_path, measure,
                   write)

# (label, Simple Icons slug or None for a lettermark)
STACK = [
    ("Languages", [("TypeScript", "typescript"), ("JavaScript", "javascript"), ("Python", "python"),
                   ("Java", "openjdk")]),
    ("Frameworks", [("React", "react"), ("Next.js", "nextdotjs"), ("Expo", "expo"), ("FastAPI", "fastapi"),
                    ("Node.js", "nodedotjs"), ("Tailwind", "tailwindcss")]),
    ("Data & infra", [("Supabase", "supabase"), ("Postgres", "postgresql"), ("Vercel", "vercel"),
                      ("Docker", "docker")]),
    ("AI & APIs", [("Anthropic", "anthropic"), ("OpenAI", "openai"), ("Plaid", None), ("Twilio", "twilio"),
                   ("Resend", "resend"), ("RevenueCat", "revenuecat")]),
    ("Test & ship", [("Vitest", "vitest"), ("Playwright", "playwright"), ("Git", "git"),
                     ("Google Maps", "googlemaps")]),
]
DESC = "; ".join(f"{cat}: {', '.join(n for n, _ in items)}" for cat, items in STACK) + "."


WAVE = 6.0  # seconds per pass of the light wave

MOTION = (
    "@keyframes rise{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:none}}"
    ".tile{animation:rise .8s cubic-bezier(.2,.7,.2,1) both}"
    "@keyframes lit{0%,16%,100%{opacity:0}5%{opacity:1}}"
    ".lit{opacity:0;animation:lit 6s ease-in-out infinite}"
    "@keyframes lift{0%,16%,100%{transform:none}5%{transform:translateY(-4px)}}"
    ".ic{animation:lift 6s ease-in-out infinite}"
    "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
    ".bar{transform-box:fill-box;transform-origin:left;animation:grow 1s cubic-bezier(.6,0,.2,1) both}"
    "@media (prefers-reduced-motion:reduce){.tile,.lit,.ic,.bar{animation:none}.lit{opacity:0}}"
)


def tile(x: float, y: float, w: float, h: float, name: str, slug: str | None, icon: float, label: float,
         row: int = 0, col: int = 0) -> str:
    cx = x + w / 2
    iy = y + h * 0.40
    if slug:
        s = icon / 24
        glyph = (f'<path fill="{TEXT}" transform="translate({cx - icon / 2:.1f} {iy - icon / 2:.1f}) scale({s:.3f})" '
                 f'd="{icon_path(slug)}"/>')
    else:  # lettermark for brands without a CC0 icon
        glyph = (f'<rect x="{cx - icon / 2:.1f}" y="{iy - icon / 2:.1f}" width="{icon}" height="{icon}" rx="7" '
                 f'fill="none" stroke="{TEXT}" stroke-width="2.4"/><text x="{cx:.1f}" y="{iy + icon * 0.2:.1f}" '
                 f'text-anchor="middle" font-family="MM Mono Bold" font-size="{icon * 0.55:.0f}" fill="{TEXT}">'
                 f'{name[0]}</text>')
    enter = 0.15 + row * 0.12 + col * 0.05
    wave = f"{2.2 + col * 0.16 + row * 0.22:.2f}s"
    return (f'<g class="tile" style="animation-delay:{enter:.2f}s">'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="14" fill="{PANEL}" stroke="{LINE}" '
            f'stroke-width="1.5"/>'
            f'<rect class="lit" opacity="0" style="animation-delay:{wave}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" '
            f'rx="14" fill="url(#glow)" stroke="{ACCENT}" stroke-opacity="0.8" stroke-width="1.5"/>'
            f'<g class="ic" style="animation-delay:{wave}">{glyph}</g><text x="{cx:.1f}" y="{y + h * 0.82:.1f}" '
            f'text-anchor="middle" font-family="MM Mono" font-size="{label}" letter-spacing="0.6" fill="{SOFT}">'
            f'{esc(name)}</text></g>')


def frame(w: int, h: int, body: str) -> str:
    labels = "".join(cat.upper() for cat, _ in STACK) + "".join(n for _, items in STACK for n, _ in items)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="t d"><title id="t">Toolkit</title><desc id="d">{esc(DESC)}</desc>'
            f'<style>{font_css(mono=labels, monobold=labels + "P")}{MOTION}</style>'
            f'<defs><radialGradient id="g" cx="1" cy="0" r="0.9"><stop offset="0" stop-color="{ACCENT}" '
            f'stop-opacity="0.12"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient>'
            f'<radialGradient id="glow" cx="0.5" cy="0.35" r="0.75"><stop offset="0" stop-color="{ACCENT}" '
            f'stop-opacity="0.22"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0.04"/></radialGradient></defs>'
            f'<rect width="{w}" height="{h}" rx="28" fill="{INK}"/><rect width="{w}" height="{h}" rx="28" fill="url(#g)"/>'
            f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="27.25" fill="none" stroke="{LINE}" '
            f'stroke-width="1.5"/>{body}</svg>')


def category(x: float, y: float, name: str, size: float) -> str:
    w = measure(name.upper(), "monobold", size, 3)
    return (f'<text x="{x}" y="{y}" font-family="MM Mono Bold" font-size="{size}" letter-spacing="3" '
            f'fill="{MUTED}">{esc(name.upper())}</text>'
            f'<rect class="bar" x="{x}" y="{y + 12}" width="{min(w, 26):.0f}" height="2" fill="{ACCENT}"/>')


def desktop() -> str:
    tw, th, gap, x0, top, row = 132, 112, 14, 290, 48, 136
    body = ""
    for r, (cat, items) in enumerate(STACK):
        y = top + r * row
        body += category(48, y + th / 2 + 4, cat, 14)
        for i, (name, slug) in enumerate(items):
            body += tile(x0 + i * (tw + gap), y, tw, th, name, slug, 34, 13.5, r, i)
    return frame(1200, top + row * len(STACK) - (row - th) + 48, body)


def phone() -> str:
    per, gap, pad = 3, 14, 36
    tw = (600 - 2 * pad - gap * (per - 1)) / per
    th = 128
    body, y = "", 64
    for n, (cat, items) in enumerate(STACK):
        body += category(pad, y, cat, 17)
        y += 34
        for i, (name, slug) in enumerate(items):
            r, c = divmod(i, per)
            body += tile(pad + c * (tw + gap), y + r * (th + gap), tw, th, name, slug, 40, 17, n * 2 + r, c)
        y += ((len(items) - 1) // per + 1) * (th + gap) + 44
    return frame(600, int(y - 10), body)


def main() -> None:
    write(ASSETS / "stack.svg", desktop())
    write(ASSETS / "stack-phone.svg", phone())


if __name__ == "__main__":
    main()
