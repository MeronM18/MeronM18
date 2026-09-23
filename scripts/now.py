"""What I'm building right now, read from GitHub: my most recently pushed public repos.

    .venv/bin/python scripts/now.py        # prints e.g. ['LEDGER.M', 'EASYMAIL']

Only public, non-fork, non-archived, non-template repos count, and never this
profile repo. Private repos never appear: the public repos endpoint can't see them.
"""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

USER = "MeronM18"
WINDOW = timedelta(days=21)  # a repo counts as "now" if pushed within this window
FALLBACK = ["EASYMAIL", "STAYDUE"]


def repos() -> list[dict]:
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&direction=desc&per_page=30",
        headers={"Accept": "application/vnd.github+json", "User-Agent": USER},
    )
    if token := os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def now_building(limit: int = 2) -> list[str]:
    """Up to `limit` repo names, most recently pushed first; FALLBACK if the API fails or nothing is recent."""
    try:
        data = repos()
    except Exception as e:  # never fail the build over the API
        print(f"now.py: GitHub API unavailable ({e}); using fallback")
        return FALLBACK
    cutoff = datetime.now(timezone.utc) - WINDOW
    names = [
        r["name"].upper()
        for r in data
        if not (r["fork"] or r["archived"] or r.get("is_template") or r["private"])
        and r["name"].lower() != USER.lower()
        and datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00")) >= cutoff
    ]
    return names[:limit] or FALLBACK


if __name__ == "__main__":
    print(now_building())
