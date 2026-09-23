# Design direction

**Quiet money after dark.** Near-black graphite, bone-white type, one cold steel accent, and a high-contrast Didone set like a masthead. It should read like a private dossier: ruled paper, corner registration marks, coordinates instead of a city name. The screenshots are the only saturated color on the page. The palette lives in `scripts/brand.py`, which every generator imports.

## Type

| Key | Face | Use | License |
| :-- | :-- | :-- | :-- |
| `display` | Bodoni Moda 500, opsz 96 | The name (uppercase, +6 tracking), card titles, section words | OFL, committed |
| `serif` | Bodoni Moda Italic 400, opsz 96 | Taglines and the second word of each heading, in steel | OFL, committed |
| `body` / `bodybold` | Switzer 400 / 500 | Body copy and descriptions | ITF Free Font License, **not committed** |
| `mono` / `monobold` | IBM Plex Mono 400 / 600 | The typing line, labels, pills, status, coordinates | OFL, committed |

`scripts/fetch_fonts.py` downloads all three and writes the static instances into `scripts/fonts/`.

Switzer's license forbids redistributing the font file and only allows embedding that can't be extracted. So Switzer never goes into the repo, and never into an SVG as a font: `brand.outline()` draws it as paths, and cards are rasterized to WebP. Bodoni and Plex are embedded in SVGs as glyph subsets (base64 WOFF), since images on GitHub can't load web fonts.

## Color tokens

| Token | Hex | Use |
| :-- | :-- | :-- |
| `INK` | `#0A0A0A` | Card background |
| `PANEL` | `#111111` | Tiles, buttons, windows inside a card |
| `RAISED` | `#171717` | Window chrome, raised boxes |
| `LINE` | `#262626` | Borders and rules |
| `TEXT` | `#ECE9E2` | Bone. Titles and primary text |
| `SOFT` | `#B3AFA7` | Body copy, pill labels |
| `MUTED` | `#86827A` | Secondary labels and captions |
| **`ACCENT`** | `#A9B4C0` | Steel. Italic taglines, eyebrows, the caret. The one thing to look at |
| `ACCENT_DEEP` | `#3F4955` | Steel on white (light-theme headings) |
| `SIGNAL` | `#F4F0E6` | Status only: a glowing dot for "live" or "now building", always with a label |

Light-theme section headings use `LIGHT_TEXT` `#111111`, `LIGHT_MUTED` `#5E5A54` and `LIGHT_LINE` `#DAD6CF` on GitHub's white page. Dark cards look the same in both themes.

Background light is white at 7–9% opacity from the top-left (a desk lamp), plus a faint steel glow bottom-right. No stars, no gradients in the type, no second hue.

## Layout

- Desktop art is 1200 wide with a 28px radius, a 1.5px `LINE` border and corner registration ticks. Cards render at 2× as WebP.
- Every card and panel has a **phone variant** (500–600 wide, stacked layout), chosen with `<picture>` `media="(max-width: 600px)"`. Section headings too.
- Section headings: a mono index (`01 /`), a Bodoni word, a steel Bodoni italic word, a hairline, and a small steel diamond.

## Motion

- **Hero typing line:** "› I build …" types, holds, deletes and cycles through five phrases, driven by SMIL `<animate>` on clip rects, so it works inside `<img>` on GitHub. The steel caret blinks.
- **Hero sheen:** a soft light band sweeps across the name every 9 seconds.
- **Status pulse:** the "now building" and "say hello" dots breathe.
- **Every animation adds to a finished frame.** Without animation the hero shows the first phrase in full with the caret after it, and the name without the sheen.
- CSS motion (caret, pulse) turns off under `prefers-reduced-motion`. SMIL can't read that media query, so the typing and sheen still run.

## Build

```sh
python3 -m venv .venv && .venv/bin/pip install fonttools pillow
.venv/bin/python scripts/fetch_fonts.py   # once, or after a clean clone
.venv/bin/python scripts/build.py         # every asset
.venv/bin/python scripts/cards.py ledger  # one card
.venv/bin/python scripts/preview.py       # README in light/dark/phone, into .preview/
```

Cards need Google Chrome. Live-site screenshots live in `scripts/shots/`; the Ledger.m one has its dollar amounts blanked.

The contribution snake is drawn by `.github/workflows/snake.yml` (Platane/snk) in greyscale every 12 hours and pushed to the `output` branch.

## Do

- Put the facts in the markdown too (alt text and link lines), so the page works without images.
- Keep one idea per card and let the screenshots carry the color.
- Use steel sparingly. If two things are steel on one card, one of them shouldn't be.

## Don't

- Don't add a hue. Gold, violet or neon would break the monochrome.
- Don't use emoji as icons or bullets.
- Don't commit Switzer or embed it as a font.
- Don't embed third-party stat cards or badges. They break the palette and go down.
- Don't claim anything the repos don't show (users, metrics, App Store status).
