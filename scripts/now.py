"""What I'm building right now, read from GitHub: my most recently pushed repos.

    .venv/bin/python scripts/now.py        # prints e.g. ['KYUU CAFE', 'MATTI STUDIO']

Rules, so the hero never surfaces something I'm keeping quiet:
- Private repos appear only under a name in SHOWN, i.e. projects the README already features.
  Every other private repo stays invisible, so none of them needs to be named here.
- HIDDEN lists public repos that must never appear.
  Seeing them at all needs PROFILE_TOKEN (read-only); without it only public repos are visible.
- Public repos appear by name, unless they're forks, archived, templates or this profile repo.
"""

from __future__ import annotations

import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone

USER = "MeronM18"
WINDOW = timedelta(days=21)  # a repo counts as "now" if pushed within this window
HIDDEN = {"dummypeptides"}
SHOWN = {  # repo name (lowercase) -> name shown in the hero
    "kyuu-platform": "KYUU CAFE",
    "kyuu-cafe-site": "KYUU CAFE",
    "matti-studio": "MATTI STUDIO",
    "ledger.m": "LEDGER.M",
    "cosmo": "COSMO",
    "staydue": "STAYDUE",
    "easymail": "EASYMAIL",
}
FALLBACK = ["KYUU CAFE", "MATTI STUDIO"]


def repos() -> list[dict]:
    """With PROFILE_TOKEN: every repo I own (incl. private). Otherwise: my public repos."""
    if token := os.environ.get("PROFILE_TOKEN"):
        url = "https://api.github.com/user/repos?affiliation=owner&sort=pushed&direction=desc&per_page=50"
    else:
        token = os.environ.get("GITHUB_TOKEN")
        url = f"https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&direction=desc&per_page=50"
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": USER})
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def label(repo: dict) -> str | None:
    name = repo["name"].lower()
    if name in HIDDEN or name == USER.lower():
        return None
    if repo["fork"] or repo["archived"] or repo.get("is_template"):
        return None
    if repo["private"]:
        return SHOWN.get(name)
    return SHOWN.get(name, repo["name"].upper())


def now_building(limit: int = 2) -> list[str]:
    """Up to `limit` names, most recently pushed first; FALLBACK if the API fails or nothing is recent."""
    try:
        data = repos()
    except Exception as e:  # never fail the build over the API
        print(f"now.py: GitHub API unavailable ({e}); using fallback")
        return FALLBACK
    cutoff = datetime.now(timezone.utc) - WINDOW
    names: list[str] = []
    for r in data:
        shown = label(r)
        if shown and shown not in names and datetime.fromisoformat(r["pushed_at"].replace("Z", "+00:00")) >= cutoff:
            names.append(shown)
    return names[:limit] or FALLBACK


if __name__ == "__main__":
    print(now_building())
