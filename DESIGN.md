# Design direction

The profile reads as **a night sky of finished work**: midnight cards with a faint starfield, big grotesk titles, a serif italic voice, and one ultraviolet accent. Each project gets its own card built around a real screenshot or a diagram of how it works. The palette lives in `scripts/brand.py`, which every generator imports.

## Type

Three families, all SIL OFL 1.1, stored in `scripts/fonts/`:

- **Bricolage Grotesque**: 800 at display size for names and titles (`display`), 400 and 600 for body copy (`body`, `bodybold`).
- **Instrument Serif Italic** (`serif`): taglines only. The accent half of a tagline is violet.
- **JetBrains Mono** 500 and 700 (`mono`, `monobold`): UPPERCASE labels, eyebrows, tech pills and status, with +2 to +4 tracking.

SVGs embed a subset of each font (only the glyphs they use) as base64 WOFF, since images on GitHub can't load web fonts. Cards are HTML rendered by headless Chrome, so they use the TTFs directly.

## Color tokens

| Token | Hex | Use |
| :-- | :-- | :-- |
| `INK` | `#0A0A10` | Card background |
| `PANEL` | `#12121A` | Tiles, buttons, windows inside a card |
| `RAISED` | `#1A1A25` | Window chrome, raised boxes |
| `LINE` | `#272733` | Borders and rules |
| `TEXT` | `#F3F1F8` | Titles and primary text |
| `SOFT` | `#C7C3D4` | Body copy, pill labels |
| `MUTED` | `#8E8A9E` | Secondary labels and captions |
| **`VIOLET`** | `#A994FF` | Brand accent: eyebrows, the name's period, tagline accents, the star mark |
| `VIOLET_DEEP` | `#5A3FD9` | Violet on white (light-theme section headings, light snake) |
| **`VOLT`** | `#D4FF4F` | Signal only: something is live or running right now |

Light-theme section headings use `LIGHT_TEXT` `#1B1830` and `LIGHT_LINE` `#E2DEF0` on GitHub's white page. Dark cards look the same in both themes.

**Status is never color alone.** Every status dot sits next to a label (`LIVE`, `PRIVATE DEPLOY`, `PRIVATE BETA`, `IN DEVELOPMENT`).

## Layout

- Desktop art is 1200 wide with a 28px radius and a 1.5px `LINE` border. Cards render at 2× as WebP.
- Every card and panel has a **phone variant** (500–600 wide, stacked layout), chosen with `<picture>` `media="(max-width: 600px)"`.
- Section headings are a four-point star, a grotesk word and a serif italic word, with light and dark versions chosen by `prefers-color-scheme`.
- Screenshot windows bleed off the card edge, which reads as "there's more."

## Motion

- Only in SVGs: twinkling stars, a slow orbit around the header constellation, and a pulsing `VOLT` dot.
- **Every animation adds to a finished frame.** Without CSS the graphic is complete. Nothing types in or fades in from empty.
- Each animated SVG turns its motion off under `prefers-reduced-motion: reduce`.
- Animated SVGs are embedded with `<img>`/`<picture>` so GitHub keeps the animation.

## Build

```sh
python3 -m venv .venv && .venv/bin/pip install fonttools pillow
.venv/bin/python scripts/build.py     # every asset
.venv/bin/python scripts/cards.py ledger   # one card
.venv/bin/python scripts/preview.py   # README in light/dark/phone, into .preview/
```

Cards need Google Chrome. Screenshots of the live sites live in `scripts/shots/`; the Ledger.m one has its dollar amounts blanked.

The contribution snake is drawn by `.github/workflows/snake.yml` (Platane/snk) every 12 hours and pushed to the `output` branch.

## Do

- Put the facts in the markdown too (alt text and link lines), so the page works without images.
- Keep one idea per card, and let the screenshots carry the color.
- Use `VIOLET` for what to look at first, and nothing else competing with it.

## Don't

- Don't use emoji as icons or bullets.
- Don't add a typeface or accent color without adding it here first.
- Don't use `VOLT` for decoration. It means live.
- Don't embed third-party stat cards or badges. They break the palette and go down.
- Don't claim anything the repos don't show (users, metrics, App Store status).
