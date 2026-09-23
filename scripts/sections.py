"""Section headings in light and dark: a star mark, a grotesk word and a serif italic word."""

from __future__ import annotations

from brand import (ASSETS, LIGHT_LINE, LIGHT_TEXT, LINE, TEXT, VIOLET, VIOLET_DEEP, esc, font_css, measure,
                   write)

SECTIONS = {
    "work": ("Selected", "work"),
    "building": ("Still", "building"),
    "toolkit": ("The", "toolkit"),
    "activity": ("Lately on", "GitHub"),
}

W, H = 1200, 104
DISPLAY, SERIF = 56, 64


def star(cx: float, cy: float, r: float, fill: str) -> str:
    """Four-point star, the mark used across the profile."""
    k = r * 0.22
    return (f'<path fill="{fill}" d="M{cx} {cy - r} Q{cx + k} {cy - k} {cx + r} {cy} Q{cx + k} {cy + k} {cx} {cy + r} '
            f'Q{cx - k} {cy + k} {cx - r} {cy} Q{cx - k} {cy - k} {cx} {cy - r}Z"/>')


def heading(word: str, accent: str, dark: bool, W: int = W) -> str:
    """W is 1200 on desktop and 600 on phones, where the same type renders twice as large."""
    text, violet, line = (TEXT, VIOLET, LINE) if dark else (LIGHT_TEXT, VIOLET_DEEP, LIGHT_LINE)
    x0 = 44
    w1 = measure(word + " ", "display", DISPLAY, -1.5)
    w2 = measure(accent, "serif", SERIF)
    end = x0 + w1 + w2 + 28
    body = f"""
<style>{font_css(display=word, serif=accent)}</style>
{star(16, 58, 14, violet)}
<text x="{x0}" y="76" font-family="MM Display" font-size="{DISPLAY}" letter-spacing="-1.5" fill="{text}">{esc(word)} <tspan font-family="MM Serif" font-size="{SERIF}" letter-spacing="0" fill="{violet}">{esc(accent)}</tspan></text>
<line x1="{end:.0f}" y1="58.5" x2="{W - 30}" y2="58.5" stroke="{line}" stroke-width="1.5"/>
{star(W - 12, 58.5, 7, violet)}"""
    title = f"{word} {accent}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{esc(title)}"><title>{esc(title)}</title>{body}</svg>')


def main() -> None:
    for key, (word, accent) in SECTIONS.items():
        for theme in ("dark", "light"):
            write(ASSETS / "sections" / f"{key}-{theme}.svg", heading(word, accent, theme == "dark"))
            write(ASSETS / "sections" / f"{key}-{theme}-phone.svg", heading(word, accent, theme == "dark", W=600))


if __name__ == "__main__":
    main()
