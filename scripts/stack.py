"""Toolkit grid: rows of icon tiles, one row per category (desktop + phone)."""

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


def tile(x: float, y: float, w: float, h: float, name: str, slug: str | None, icon: float, label: float) -> str:
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
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="14" fill="{PANEL}" stroke="{LINE}" '
            f'stroke-width="1.5"/>{glyph}<text x="{cx:.1f}" y="{y + h * 0.82:.1f}" text-anchor="middle" '
            f'font-family="MM Mono" font-size="{label}" letter-spacing="0.6" fill="{SOFT}">{esc(name)}</text>')


def frame(w: int, h: int, body: str) -> str:
    labels = "".join(cat.upper() for cat, _ in STACK) + "".join(n for _, items in STACK for n, _ in items)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="t d"><title id="t">Toolkit</title><desc id="d">{esc(DESC)}</desc>'
            f'<style>{font_css(mono=labels, monobold=labels + "P")}</style>'
            f'<defs><radialGradient id="g" cx="1" cy="0" r="0.9"><stop offset="0" stop-color="{ACCENT}" '
            f'stop-opacity="0.14"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="{w}" height="{h}" rx="28" fill="{INK}"/><rect width="{w}" height="{h}" rx="28" fill="url(#g)"/>'
            f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="27.25" fill="none" stroke="{LINE}" '
            f'stroke-width="1.5"/>{body}</svg>')


def category(x: float, y: float, name: str, size: float) -> str:
    w = measure(name.upper(), "monobold", size, 3)
    return (f'<text x="{x}" y="{y}" font-family="MM Mono Bold" font-size="{size}" letter-spacing="3" '
            f'fill="{MUTED}">{esc(name.upper())}</text>'
            f'<rect x="{x}" y="{y + 12}" width="{min(w, 26):.0f}" height="2" fill="{ACCENT}"/>')


def desktop() -> str:
    tw, th, gap, x0, top, row = 132, 112, 14, 290, 48, 136
    body = ""
    for r, (cat, items) in enumerate(STACK):
        y = top + r * row
        body += category(48, y + th / 2 + 4, cat, 14)
        for i, (name, slug) in enumerate(items):
            body += tile(x0 + i * (tw + gap), y, tw, th, name, slug, 34, 13.5)
    return frame(1200, top + row * len(STACK) - (row - th) + 48, body)


def phone() -> str:
    per, gap, pad = 3, 14, 36
    tw = (600 - 2 * pad - gap * (per - 1)) / per
    th = 128
    body, y = "", 64
    for cat, items in STACK:
        body += category(pad, y, cat, 17)
        y += 34
        for i, (name, slug) in enumerate(items):
            r, c = divmod(i, per)
            body += tile(pad + c * (tw + gap), y + r * (th + gap), tw, th, name, slug, 40, 17)
        y += ((len(items) - 1) // per + 1) * (th + gap) + 44
    return frame(600, int(y - 10), body)


def main() -> None:
    write(ASSETS / "stack.svg", desktop())
    write(ASSETS / "stack-phone.svg", phone())


if __name__ == "__main__":
    main()
