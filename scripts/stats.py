"""Live GitHub stats panel: headline numbers, a weekly activity chart that draws itself, and languages.

    .venv/bin/python scripts/stats.py                 # live data (needs GITHUB_TOKEN or `gh auth token`)
    .venv/bin/python scripts/stats.py --out dist      # where the workflow writes it

Data comes from the GraphQL API: the contribution calendar (what the profile's own
graph shows) and language bytes across my public repos. If the API is unreachable,
the last good pull in scripts/stats-snapshot.json is used, so a build never fails.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path

from brand import (ACCENT, ASSETS, INK, LINE, MUTED, SCRIPTS, SIGNAL, SOFT, TEXT, esc, font_css, measure,
                   write)

USER = "MeronM18"
SNAPSHOT = SCRIPTS / "stats-snapshot.json"
QUERY = """query($login:String!){user(login:$login){
  contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}
  repositories(privacy:PUBLIC,ownerAffiliations:OWNER,isFork:false,first:100){nodes{
    languages(first:8,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}"""
MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
SHADES = [TEXT, ACCENT, "#7C8794", "#56606B", "#3A424B"]  # languages, largest first


EASTERN = ZoneInfo("America/New_York")

# Whose commits count as mine for "commits today". GitHub's own graph misses a lot of real work:
# it only counts default branches, and only emails linked to the account. This counts every
# branch, and these identities: my account, my Mac's local git email (not linked on GitHub),
# and commits my Claude sessions make in my repos. Bots and other people's commits never count.
MY_LOGINS = {"MeronM18"}
MY_EMAILS = {"meron@merons-macbook-pro.local", "meronmatti123@gmail.com"}
AGENT_EMAILS = {"noreply@anthropic.com"}

REPOS_QUERY = """query($login:String!){user(login:$login){id repositories(first:40,orderBy:{field:PUSHED_AT,direction:DESC},
  ownerAffiliations:[OWNER,COLLABORATOR,ORGANIZATION_MEMBER]){nodes{name owner{login} pushedAt isPrivate}}}}"""
BRANCHES = """refs(refPrefix:"refs/heads/",first:100){nodes{target{... on Commit{
  history(since:$since,first:100){nodes{oid author{email user{login}}}}}}}}"""


def tokens() -> list[tuple[str, str]]:
    """(name, token) to try in order: PROFILE_TOKEN (read-only, can see private repos), then the workflow's
    GITHUB_TOKEN (public repos only), then locally the gh CLI's token."""
    out = [(n, os.environ[n]) for n in ("PROFILE_TOKEN", "GITHUB_TOKEN") if os.environ.get(n)]
    if not out:
        try:
            out.append(("gh", subprocess.run(["gh", "auth", "token"], capture_output=True, text=True,
                                             check=True).stdout.strip()))
        except Exception:
            pass
    return out


_TOKEN: str | None = None


def graphql(query: str, variables: dict) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"Bearer {_TOKEN}", "User-Agent": USER},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors"):
        raise RuntimeError(body["errors"][0].get("message"))
    return body["data"]


def is_mine(author: dict) -> bool:
    login = ((author or {}).get("user") or {}).get("login") or ""
    email = ((author or {}).get("email") or "").lower()
    if login.endswith("[bot]") or "[bot]" in email:
        return False
    return login in MY_LOGINS or email in MY_EMAILS or email in AGENT_EMAILS


def commits_today() -> dict:
    """Distinct commits of mine since midnight Eastern, across every branch of every repo I can see."""
    now = datetime.now(EASTERN)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    repos = graphql(REPOS_QUERY, {"login": USER})["user"]["repositories"]["nodes"]
    fresh = [r for r in repos
             if datetime.fromisoformat(r["pushedAt"].replace("Z", "+00:00")) >= start]
    # Counts only: this repo's Actions logs are public, so private repo names are never printed.
    print(f"stats.py: {len(repos)} repos visible ({sum(r['isPrivate'] for r in repos)} private), "
          f"{len(fresh)} pushed today")
    oids: set[str] = set()
    if fresh:
        parts = "".join(f'r{i}:repository(owner:"{r["owner"]["login"]}",name:"{r["name"]}"){{{BRANCHES}}}'
                        for i, r in enumerate(fresh))
        data = graphql(f"query($since:GitTimestamp!){{{parts}}}", {"since": start.isoformat()})
        for repo in data.values():
            for ref in (repo or {}).get("refs", {}).get("nodes", []):
                for c in ((ref.get("target") or {}).get("history") or {}).get("nodes", []):
                    if is_mine(c["author"]):
                        oids.add(c["oid"])
    print(f"stats.py: {len(oids)} commits today (Eastern)")
    return {"count": len(oids), "date": start.date().isoformat()}


def fetch() -> dict:
    """Raw GraphQL user data plus today's commit count, live if possible, else the snapshot.
    A token that fails (expired, revoked) falls through to the next one before the snapshot."""
    global _TOKEN
    for name, _TOKEN in tokens():
        try:
            user = graphql(QUERY, {"login": USER})["user"]
            user["commitsToday"] = commits_today()
            user["fetchedAt"] = datetime.now(timezone.utc).isoformat(timespec="minutes")
            SNAPSHOT.write_text(json.dumps(user))
            print(f"stats.py: live data via {name}")
            return user
        except Exception as e:
            print(f"stats.py: {name} failed ({e})")
    print("stats.py: using snapshot")
    return json.loads(SNAPSHOT.read_text())


def summarize(user: dict) -> dict:
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in cal["weeks"] for d in w["contributionDays"]]
    counts = [d["contributionCount"] for d in days]
    streak = 0
    for i, c in enumerate(reversed(counts)):
        if c:
            streak += 1
        elif i:  # today may still be empty
            break
    busiest = max(days, key=lambda d: d["contributionCount"])
    weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]
    firsts = [w["contributionDays"][0]["date"] for w in cal["weeks"]]
    langs = Counter()
    for repo in user["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]
    total = sum(langs.values()) or 1
    top = [(n, v / total) for n, v in langs.most_common(4)]
    rest = 1 - sum(v for _, v in top)
    if rest > 0.005:
        top.append(("Other", rest))
    bd = date.fromisoformat(busiest["date"])
    today = user.get("commitsToday") or {"count": counts[-1], "date": days[-1]["date"]}
    td = date.fromisoformat(today["date"])
    fetched = user.get("fetchedAt")
    updated = ""
    if fetched:
        et = datetime.fromisoformat(fetched).astimezone(EASTERN)
        updated = f"{MONTHS[et.month - 1]} {et.day} · {et.strftime('%-I:%M %p')} ET"
    return {
        "total": cal["totalContributions"],
        "month": sum(counts[-30:]),
        "streak": streak,
        "busiest": busiest["contributionCount"],
        "busiest_label": f"{MONTHS[bd.month - 1]} {bd.day}",
        "today": today["count"],
        "today_label": f"{MONTHS[td.month - 1]} {td.day}",
        "weeks": weeks,
        "week_starts": firsts,
        "langs": top,
        "updated": updated,
    }


MOTION = (
    "@keyframes draw{from{stroke-dashoffset:1}to{stroke-dashoffset:0}}"
    ".line{stroke-dasharray:1;animation:draw 2.6s cubic-bezier(.5,0,.2,1) .4s both}"
    "@keyframes fade{from{opacity:0}to{opacity:1}}"
    ".area{animation:fade 1.4s ease 1.6s both}.peak{animation:fade .6s ease 2.8s both}"
    "@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"
    ".seg{transform-box:fill-box;transform-origin:left;animation:grow 1s cubic-bezier(.6,0,.2,1) both}"
    "@keyframes pulse{0%,100%{opacity:.9}50%{opacity:.3}}.pulse{animation:pulse 2.4s ease-in-out infinite}"
    "@media (prefers-reduced-motion:reduce){.line,.area,.peak,.seg,.pulse{animation:none}}"
)


def chart(s: dict, x: float, y: float, w: float, h: float, label_size: float) -> str:
    """Weekly contributions as a smoothed steel line over a faint area, with month ticks and the peak marked."""
    weeks = s["weeks"]
    top = max(weeks) or 1
    pts = [(x + i * w / (len(weeks) - 1), y + h - (v / top) * h) for i, v in enumerate(weeks)]

    def smooth(points):
        d = f"M{points[0][0]:.1f} {points[0][1]:.1f}"
        for (x0, y0), (x1, y1) in zip(points, points[1:]):
            mx = (x0 + x1) / 2
            d += f" C{mx:.1f} {y0:.1f} {mx:.1f} {y1:.1f} {x1:.1f} {y1:.1f}"
        return d

    line = smooth(pts)
    area = line + f" L{pts[-1][0]:.1f} {y + h} L{pts[0][0]:.1f} {y + h} Z"
    grid = "".join(
        f'<line x1="{x}" y1="{y + h * f:.1f}" x2="{x + w}" y2="{y + h * f:.1f}" stroke="{LINE}" '
        f'stroke-dasharray="2 6"/>' for f in (0, 0.5, 1)
    )
    ticks, last = "", None
    for i, start in enumerate(s["week_starts"]):
        m = int(start[5:7])
        if m != last and i:
            tx = pts[i][0]
            ticks += (f'<text x="{tx:.1f}" y="{y + h + label_size * 2.1:.1f}" text-anchor="middle" font-family="MM Mono" '
                      f'font-size="{label_size}" letter-spacing="1.5" fill="{MUTED}">{MONTHS[m - 1]}</text>')
        last = m
    pi = weeks.index(max(weeks))
    px, py = pts[pi]
    peak_label = f"PEAK WEEK · {max(weeks)}"
    anchor = "end" if pi > len(weeks) * 0.7 else "start"
    lx = px - 14 if anchor == "end" else px + 14
    return f"""
<defs><linearGradient id="fill" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{ACCENT}" stop-opacity="0.28"/><stop offset="1" stop-color="{ACCENT}" stop-opacity="0"/>
</linearGradient></defs>
{grid}
<path class="area" d="{area}" fill="url(#fill)"/>
<path class="line" pathLength="1" d="{line}" fill="none" stroke="{TEXT}" stroke-width="2" stroke-linejoin="round"/>
<g class="peak">
  <line x1="{px:.1f}" y1="{py:.1f}" x2="{px:.1f}" y2="{y + h}" stroke="{ACCENT}" stroke-dasharray="2 4"/>
  <circle cx="{px:.1f}" cy="{py:.1f}" r="9" fill="{SIGNAL}" opacity="0.18" class="pulse"/>
  <circle cx="{px:.1f}" cy="{py:.1f}" r="4" fill="{SIGNAL}"/>
  <text x="{lx:.1f}" y="{py + 5:.1f}" text-anchor="{anchor}" font-family="MM Mono Bold" font-size="{label_size}"
    letter-spacing="1.8" fill="{TEXT}">{peak_label}</text>
</g>
{ticks}"""


def langs(s: dict, x: float, y: float, w: float, size: float, per_row: int) -> str:
    out, cx = [], x
    for i, (name, share) in enumerate(s["langs"]):
        seg = max(w * share - 3, 2)
        out.append(f'<rect class="seg" style="animation-delay:{1.2 + i * 0.15:.2f}s" x="{cx:.1f}" y="{y}" '
                   f'width="{seg:.1f}" height="8" rx="2" fill="{SHADES[i]}"/>')
        cx += w * share
    lx, ly = x, y + 8 + size * 2.4
    col = w / per_row
    for i, (name, share) in enumerate(s["langs"]):
        r, c = divmod(i, per_row)
        tx, ty = lx + c * col, ly + r * size * 2.2
        out.append(f'<rect x="{tx}" y="{ty - size * 0.72:.1f}" width="{size * 0.72:.1f}" height="{size * 0.72:.1f}" '
                   f'rx="2" fill="{SHADES[i]}"/>'
                   f'<text x="{tx + size * 1.3:.1f}" y="{ty}" font-family="MM Mono" font-size="{size}" letter-spacing="1.4" '
                   f'fill="{SOFT}">{esc(name.upper())} <tspan fill="{MUTED}">{share * 100:.0f}%</tspan></text>')
    return "".join(out)


def stat(x: float, y: float, value: str, label: str, size: float, label_size: float, kind: str = "",
         tracking: float = 2) -> str:
    """One headline number. kind "accent" is steel; "hero" (today) glows bone-white with a live dot."""
    if kind == "hero":
        dot_y = y + label_size * 2.4 - label_size * 0.36
        return (f'<text x="{x}" y="{y}" font-family="MM Display" font-size="{size}" fill="{SIGNAL}" '
                f'filter="url(#glow)">{esc(value)}</text>'
                f'<circle cx="{x + 5}" cy="{dot_y:.1f}" r="{label_size * 0.75:.1f}" fill="{SIGNAL}" opacity="0.18" '
                f'class="pulse"/><circle cx="{x + 5}" cy="{dot_y:.1f}" r="{label_size * 0.28:.1f}" fill="{SIGNAL}"/>'
                f'<text x="{x + 18}" y="{y + label_size * 2.4:.1f}" font-family="MM Mono Bold" font-size="{label_size}" '
                f'letter-spacing="{tracking}" fill="{TEXT}">{esc(label)}</text>')
    return (f'<text x="{x}" y="{y}" font-family="MM Display" font-size="{size}" '
            f'fill="{ACCENT if kind == "accent" else TEXT}">{esc(value)}</text>'
            f'<text x="{x + 2}" y="{y + label_size * 2.4:.1f}" font-family="MM Mono" font-size="{label_size}" '
            f'letter-spacing="{tracking}" fill="{MUTED}">{esc(label)}</text>')


def hero_panel(x: float, y: float, w: float, h: float) -> str:
    """A faint raised plate behind today's number so it reads as the live one."""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="16" fill="#fff" fill-opacity="0.035" '
            f'stroke="{ACCENT}" stroke-opacity="0.35" stroke-width="1.2"/>')


