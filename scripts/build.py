"""Rebuild every generated asset (see DESIGN.md).

    .venv/bin/python scripts/build.py
"""

import cards  # run fetch_fonts.py first on a fresh clone
import footer
import header
import sections
import stack

for module in (header, sections, cards, stack, footer):
    module.main()
