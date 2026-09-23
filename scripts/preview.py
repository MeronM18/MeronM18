"""Render the README and every asset to PNG for review (see DESIGN.md).

    .venv/bin/python scripts/preview.py

Writes to .preview/ (git-ignored):
  gallery-{light,dark}.png   every asset on GitHub's page color, as authored,
                             frozen (no CSS) and on its alternate animation frame
  readme-{desktop,phone}-{light,dark}-N.png
                             the README rendered by GitHub's markdown API, in slices

Needs Google Chrome and the GitHub CLI (`gh`) for the markdown API.
"""

from __future__ import annotations

import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
OUT = ROOT / ".preview"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PAGE = {"light": "#ffffff", "dark": "#0d1117"}
# Pins every animated class (see DESIGN.md, Motion) to its other extreme.
ALT_FRAME_CSS = ".tw,.pulse{opacity:.3!important;animation:none!important}.orbit{transform:rotate(180deg)!important}"
CSS = "https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown-{}.css"
SLICE = {"desktop": 1400, "phone": 1600}


def shoot(html: pathlib.Path, png: pathlib.Path, width: int, height: int, dark: bool) -> None:
    args = [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
            f"--window-size={width},{height}", f"--screenshot={png}", "--virtual-time-budget=1500"]
    if dark:
        args.append("--force-dark-mode")
    subprocess.run(args + [html.as_uri()], check=True, capture_output=True)
    print(f"wrote {png.relative_to(ROOT)}")


def frames(svg: pathlib.Path) -> list[tuple[str, pathlib.Path]]:
    """The asset as authored, plus frozen and alternate-frame copies if it is animated."""
    src = svg.read_text()
    if "<style>" not in src:
        return [("static", svg)]
    frozen = OUT / "frames" / f"{svg.stem}-frozen.svg"
    alt = OUT / "frames" / f"{svg.stem}-alt.svg"
    frozen.write_text(re.sub(r"<style>.*?</style>", "", src, flags=re.S))
    alt.write_text(src.replace("</style>", ALT_FRAME_CSS + "</style>", 1))
    return [("animated", svg), ("frozen", frozen), ("alt frame", alt)]


def gallery(theme: str) -> None:
    other = "light" if theme == "dark" else "dark"
    items = []
    for svg in sorted(ASSETS.rglob("*.svg")):
        if f"-{other}" in svg.stem:
            continue
        cells = "".join(
            f'<figure><img src="{path.as_uri()}"><figcaption>{label}</figcaption></figure>'
            for label, path in frames(svg)
        )
        items.append(f"<section><h2>{svg.name}</h2><div class=row>{cells}</div></section>")
    color = "#e6edf3" if theme == "dark" else "#1f2328"
    html = OUT / f"gallery-{theme}.html"
    html.write_text(
        f"<!doctype html><meta charset=utf-8><style>body{{background:{PAGE[theme]};color:{color};"
        "font:12px -apple-system,sans-serif;margin:24px}.row{display:flex;gap:16px;align-items:flex-start}"
        "figure{margin:0}img{max-width:420px;display:block}h2{font-size:12px;margin:18px 0 6px}"
        "figcaption{opacity:.6;margin-top:4px}</style>" + "".join(items)
    )
    shoot(html, OUT / f"gallery-{theme}.png", 1340, 5200, theme == "dark")


def readme() -> None:
    body = subprocess.run(
        ["gh", "api", "-X", "POST", "/markdown", "-F", f"text=@{ROOT / 'README.md'}", "-f", "mode=gfm"],
        check=True, capture_output=True, text=True,
    ).stdout
    body = body.replace('="./assets/', f'="{ASSETS.as_uri()}/')
    for theme in PAGE:
        # Headless Chrome won't open a window narrower than ~500px, so the phone
        # page is a 390px column inside a 500px window (still under the 600px
        # breakpoint that picks the phone assets).
        for device, width, column in (("desktop", 1012, 1012), ("phone", 500, 390)):
            pad = 32 if device == "desktop" else 16
            for n in range(6):
                html = OUT / f"readme-{device}-{theme}-{n}.html"
                html.write_text(
                    f'<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width">'
                    f'<link rel=stylesheet href="{CSS.format(theme)}">'
                    f"<style>body{{margin:0;background:{PAGE[theme]}}}.markdown-body{{padding:{pad}px;"
                    f"box-sizing:border-box;width:{column}px;"
                    f"margin-top:-{n * SLICE[device]}px}}</style>"
                    f'<article class="markdown-body">{body}</article>'
                )
                shoot(html, OUT / f"readme-{device}-{theme}-{n}.png", width, SLICE[device], theme == "dark")


def main() -> None:
    (OUT / "frames").mkdir(parents=True, exist_ok=True)
    for theme in PAGE:
        gallery(theme)
    readme()


if __name__ == "__main__":
    main()
