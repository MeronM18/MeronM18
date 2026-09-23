"""Closing card and contact buttons (desktop + phone)."""

from __future__ import annotations

from header import signature
from brand import (shape, ASSETS, INK, LINE, MUTED, PANEL, SOFT, TEXT, ACCENT, SIGNAL, esc, font_css, measure,
                   write)

LINE_A = "Got an idea worth shipping?"
LINE_B = "Let's build it."
KICKER = "SAY HELLO"
SIGN = "MERON MATTI · MICHIGAN · THANKS FOR STOPPING BY"
EMAIL = "meronmatti123@gmail.com"

# file name: (glyph, label, style). "ghost" is a label, not a link: dashed and muted.
BUTTONS = {
    "linkedin": ("linkedin", "LinkedIn", "solid"),
    "email": ("email", "Email me", "solid"),
    "github": ("github", "Follow on GitHub", "solid"),
    "demo": ("play", "Watch the demo", "solid"),
    "live": ("arrow", "Visit the live site", "solid"),
    "source": ("github", "Source", "solid"),
    "private": ("lock", "Private deployment", "ghost"),
    "staydue": ("github", "StayDue", "solid"),
    "easymail": ("github", "EasyMail", "solid"),
}

MOTION = (
    # The signature writes itself, holds, fades and writes again, so it plays whenever you scroll here.
    "@keyframes sig{0%{stroke-dashoffset:1;fill-opacity:0;opacity:1}16%{stroke-dashoffset:0;fill-opacity:0}"
    "24%{fill-opacity:1}86%{opacity:1;stroke-dashoffset:0;fill-opacity:1}"
    "94%,100%{opacity:0;stroke-dashoffset:0;fill-opacity:1}}"
    ".sig{stroke-dasharray:1;animation:sig 9s cubic-bezier(.55,0,.35,1) infinite both}"
    "@keyframes pulse{0%,100%{opacity:.9}50%{opacity:.35}}.pulse{animation:pulse 2.4s ease-in-out infinite}"
    "@media (prefers-reduced-motion:reduce){.pulse,.sig{animation:none}}"
)


def backdrop(w: int, h: int, seed: int) -> str:
    ticks = "".join(
        f'<path d="M{x} {y + dy * 16}V{y}H{x + dx * 16}" fill="none" stroke="#3A3A3A" stroke-width="1.5"/>'
        for x, y, dx, dy in ((24, 24, 1, 1), (w - 24, 24, -1, 1), (24, h - 24, 1, -1), (w - 24, h - 24, -1, -1))
    )
    return f"""
<defs>
  <radialGradient id="g1" cx="0.5" cy="-0.2" r="0.85">
    <stop offset="0" stop-color="#fff" stop-opacity="0.09"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </radialGradient>
  <clipPath id="frame"><rect width="{w}" height="{h}" rx="28"/></clipPath>
</defs>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="{INK}"/>
  <rect width="{w}" height="{h}" fill="url(#g1)"/>
</g>
{ticks}
<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="27.25" fill="none" stroke="{LINE}" stroke-width="1.5"/>"""


def kicker(cx: float, y: float, size: float) -> str:
    w = measure(KICKER, "monobold", size, 4)
    x = cx - (w + 34) / 2
    return (f'<circle cx="{x + 8}" cy="{y - size * 0.36:.1f}" r="{size * 0.9:.1f}" fill="{SIGNAL}" opacity="0.18" class="pulse"/>'
            f'<circle cx="{x + 8}" cy="{y - size * 0.36:.1f}" r="{size * 0.36:.1f}" fill="{SIGNAL}"/>'
            f'<text x="{x + 34:.1f}" y="{y}" font-family="MM Mono Bold" font-size="{size}" letter-spacing="4" '
            f'fill="{ACCENT}">{KICKER}</text>')


def card(w: int, h: int, body: str, seed: int) -> str:
    desc = f"{LINE_A} {LINE_B} Email {EMAIL} or find me on LinkedIn."
    fonts = font_css(display=LINE_A, monobold=KICKER, mono=SIGN + EMAIL)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="t d"><title id="t">Contact</title><desc id="d">{esc(desc)}</desc>'
            f"<style>{fonts}{MOTION}</style>{backdrop(w, h, seed)}{body}</svg>")


def script_line(cx: float, y: float, size: float) -> str:
    _, width = shape(LINE_B, "script", size)
    return signature(LINE_B, cx - width / 2, y, size, start=0, sheen=False)


def desktop() -> str:
    w, h = 1200, 430
    body = f"""
{kicker(w / 2, 100, 15)}
<text x="{w / 2}" y="190" text-anchor="middle" font-family="MM Display" font-size="70" letter-spacing="-0.5" fill="{TEXT}">{esc(LINE_A)}</text>
{script_line(w / 2, 286, 104)}
<text x="{w / 2}" y="370" text-anchor="middle" font-family="MM Mono" font-size="14" letter-spacing="2.4" fill="{MUTED}">{esc(SIGN)}</text>"""
    return card(w, h, body, seed=61)


