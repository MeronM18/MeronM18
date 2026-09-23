"""Download the three typefaces and write the static fonts the generators use.

    .venv/bin/python scripts/fetch_fonts.py

- Imperial Script (OFL): script.ttf, the hero name. Committed.
- Bodoni Moda (OFL): display.ttf, serif.ttf. Committed.
- IBM Plex Mono (OFL): mono.ttf, monobold.ttf. Committed.
- Switzer (ITF Free Font License): body.ttf, bodybold.ttf. Git-ignored, because the
  license forbids redistributing the font files. SVGs never embed it as a font:
  brand.outline() turns Switzer text into paths, and cards are rasterized.
"""

from __future__ import annotations

import io
import urllib.request
import zipfile

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

from brand import FONTS

GOOGLE = "https://raw.githubusercontent.com/google/fonts/main/ofl"
SWITZER = "https://api.fontshare.com/v2/fonts/download/switzer"


def get(url: str) -> bytes:
    with urllib.request.urlopen(url) as r:
        return r.read()


def bodoni(src: str, out: str, wght: int, opsz: int) -> None:
    font = TTFont(io.BytesIO(get(f"{GOOGLE}/bodonimoda/{src}")))
    static = instantiateVariableFont(font, {"wght": wght, "opsz": opsz})
    static.save(FONTS / out)
    print(f"wrote {out}")


def main() -> None:
    FONTS.mkdir(exist_ok=True)
    bodoni("BodoniModa%5Bopsz,wght%5D.ttf", "display.ttf", 500, 96)
    bodoni("BodoniModa-Italic%5Bopsz,wght%5D.ttf", "serif.ttf", 400, 96)
    (FONTS / "OFL-BodoniModa.txt").write_bytes(get(f"{GOOGLE}/bodonimoda/OFL.txt"))

    (FONTS / "script.ttf").write_bytes(get(f"{GOOGLE}/imperialscript/ImperialScript-Regular.ttf"))
    (FONTS / "OFL-ImperialScript.txt").write_bytes(get(f"{GOOGLE}/imperialscript/OFL.txt"))
    print("wrote script.ttf")

    for weight, out in (("Regular", "mono.ttf"), ("SemiBold", "monobold.ttf")):
        (FONTS / out).write_bytes(get(f"{GOOGLE}/ibmplexmono/IBMPlexMono-{weight}.ttf"))
        print(f"wrote {out}")
    (FONTS / "OFL-IBMPlexMono.txt").write_bytes(get(f"{GOOGLE}/ibmplexmono/OFL.txt"))

    with zipfile.ZipFile(io.BytesIO(get(SWITZER))) as z:
        for weight, out in (("Regular", "body.ttf"), ("Medium", "bodybold.ttf")):
            name = next(n for n in z.namelist() if n.endswith(f"/Switzer-{weight}.ttf"))
            (FONTS / out).write_bytes(z.read(name))
            print(f"wrote {out}")


if __name__ == "__main__":
    main()
