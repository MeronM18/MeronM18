"""Section headings in light and dark: an index number, a Bodoni word and a Bodoni italic word."""

from __future__ import annotations

from brand import (ACCENT, ACCENT_DEEP, ASSETS, LIGHT_LINE, LIGHT_MUTED, LIGHT_TEXT, LINE, MUTED, TEXT, esc,
                   font_css, measure, write)

SECTIONS = {
    "work": ("01", "Selected", "work"),
    "building": ("02", "Still", "building"),
    "toolkit": ("03", "The", "toolkit"),
    "activity": ("04", "Lately on", "GitHub"),
}

W, H = 1200, 104
DISPLAY, SERIF, INDEX = 58, 60, 15


def heading(num: str, word: str, accent: str, dark: bool, W: int = W) -> str:
    """W is 1200 on desktop and 600 on phones, where the same type renders twice as large."""
    text, steel, line, muted = ((TEXT, ACCENT, LINE, MUTED) if dark
                                else (LIGHT_TEXT, ACCENT_DEEP, LIGHT_LINE, LIGHT_MUTED))
    label = f"{num} /"
    x0 = 4 + measure(label, "monobold", INDEX, 2) + 22
    w1 = measure(word + " ", "display", DISPLAY, -0.5)
    w2 = measure(accent, "serif", SERIF)
    end = x0 + w1 + w2 + 28
    body = f"""
<style>{font_css(display=word, serif=accent, monobold=label)}</style>
<text x="4" y="74" font-family="MM Mono Bold" font-size="{INDEX}" letter-spacing="2" fill="{muted}">{label}</text>
<text x="{x0:.1f}" y="78" font-family="MM Display" font-size="{DISPLAY}" letter-spacing="-0.5" fill="{text}">{esc(word)} <tspan font-family="MM Serif" font-size="{SERIF}" letter-spacing="0" fill="{steel}">{esc(accent)}</tspan></text>
<line x1="{end:.0f}" y1="68.5" x2="{W - 18}" y2="68.5" stroke="{line}" stroke-width="1.5"/>
<rect x="{W - 12}" y="64.5" width="8" height="8" transform="rotate(45 {W - 8} 68.5)" fill="{steel}"/>"""
    title = f"{word} {accent}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="{esc(title)}"><title>{esc(title)}</title>{body}</svg>')


def main() -> None:
    for key, (num, word, accent) in SECTIONS.items():
        for theme in ("dark", "light"):
            write(ASSETS / "sections" / f"{key}-{theme}.svg", heading(num, word, accent, theme == "dark"))
            write(ASSETS / "sections" / f"{key}-{theme}-phone.svg", heading(num, word, accent, theme == "dark", W=600))


if __name__ == "__main__":
    main()