def stats_list(s: dict) -> list[tuple[str, str, str]]:
    return [
        (f"{s['total']:,}", "CONTRIBUTIONS · 12 MO", ""),
        (str(s["month"]), "IN THE LAST 30 DAYS", "accent"),
        (str(s["streak"]), "DAY STREAK", ""),
        (str(s["busiest"]), f"BUSIEST DAY · {s['busiest_label']}", ""),
        (str(s["today"]), f"COMMITS TODAY · {s['today_label']}", "hero"),
    ]


def frame(w: int, h: int, s: dict, body: str) -> str:
    items = stats_list(s)
    glyph_text = "".join(v for v, _, _ in items)
    labels = "".join(l for _, l, _ in items) + "".join(MONTHS) + "".join(n.upper() for n, _ in s["langs"])
    labels += "0123456789% · LIVE UPDATED UTC:-PEAK WEEK LANGUAGES WEEKLY CONTRIBUTIONS ON GITHUB LAST 12 MONTHS TODAY COMMITS ET AM PM EVERY BRANCH REPO"
    desc = (f"{s['today']} commits today (Eastern time, every branch), {s['total']} contributions in the last 12 months, {s['month']} in the last 30 days, a {s['streak']}-day "
            f"streak, busiest day {s['busiest']} on {s['busiest_label'].title()}. Languages: "
            + ", ".join(f"{n} {v * 100:.0f}%" for n, v in s["langs"]) + ".")
    ticks = "".join(
        f'<path d="M{x} {y + dy * 16}V{y}H{x + dx * 16}" fill="none" stroke="#3A3A3A" stroke-width="1.5"/>'
        for x, y, dx, dy in ((24, 24, 1, 1), (w - 24, 24, -1, 1))
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="t d"><title id="t">GitHub activity</title><desc id="d">{esc(desc)}</desc>'
            f'<style>{font_css(display=glyph_text, mono=labels, monobold=labels)}{MOTION}</style>'
            f'<defs><radialGradient id="spot" cx="0.1" cy="-0.2" r="0.9"><stop offset="0" stop-color="#fff" '
            f'stop-opacity="0.07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            f'<filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="7" '
            f'result="b"/><feColorMatrix in="b" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 .55 0" result="g"/>'
            f'<feMerge><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>'
            f'<rect width="{w}" height="{h}" rx="28" fill="{INK}"/><rect width="{w}" height="{h}" rx="28" fill="url(#spot)"/>'
            f'{ticks}<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="27.25" fill="none" '
            f'stroke="{LINE}" stroke-width="1.5"/>{body}</svg>')


