# Design direction

The profile reads as a set of **terminal windows on a quiet page**. Dark cards carry the content, and the page around them stays calm. Everything comes from `assets/profile-header.svg`, which is the source of truth for palette, type and window style.

Direction chosen with the `ui-ux-pro-max` skill. Its design-system database was not installed, so this uses the skill's built-in rules (contrast, no emoji icons, phone layouts, meaningful and reduced motion, color tokens, a 12px text minimum), not a generated palette.

## Type

- **IBM Plex Mono** (SIL OFL 1.1) is the only typeface. Every letter is outlined into SVG paths by `scripts/build_assets.py`, so nothing depends on installed fonts.
- Weights: Regular for body, SemiBold for titles and prompts, Bold with letter-spacing for UPPERCASE labels.
- Sizes (desktop cards, 760 wide): labels 11–13px bold with +2 to +2.4 tracking, body 12–14px, titles 15–28px.
- Phone variants (400 wide) never go below 13px in the SVG. They render at about 0.85×, so the smallest text stays near 11–12px on screen.

## Color tokens

| Token | Hex | Use |
| :-- | :-- | :-- |
| `bg` | `#0A0A0B` | Card background |
| `panel` | `#111113` | Boxes inside a card |
| `border` | `#262628` | Card and box outlines |
| `rule` | `#242426` | Divider lines inside cards |
| `text` | `#F2F0EB` | Primary text |
| `soft` | `#B8B6B1` | Secondary text |
| `muted` | `#8A8A8A` | Labels, captions, "private" status (5.7:1 on `bg`) |
| `dim` | `#4A4946` | Separators and dotted connectors only, never text |
| **`accent`** | `#C9BFA8` | Brand: prompts, section numbers, the cursor, arrows, the monogram |
| **`live`** | `#8FBF8F` | Status only: something is deployed and public |
| **`build`** | `#D9A65B` | Status only: in development or private beta |

Light-theme section headings (transparent, on GitHub's white page): label `#57534C`, accent `#6F6450`, rule `#DAD5C9`. Both text colors pass 4.5:1 on white.

**Status is never shown by color alone.** Every status dot has a text label next to it: `LIVE` (live), `BETA` and `BUILDING` (build), and `PRIVATE`, `DEMO` and `SOURCE` (muted).

## Layout and spacing

- Desktop cards are 760 wide with an 18px corner radius, a 1.5px border, and window chrome (three dots, a caption, and a rule at y=52). Content starts 30px from the left edge.
- Inner boxes use a 10px radius, 14px gaps, and 14px padding.
- Spacing steps: 4, 8, 14, 24, 36.
- Each graphic has a **phone variant** 400 wide with a stacked layout, chosen with `<picture>` `media="(max-width: 600px)"`.
- Theme-dependent graphics (section headings) use `prefers-color-scheme` sources. Dark cards look the same in both themes, so they only have width variants.

## Motion

- Only three animations: the blinking cursor, a slow "live" pulse on status dots, and a highlight that walks through the Imperium pipeline.
- **Every animation adds to a finished frame.** Without CSS the graphic is complete, and the other keyframe state is also complete. Nothing types in or fades in from empty.
- Each animated SVG disables its motion under `prefers-reduced-motion: reduce`.
- Animated SVGs are embedded with `<img>` or `<picture>`, never inlined, so GitHub keeps the animation.

## Do

- Rebuild with `scripts/build_assets.py` and preview with `scripts/preview.py` in light, dark and phone before committing.
- Keep one idea per card, and let the screenshots carry the color.
- Put the facts in the markdown too (alt text and project text), so the page still works without images.
- Use the beige accent sparingly. It marks what to look at first.

## Don't

- Don't use emoji as icons or bullets.
- Don't add a new typeface, gradient or accent color without adding it to this file first.
- Don't use `live`/`build` green or amber for decoration. They mean status.
- Don't put text in `dim`, or text smaller than 11px in desktop cards or 13px in phone cards.
- Don't embed third-party stat cards or badges. They break the palette and go down.
- Don't claim anything the repos don't show (users, metrics, App Store status).
