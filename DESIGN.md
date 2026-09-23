# Design direction

**Quiet money after dark.** Near-black graphite, bone-white type, one cold steel accent, a script signature for the name and a high-contrast Didone for everything titled. It should read like a private dossier: ruled paper, corner registration marks, coordinates instead of a city name. Even the screenshots are toned toward steel. The palette lives in `scripts/brand.py`, which every generator imports.

## Type

| Key | Face | Use | License |
| :-- | :-- | :-- | :-- |
| `script` | Imperial Script | The hero name only, drawn as paths so it can write itself | OFL, committed |
| `display` | Bodoni Moda 500, opsz 96 | Card titles, section words | OFL, committed |
| `serif` | Bodoni Moda Italic 400, opsz 96 | Taglines and the second word of each heading, in steel | OFL, committed |
| `body` / `bodybold` | Switzer 400 / 500 | Body copy and descriptions | ITF Free Font License, **not committed** |
| `mono` / `monobold` | IBM Plex Mono 400 / 600 | The typing line, labels, pills, status, coordinates | OFL, committed |

`scripts/fetch_fonts.py` downloads all four and writes the static instances into `scripts/fonts/`.

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
- **Hero signature:** on load, each glyph of the script name is traced as an outline (`stroke-dashoffset` on a `pathLength="1"` path per glyph, staggered left to right), then fills with ink. The rule below it draws out after.
- **Hero sheen:** once the name is written, a soft light band sweeps across it every 8 seconds.
- **Toolkit:** tiles rise in row by row on load, then a diagonal wave of steel light passes through the grid every 6 seconds, lifting each logo as it goes. Category underlines draw in.
- **Imperium card:** an animated WebP (44 frames, ~330 KB, 7.6 s loop). The message arrives, PAIR → PLAN → PERMIT → GATE check off in turn while the progress line fills, RUN lights up, the audit entry is written, then it holds and resets. `cards.py` renders each frame's state in Chrome (`imperium_state(t)`) and `brand.render_anim` assembles them, 15 fps while moving and one long frame while holding.
- **Stats panel:** the weekly contributions line draws itself, the area and peak marker fade in, the language bar grows segment by segment.
- **Section headings:** the hairline draws out from the words and the diamond lands at its end.
- **Status pulse:** the "now building" and "say hello" dots breathe.
- **Every animation adds to a finished frame.** Without animation the hero shows the whole name and the first phrase in full with the caret after it, and the toolkit shows every tile unlit.
- CSS motion (signature, rule, caret, pulse, toolkit) turns off under `prefers-reduced-motion`. SMIL can't read that media query, so the typing and sheen still run.

## Build

```sh
python3 -m venv .venv && .venv/bin/pip install fonttools pillow uharfbuzz
.venv/bin/python scripts/fetch_fonts.py   # once, or after a clean clone
.venv/bin/python scripts/build.py         # every asset
.venv/bin/python scripts/cards.py ledger  # one card
.venv/bin/python scripts/preview.py       # README in light/dark/phone, into .preview/
```

Cards need Google Chrome. Live-site screenshots live in `scripts/shots/`; the Ledger.m one has its dollar amounts blanked. Bright screenshots get `tone=True` in `cards.py`, a steel duotone (grayscale, dimmed, steel tint) so they sit in the monochrome page. Dummy Peptides uses it; Cosmo's phone gets the same steel treatment through a CSS filter.

`.github/workflows/profile.yml` runs every 3 hours and on every push to main. It rebuilds the hero with a live **Now building** list, the **stats panel** (`scripts/stats.py`: contribution calendar and language bytes from the GraphQL API, falling back to `scripts/stats-snapshot.json`), (`scripts/now.py`: my two most recently pushed public repos from the last 21 days, excluding this repo, forks, templates and archived repos, with EasyMail · StayDue as the fallback), draws the contribution snake in greyscale, and publishes both to the `output` branch. The README loads the hero from there, so main never gets automated commits. `assets/header.svg` is the local copy.

## Still building

The in-progress card is built from each repo's commit history and status docs: StayDue's README and commits, and EasyMail's `PROJECT_STATE.md` phase checklist. Update `STAYDUE_LOG`, `EASYMAIL_LOG` and `EASYMAIL_PHASE` in `scripts/cards.py` when those move.

## Do

- Put the facts in the markdown too (alt text and link lines), so the page works without images.
- Keep one idea per card. Tone bright screenshots down to steel rather than letting them break the palette.
- Use steel sparingly. If two things are steel on one card, one of them shouldn't be.

## Don't

- Don't add a hue. Gold, violet or neon would break the monochrome.
- Don't use emoji as icons or bullets.
- Don't commit Switzer or embed it as a font.
- Don't embed third-party stat cards or badges. They break the palette and go down.
- Don't claim anything the repos don't show (users, metrics, App Store status).