def live_tag(x: float, y: float, s: dict, size: float, anchor_end: bool = True) -> str:
    text = f"LIVE · UPDATED {s['updated']}" if s["updated"] else "LIVE"
    tw = measure(text, "mono", size, 1.8)
    x0 = x - tw - 20 if anchor_end else x
    return (f'<circle cx="{x0 + 4}" cy="{y - size * 0.36:.1f}" r="{size * 0.8:.1f}" fill="{SIGNAL}" opacity="0.16" '
            f'class="pulse"/><circle cx="{x0 + 4}" cy="{y - size * 0.36:.1f}" r="{size * 0.3:.1f}" fill="{SIGNAL}"/>'
            f'<text x="{x0 + 20}" y="{y}" font-family="MM Mono" font-size="{size}" letter-spacing="1.8" '
            f'fill="{MUTED}">{esc(text)}</text>')


def section_label(x: float, y: float, text: str, size: float) -> str:
    return (f'<text x="{x}" y="{y}" font-family="MM Mono Bold" font-size="{size}" letter-spacing="3" '
            f'fill="{MUTED}">{text}</text>')


def desktop(s: dict) -> str:
    w, h, pad = 1200, 620, 64
    body = section_label(pad, 84, "ON GITHUB · LAST 12 MONTHS", 13) + live_tag(w - pad, 84, s, 13)
    items = stats_list(s)
    col = (w - 2 * pad) / len(items)
    body += hero_panel(pad + (len(items) - 1) * col - 22, 112, col + 22 + 10, 116)
    for i, (v, l, kind) in enumerate(items):
        body += stat(pad + i * col, 178, v, l, 64, 12, kind, tracking=1.4)
        if 0 < i < len(items) - 1:
            body += f'<line x1="{pad + i * col - 22:.1f}" y1="124" x2="{pad + i * col - 22:.1f}" y2="210" stroke="{LINE}"/>'
    body += chart(s, pad, 262, w - 2 * pad, 170, 12)
    body += section_label(pad, 516, "LANGUAGES · PUBLIC REPOS", 13)
    body += langs(s, pad, 536, w - 2 * pad, 13, 5)
    return frame(w, h, s, body)


