"""Rebuild every generated asset (see DESIGN.md).

    .venv/bin/python scripts/build.py
"""

import cards  # run fetch_fonts.py first on a fresh clone
import footer
import header
import sections
import stack
import stats

header.main(["--live"])  # falls back to a fixed list offline
stats.main()  # falls back to scripts/stats-snapshot.json offline
for module in (sections, cards, stack, footer):
    module.main()
