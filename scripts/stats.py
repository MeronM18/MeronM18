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


def token() -> str | None:
    if t := os.environ.get("GITHUB_TOKEN"):
        return t
    try:
        return subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return None


def fetch() -> dict:
    """Raw GraphQL user data, live if possible, else the snapshot."""
    try:
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
            headers={"Authorization": f"Bearer {token()}", "User-Agent": USER},
        )
        with urllib.request.urlopen(req, timeout=30) as r:
            user = json.load(r)["data"]["user"]
        user["fetchedAt"] = datetime.now(timezone.utc).isoformat(timespec="minutes")
        SNAPSHOT.write_text(json.dumps(user))
        return user
    except Exception as e:
        print(f"stats.py: GitHub API unavailable ({e}); using snapshot")
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
    return {
        "total": cal["totalContributions"],
        "month": sum(counts[-30:]),
        "streak": streak,
        "busiest": busiest["contributionCount"],
        "busiest_label": f"{MONTHS[bd.month - 1]} {bd.day}",
        "weeks": weeks,
        "week_starts": firsts,
        "langs": top,
        "updated": user.get("fetchedAt", "")[:16].replace("T", " "),
        "calendar": [[d["contributionCount"] for d in w["contributionDays"]] for w in cal["weeks"]],
        "active_days": sum(1 for c in counts if c),
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


def stat(x: float, y: float, value: str, label: str, size: float, label_size: float, accent: bool = False) -> str:
    return (f'<text x="{x}" y="{y}" font-family="MM Display" font-size="{size}" fill="{ACCENT if accent else TEXT}">'
            f'{esc(value)}</text>'
            f'<text x="{x + 2}" y="{y + label_size * 2.4:.1f}" font-family="MM Mono" font-size="{label_size}" '
            f'letter-spacing="2" fill="{MUTED}">{esc(label)}</text>')


def stats_list(s: dict) -> list[tuple[str, str, bool]]:
    return [
        (f"{s['total']:,}", "CONTRIBUTIONS · 12 MO", False),
        (str(s["month"]), "IN THE LAST 30 DAYS", True),
        (str(s["streak"]), "DAY STREAK", False),
        (str(s["busiest"]), f"BUSIEST DAY · {s['busiest_label']}", False),
    ]


def frame(w: int, h: int, s: dict, body: str) -> str:
    items = stats_list(s)
    glyph_text = "".join(v for v, _, _ in items)
    labels = "".join(l for _, l, _ in items) + "".join(MONTHS) + "".join(n.upper() for n, _ in s["langs"])
    labels += "0123456789% · LIVE UPDATED UTC:-PEAK WEEK LANGUAGES WEEKLY CONTRIBUTIONS ON GITHUB LAST 12 MONTHS"
    desc = (f"{s['total']} contributions in the last 12 months, {s['month']} in the last 30 days, a {s['streak']}-day "
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
            f'stop-opacity="0.07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="{w}" height="{h}" rx="28" fill="{INK}"/><rect width="{w}" height="{h}" rx="28" fill="url(#spot)"/>'
            f'{ticks}<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="27.25" fill="none" '
            f'stroke="{LINE}" stroke-width="1.5"/>{body}</svg>')


def live_tag(x: float, y: float, s: dict, size: float, anchor_end: bool = True) -> str:
    text = f"LIVE · UPDATED {s['updated']} UTC" if s["updated"] else "LIVE"
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
    col = (w - 2 * pad) / 4
    for i, (v, l, acc) in enumerate(stats_list(s)):
        body += stat(pad + i * col, 178, v, l, 64, 12, acc)
        if i:
            body += f'<line x1="{pad + i * col - 24:.1f}" y1="124" x2="{pad + i * col - 24:.1f}" y2="210" stroke="{LINE}"/>'
    body += chart(s, pad, 262, w - 2 * pad, 170, 12)
    body += section_label(pad, 516, "LANGUAGES · PUBLIC REPOS", 13)
    body += langs(s, pad, 536, w - 2 * pad, 13, 5)
    return frame(w, h, s, body)


def phone(s: dict) -> str:
    w, pad = 600, 40
    body = section_label(pad, 76, "GITHUB · LIVE", 15)
    for i, (v, l, acc) in enumerate(stats_list(s)):
        r, c = divmod(i, 2)
        body += stat(pad + c * 270, 168 + r * 130, v, l, 68, 13.5, acc)
    body += section_label(pad, 420, "WEEKLY CONTRIBUTIONS", 15)
    body += chart(s, pad, 470, w - 2 * pad, 170, 13)
    body += section_label(pad, 736, "LANGUAGES", 15)
    body += langs(s, pad, 758, w - 2 * pad, 15, 2)
    rows = (len(s["langs"]) + 1) // 2
    ly = 758 + 8 + 15 * 2.4 + rows * 15 * 2.2 + 34
    body += live_tag(pad, ly, s, 14, anchor_end=False)
    return frame(w, int(ly + 50), s, body)


GRID_SHADES = ["#171717", "#2E3237", "#4F5760", "#8A95A1", "#DCE2E8"]


def level(count: int, cuts: list[int]) -> int:
    return 0 if count == 0 else 1 + sum(count > c for c in cuts)


def grid(s: dict, weeks_shown: int, w: int, pad: int, cell: float, gap: float, label: float) -> str:
    """The contribution calendar as a steel heatmap. A scanner light sweeps across it on a loop and
    today's square pulses. Without CSS it is a finished, unlit grid."""
    cal = s["calendar"][-weeks_shown:]
    starts = s["week_starts"][-weeks_shown:]
    nonzero = sorted(c for wk in s["calendar"] for c in wk if c)
    cuts = [nonzero[int(len(nonzero) * q)] for q in (0.25, 0.5, 0.75)] if nonzero else [1, 2, 3]
    step = cell + gap
    top = 132
    sweep = 5.5  # seconds for the light to cross
    cells, scan, months, last = [], [], [], None
    for i, (wk, start) in enumerate(zip(cal, starts)):
        x = pad + i * step
        m = int(start[5:7])
        if m != last and i and i < len(cal) - 1:
            months.append(f'<text x="{x:.1f}" y="{top - 14}" font-family="MM Mono" font-size="{label}" '
                          f'letter-spacing="1.5" fill="{MUTED}">{MONTHS[m - 1]}</text>')
        last = m
        for j, c in enumerate(wk):
            cells.append(f'<rect x="{x:.1f}" y="{top + j * step:.1f}" width="{cell}" height="{cell}" rx="{cell * 0.22:.1f}" '
                         f'fill="{GRID_SHADES[level(c, cuts)]}"/>')
        scan.append(f'<rect class="scan" opacity="0" style="animation-delay:{0.8 + i * sweep / len(cal):.2f}s" '
                    f'x="{x - gap / 2:.1f}" y="{top - gap / 2:.1f}" width="{step:.1f}" height="{7 * step:.1f}" '
                    f'fill="url(#beam)"/>')
    # today = last day with data in the final week
    tx = pad + (len(cal) - 1) * step
    ty = top + (len(cal[-1]) - 1) * step
    legend_y = top + 7 * step + 38
    legend = "".join(
        f'<rect x="{w - pad - (5 - k) * (cell + 5) - 40:.1f}" y="{legend_y - cell + 3:.1f}" width="{cell}" '
        f'height="{cell}" rx="{cell * 0.22:.1f}" fill="{GRID_SHADES[k]}"/>' for k in range(5)
    )
    return f"""
<defs><linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{TEXT}" stop-opacity="0"/><stop offset="0.5" stop-color="{TEXT}" stop-opacity="0.55"/>
  <stop offset="1" stop-color="{TEXT}" stop-opacity="0"/></linearGradient></defs>
{"".join(months)}{"".join(cells)}<g style="mix-blend-mode:screen">{"".join(scan)}</g>
<rect class="pulse" x="{tx - 3:.1f}" y="{ty - 3:.1f}" width="{cell + 6}" height="{cell + 6}" rx="{cell * 0.35:.1f}"
  fill="none" stroke="{SIGNAL}" stroke-width="1.5"/>
<text x="{pad}" y="{legend_y}" font-family="MM Mono" font-size="{label}" letter-spacing="1.8" fill="{MUTED}">{s["active_days"]} ACTIVE DAYS{" · TODAY OUTLINED" if w >= 800 else ""}</text>
<text x="{w - pad - 5 * (cell + 5) - 52:.1f}" y="{legend_y}" text-anchor="end" font-family="MM Mono" font-size="{label}" letter-spacing="1.8" fill="{MUTED}">LESS</text>
{legend}
<text x="{w - pad}" y="{legend_y}" text-anchor="end" font-family="MM Mono" font-size="{label}" letter-spacing="1.8" fill="{MUTED}">MORE</text>"""


GRID_MOTION = (
    "@keyframes scan{0%,100%{opacity:0}3%{opacity:1}9%{opacity:0}}"
    ".scan{animation:scan 7s ease-in-out infinite}"
    "@keyframes pulse{0%,100%{opacity:1}50%{opacity:.25}}.pulse{animation:pulse 1.8s ease-in-out infinite}"
    "@media (prefers-reduced-motion:reduce){.scan,.pulse{animation:none}}"
)


def grid_card(s: dict, w: int, weeks_shown: int, pad: int, cell: float, gap: float, label: float, title: str) -> str:
    body = grid(s, weeks_shown, w, pad, cell, gap, label)
    h = int(132 + 7 * (cell + gap) + 38 + 52)
    text = (title + "".join(MONTHS) + "ACTIVE DAYS TODAY OUTLINED LESS MORE0123456789·")
    desc = f"Contribution calendar for the {title.lower()}: {s['active_days']} active days in the last 12 months."
    ticks = "".join(
        f'<path d="M{x} {y + dy * 16}V{y}H{x + dx * 16}" fill="none" stroke="#3A3A3A" stroke-width="1.5"/>'
        for x, y, dx, dy in ((24, 24, 1, 1), (w - 24, 24, -1, 1))
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" '
            f'aria-labelledby="t d"><title id="t">Contribution grid</title><desc id="d">{esc(desc)}</desc>'
            f'<style>{font_css(mono=text, monobold=text)}{GRID_MOTION}</style>'
            f'<defs><radialGradient id="spot" cx="0.9" cy="-0.2" r="0.9"><stop offset="0" stop-color="#fff" '
            f'stop-opacity="0.06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient></defs>'
            f'<rect width="{w}" height="{h}" rx="28" fill="{INK}"/><rect width="{w}" height="{h}" rx="28" fill="url(#spot)"/>'
            f'{ticks}<rect x="0.75" y="0.75" width="{w - 1.5}" height="{h - 1.5}" rx="27.25" fill="none" '
            f'stroke="{LINE}" stroke-width="1.5"/>'
            f'<text x="{pad}" y="76" font-family="MM Mono Bold" font-size="{label + 1}" letter-spacing="3" '
            f'fill="{MUTED}">{title}</text>{body}</svg>')


def main(argv: list[str] | None = None) -> None:
    argv = argv or []
    out = Path(argv[argv.index("--out") + 1]) if "--out" in argv else ASSETS
    s = summarize(fetch())
    write(out / "stats.svg", desktop(s))
    write(out / "stats-phone.svg", phone(s))
    weeks = len(s["calendar"])
    step = (1200 - 2 * 64) / weeks
    write(out / "grid.svg", grid_card(s, 1200, weeks, 64, round(step * 0.8, 1), round(step * 0.2, 1), 12,
                                      "CONTRIBUTION GRID · LAST 12 MONTHS"))
    write(out / "grid-phone.svg", grid_card(s, 600, 26, 40, 15.6, 4.2, 13, "CONTRIBUTIONS · LAST 6 MONTHS"))


if __name__ == "__main__":
    main(sys.argv[1:])