def phone() -> str:
    w, h = 600, 540
    body = f"""
{kicker(w / 2, 96, 17)}
<text x="{w / 2}" y="190" text-anchor="middle" font-family="MM Display" font-size="60" letter-spacing="-0.5" fill="{TEXT}">Got an idea</text>
<text x="{w / 2}" y="256" text-anchor="middle" font-family="MM Display" font-size="60" letter-spacing="-0.5" fill="{TEXT}">worth shipping?</text>
{script_line(w / 2, 368, 100)}
<text x="{w / 2}" y="462" text-anchor="middle" font-family="MM Mono" font-size="16" letter-spacing="2" fill="{MUTED}">THANKS FOR STOPPING BY</text>"""
    return card(w, h, body, seed=63)


# 24x24 glyphs, drawn as strokes so they need no third-party icon.
GLYPHS = {
    "linkedin": ('<rect x="2" y="2" width="20" height="20" rx="4" fill="none" stroke="{c}" stroke-width="2"/>'
                 '<path d="M7 10v7M7 7v.01M11 17v-7M11 13.5c0-2 1.2-3.5 3-3.5s3 1.2 3 3.5V17" fill="none" '
                 'stroke="{c}" stroke-width="2" stroke-linecap="round"/>'),
    "email": ('<rect x="2" y="4.5" width="20" height="15" rx="3" fill="none" stroke="{c}" stroke-width="2"/>'
              '<path d="M3 6.5l9 6.5 9-6.5" fill="none" stroke="{c}" stroke-width="2" stroke-linejoin="round"/>'),
    "play": ('<circle cx="12" cy="12" r="10" fill="none" stroke="{c}" stroke-width="2"/>'
             '<path d="M10 8.2v7.6l6-3.8z" fill="{c}"/>'),
    "arrow": ('<path d="M7 17L17 7M9 7h8v8" fill="none" stroke="{c}" stroke-width="2" stroke-linecap="round" '
              'stroke-linejoin="round"/>'),
    "lock": ('<rect x="4.5" y="10.5" width="15" height="10.5" rx="2.5" fill="none" stroke="{c}" stroke-width="2"/>'
             '<path d="M8 10.5V7.5a4 4 0 0 1 8 0v3" fill="none" stroke="{c}" stroke-width="2"/>'),
    "github": ('<path d="M12 2a10 10 0 0 0-3.2 19.5c.5.1.7-.2.7-.5v-1.7c-2.8.6-3.4-1.3-3.4-1.3-.5-1.2-1.1-1.5-1.1-1.5'
               '-.9-.6.1-.6.1-.6 1 .1 1.5 1 1.5 1 .9 1.5 2.3 1.1 2.9.8.1-.6.3-1.1.6-1.3-2.2-.3-4.6-1.1-4.6-5 0-1.1.4-2'
               ' 1-2.7-.1-.3-.4-1.3.1-2.7 0 0 .8-.3 2.7 1a9.4 9.4 0 0 1 5 0c1.9-1.3 2.7-1 2.7-1 .5 1.4.2 2.4.1 2.7.6.7'
               ' 1 1.6 1 2.7 0 3.9-2.4 4.7-4.6 5 .4.3.7.9.7 1.9V21c0 .3.2.6.7.5A10 10 0 0 0 12 2z" fill="{c}"/>'),
}


def button(glyph_key: str, label: str, style: str = "solid") -> str:
    size, h = 17, 60
    tw = measure(label.upper(), "monobold", size, 2.4)
    w = int(28 + 24 + 14 + tw + 30)
    ghost = style == "ghost"
    glyph = GLYPHS[glyph_key].format(c=MUTED if ghost else ACCENT)
    frame = (f'fill="none" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="5 5"' if ghost
             else f'fill="{PANEL}" stroke="{LINE}" stroke-width="1.5"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-label="{esc(label)}"><title>{esc(label)}</title>'
            f'<style>{font_css(monobold=label.upper())}</style>'
            f'<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="{(h - 1.5) / 2}" {frame}/>'
            f'<g transform="translate(28 {(h - 24) / 2})">{glyph}</g>'
            f'<text x="{28 + 24 + 14}" y="{h / 2 + size * 0.36:.1f}" font-family="MM Mono Bold" font-size="{size}" '
            f'letter-spacing="2.4" fill="{MUTED if ghost else SOFT}">{esc(label.upper())}</text></svg>')


def main() -> None:
    write(ASSETS / "footer.svg", desktop())
    write(ASSETS / "footer-phone.svg", phone())
    for name, (glyph, label, style) in BUTTONS.items():
        write(ASSETS / "buttons" / f"{name}.svg", button(glyph, label, style))


if __name__ == "__main__":
    main()