def phone(s: dict) -> str:
    w, pad = 600, 40
    body = section_label(pad, 76, "GITHUB · LIVE", 15)
    *rest, today = stats_list(s)
    for i, (v, l, kind) in enumerate(rest):
        r, c = divmod(i, 2)
        body += stat(pad + c * 270, 168 + r * 130, v, l, 68, 13.5, kind)
    body += hero_panel(pad - 16, 362, w - 2 * pad + 32, 132)
    body += stat(pad, 444, *today[:2], 68, 13.5, "hero")
    body += (f'<text x="{w - pad}" y="{444 + 13.5 * 2.4:.1f}" text-anchor="end" font-family="MM Mono" font-size="13" '
             f'letter-spacing="1.6" fill="{MUTED}">EVERY BRANCH · EVERY REPO</text>')
    dy = 150
    body += section_label(pad, 420 + dy, "WEEKLY CONTRIBUTIONS", 15)
    body += chart(s, pad, 470 + dy, w - 2 * pad, 170, 13)
    body += section_label(pad, 736 + dy, "LANGUAGES", 15)
    body += langs(s, pad, 758 + dy, w - 2 * pad, 15, 2)
    rows = (len(s["langs"]) + 1) // 2
    ly = 758 + dy + 8 + 15 * 2.4 + rows * 15 * 2.2 + 34
    body += live_tag(pad, ly, s, 14, anchor_end=False)
    return frame(w, int(ly + 50), s, body)


def main(argv: list[str] | None = None) -> None:
    argv = argv or []
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else ASSETS
    s = summarize(fetch())
    write(out / "stats.svg", desktop(s))
    write(out / "stats-phone.svg", phone(s))


if __name__ == "__main__":
    main(sys.argv[1:])
