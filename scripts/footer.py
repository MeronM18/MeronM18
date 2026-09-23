"""Closing card and contact buttons (desktop + phone)."""

from __future__ import annotations

from brand import (ASSETS, INK, LINE, MUTED, PANEL, SOFT, TEXT, VIOLET, VOLT, esc, font_css, measure, stars,
                   write)

LINE_A = "Got an idea worth shipping?"
LINE_B = "Let's build it."
KICKER = "SAY HELLO"
SIGN = "MERON MATTI · MICHIGAN · THANKS FOR STOPPING BY"
EMAIL = "meronmatti123@gmail.com"

BUTTONS = {
    "linkedin": "LinkedIn",
    "email": "Email me",
    "github": "Follow on GitHub",
}

MOTION = (
    "@keyframes tw{0%,100%{opacity:1}50%{opacity:.3}}.tw{animation:tw 3.6s ease-in-out infinite}"
    "@keyframes pulse{0%,100%{opacity:.9}50%{opacity:.35}}.pulse{animation:pulse 2.4s ease-in-out infinite}"
    "@media (prefers-reduced-motion:reduce){.tw,.pulse{animation:none}}"
)


def backdrop(w: int, h: int, seed: int) -> str:
    twinkle = ' class="tw"'
    field = "".join(
        f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" opacity="{o * 0.55:.2f}"'
        f'{twinkle if i % 5 == 0 else ""}/>'
        for i, (x, y, r, o) in enumerate(stars(60, w, h, seed))
    )
    return f"""
<defs>
  <radialGradient id="g1" cx="0.5" cy="1.15" r="0.8">
    <stop offset="0" stop-color="{VIOLET}" stop-opacity="0.30"/><stop offset="1" stop-color="{VIOLET}" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="28"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="{INK}"/>
  <rect width="{w}" height="{h}" fill="url(#g1)"/>
  {field}
</g>
<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="27.25" fill="none" stroke="{LINE}" stroke-width="1.5"/>"""


def kicker(cx: float, y: float, size: float) -> str:
    w = measure(KICKER, "monobold", size, 4)
    x = cx - (w + 34) / 2
    return (f'<circle cx="{x + 8}" cy="{y - size * 0.36:.1f}" r="{size * 0.9:.1f}" fill="{VOLT}" opacity="0.18" class="pulse"/>'
            f'<circle cx="{x + 8}" cy="{y - size * 0.36:.1f}" r="{size * 0.36:.1f}" fill="{VOLT}"/>'
            f'<text x="{x + 34:.1f}" y="{y}" font-family="MM Mono Bold" font-size="{size}" letter-spacing="4" '
            f'fill="{VIOLET}">{KICKER}</text>')


def card(w: int, h: int, body: str, seed: int) -> str:
    desc = f"{LINE_A} {LINE_B} Email {EMAIL} or find me on LinkedIn."
    fonts = font_css(display=LINE_A, serif=LINE_B, monobold=KICKER, mono=SIGN + EMAIL)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="t d"><title id="t">Contact</title><desc id="d">{esc(desc)}</desc>'
            f"<style>{fonts}{MOTION}</style>{backdrop(w, h, seed)}{body}</svg>")


def desktop() -> str:
    w, h = 1200, 400
    body = f"""
{kicker(w / 2, 100, 15)}
<text x="{w / 2}" y="190" text-anchor="middle" font-family="MM Display" font-size="68" letter-spacing="-2" fill="{TEXT}">{esc(LINE_A)}</text>
<text x="{w / 2}" y="258" text-anchor="middle" font-family="MM Serif" font-size="64" fill="{VIOLET}">{esc(LINE_B)}</text>
<text x="{w / 2}" y="336" text-anchor="middle" font-family="MM Mono" font-size="14" letter-spacing="2.4" fill="{MUTED}">{esc(SIGN)}</text>"""
    return card(w, h, body, seed=61)


def phone() -> str:
    w, h = 600, 520
    body = f"""
{kicker(w / 2, 96, 17)}
<text x="{w / 2}" y="190" text-anchor="middle" font-family="MM Display" font-size="58" letter-spacing="-1.8" fill="{TEXT}">Got an idea</text>
<text x="{w / 2}" y="256" text-anchor="middle" font-family="MM Display" font-size="58" letter-spacing="-1.8" fill="{TEXT}">worth shipping?</text>
<text x="{w / 2}" y="340" text-anchor="middle" font-family="MM Serif" font-size="64" fill="{VIOLET}">{esc(LINE_B)}</text>
<text x="{w / 2}" y="432" text-anchor="middle" font-family="MM Mono" font-size="16" letter-spacing="2" fill="{MUTED}">THANKS FOR STOPPING BY</text>"""
    return card(w, h, body, seed=63)


# 24x24 glyphs, drawn as strokes so they need no third-party icon.
GLYPHS = {
    "linkedin": ('<rect x="2" y="2" width="20" height="20" rx="4" fill="none" stroke="{c}" stroke-width="2"/>'
                 '<path d="M7 10v7M7 7v.01M11 17v-7M11 13.5c0-2 1.2-3.5 3-3.5s3 1.2 3 3.5V17" fill="none" '
                 'stroke="{c}" stroke-width="2" stroke-linecap="round"/>'),
    "email": ('<rect x="2" y="4.5" width="20" height="15" rx="3" fill="none" stroke="{c}" stroke-width="2"/>'
              '<path d="M3 6.5l9 6.5 9-6.5" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>'),
    "github": ('<path d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.3-3.4-1.3-.5-1.2-1.1-1.5-1.1-1.5'
               '-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.3 1.1 2.9.8.1-.6.3-1.1.6-1.3-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2'
               ' 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.7 1a9.4 9.4 0 0 1 5 0c1.9-1.3 2.7-1 2.7-1 .5 1.4.2 2.4.1 2.7.6.7'
               ' 1 1.6 1 2.7 0 3.9-2.4 4.7-4.6 5 .4.3.7.9.7 1.9V21c0 .3.2.6.7.5A10 10 0 0 0 12 2z" fill="{c}"/>'),
}


def button(key: str, label: str) -> str:
    size, h = 17, 60
    tw = measure(label.upper(), "monobold", size, 2.4)
    w = int(28 + 24 + 14 + tw + 30)
    glyph = GLYPHS[key].format(c=VIOLET)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{esc(label)}"><title>{esc(label)}</title>'
            f'<style>{font_css(monobold=label.upper())}</style>'
            f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="{(h - 1.5) / 2}" fill="{PANEL}" '
            f'stroke="{LINE}" stroke-width="1.5"/>'
            f'<g transform="translate(28 {(h - 24) / 2})">{glyph}</g>'
            f'<text x="{28 + 24 + 14}" y="{h / 2 + size * 0.36:.1f}" font-family="MM Mono Bold" font-size="{size}" '
            f'letter-spacing="2.4" fill="{SOFT}">{esc(label.upper())}</text></svg>')


def main() -> None:
    write(ASSETS / "footer.svg", desktop())
    write(ASSETS / "footer-phone.svg", phone())
    for key, label in BUTTONS.items():
        write(ASSETS / "buttons" / f"{key}.svg", button(key, label))


if __name__ == "__main__":
    main()
