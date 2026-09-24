"""Project cards: HTML/CSS rendered to WebP by headless Chrome.

Each card renders twice from the same HTML: a 1200px desktop layout and a 480px
phone layout (picked by a CSS media query), both at high DPI.
"""

from __future__ import annotations

from brand import (ASSETS, INK, LINE, MUTED, PANEL, RAISED, SHOTS, SOFT, TEXT, ACCENT, ACCENT_DIM, SIGNAL,
                   esc, font_files_css, render, render_anim)

DESKTOP_W = 1200
PHONE_W = 500


def starfield(seed: int, n: int = 0) -> str:
    """Faint registration ticks in the corners: a dossier, not a sky."""
    return '<div class="ticks"><i></i><i></i></div>'


CSS = f"""
{font_files_css()}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:transparent;width:100%;height:100%}}
.card{{position:relative;width:100vw;height:100vh;border-radius:28px;overflow:hidden;color:{TEXT};
  font-family:'MM Body';border:1.5px solid {LINE};
  background:radial-gradient(900px 560px at 8% -20%,rgba(255,255,255,.075),transparent 62%),
             radial-gradient(800px 520px at 105% 115%,rgba(169,180,192,.07),transparent 60%),{INK}}}
.ticks i{{position:absolute;width:14px;height:14px;border-color:#3a3a3a;border-style:solid;border-width:0}}
.ticks i:nth-child(1){{left:22px;top:22px;border-left-width:1.5px;border-top-width:1.5px}}
.ticks i:nth-child(2){{right:22px;top:22px;border-right-width:1.5px;border-top-width:1.5px}}
.ticks i:nth-child(3){{left:22px;bottom:22px;border-left-width:1.5px;border-bottom-width:1.5px}}
.ticks i:nth-child(4){{right:22px;bottom:22px;border-right-width:1.5px;border-bottom-width:1.5px}}
.grain{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.014) 1px,transparent 1px);
  background-size:100% 44px;pointer-events:none}}
.eyebrow{{font-family:'MM Mono Bold';font-size:15px;letter-spacing:.24em;text-transform:uppercase;color:{ACCENT}}}
.title{{font-family:'MM Display';font-size:104px;letter-spacing:-.02em;line-height:.98;margin-top:22px}}
.tag{{font-family:'MM Serif';font-size:33px;line-height:1.15;color:{SOFT};margin-top:14px}}
.tag em{{font-style:normal;color:{ACCENT}}}
.desc{{font-size:20px;line-height:1.55;color:{SOFT};margin-top:22px;max-width:520px}}
.pills{{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}}
.pill{{font-family:'MM Mono';font-size:12.5px;letter-spacing:.12em;text-transform:uppercase;color:{SOFT};
  border:1.5px solid {LINE};border-radius:999px;padding:8px 14px;background:rgba(255,255,255,.02)}}
.status{{display:inline-flex;align-items:center;gap:10px;font-family:'MM Mono Bold';font-size:14px;
  letter-spacing:.22em;text-transform:uppercase;color:{SOFT}}}
.dot{{width:10px;height:10px;border-radius:50%;background:{ACCENT};box-shadow:0 0 0 5px rgba(169,180,192,.14)}}
.dot.live{{background:{SIGNAL};box-shadow:0 0 0 5px rgba(244,240,230,.14),0 0 18px rgba(244,240,230,.55)}}
.stats{{display:flex;gap:48px;margin-top:30px}}
.stat .n{{font-family:'MM Display';font-size:64px;letter-spacing:-.01em;line-height:1;color:{TEXT}}}
.stat .n.v{{color:{ACCENT}}}
.stat .l{{font-family:'MM Mono';font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:{MUTED};
  margin-top:10px;line-height:1.6}}
.window{{border-radius:18px;border:1.5px solid {LINE};background:{PANEL};overflow:hidden;
  box-shadow:0 40px 90px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.02),0 0 120px rgba(255,255,255,.05)}}
.chrome{{display:flex;align-items:center;gap:8px;height:48px;padding:0 18px;border-bottom:1.5px solid {LINE};
  background:{RAISED};font-family:'MM Mono';font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:{MUTED}}}
.chrome i{{width:11px;height:11px;border-radius:50%;background:#333;display:block}}
.chrome i:first-child{{background:{ACCENT}}}
.chrome span{{margin-left:12px}}
.shot{{position:relative;overflow:hidden;background:#000}}
.shot img{{position:absolute;display:block}}
@media (max-width:700px){{
  .card{{border-radius:22px}}
  .title{{font-size:76px}}
  .tag{{font-size:28px}}
  .desc{{font-size:19px;max-width:none}}
  .pill{{font-size:14px;padding:9px 15px}}
  .eyebrow{{font-size:15px}}
  .stats{{gap:36px}}
  .stat .n{{font-size:50px}}
  .stat .l{{font-size:13px}}
}}
"""


def page(body: str, seed: int, extra_css: str = "") -> str:
    return (f"<!doctype html><meta charset=utf-8><style>{CSS}{extra_css}</style>"
            f'<div class="card">{starfield(seed)}<div class="grain"></div>{body}</div>')


def pills(*names: str) -> str:
    return '<div class="pills">' + "".join(f'<span class="pill">{esc(n)}</span>' for n in names) + "</div>"


def screenshot(src: str, crop: tuple[int, int, int, int], width: int) -> str:
    """Crop (x, y, w, h) out of a screenshot in scripts/shots and scale it to `width` px."""
    x, y, w, h = crop
    s = width / w
    from PIL import Image

    img = (SHOTS / src).as_uri()
    full_w = Image.open(SHOTS / src).width * s
    return (f'<div class="shot" style="width:{width}px;height:{h * s:.0f}px">'
            f'<img src="{img}" style="width:{full_w:.0f}px;left:{-x * s:.0f}px;top:{-y * s:.0f}px"></div>')


# --- Imperium ---------------------------------------------------------------

TRACE = [
    ("PAIR", "token verified · paired phone", "ok"),
    ("PLAN", 'open Spotify → search "Drake" → play', "ok"),
    ("PERMIT", "low risk · no confirm tap needed", "ok"),
    ("GATE", "script lexed · app on allowlist", "ok"),
    ("RUN", 'tell application "Spotify"', "run"),
]


LOOP = 7.6  # seconds: message in, five checkpoints, audit, hold, reset
RESET = (6.9, 7.3)


def ease(a: float, b: float, t: float) -> float:
    """0 before a, 1 after b, smoothstep between."""
    x = min(max((t - a) / (b - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)


def imperium_state(t: float | None) -> dict:
    """How far each part of the trace has played at time t; None is the finished poster frame."""
    if t is None:
        return {"bubble": 1.0, "rows": [1.0] * len(TRACE), "audit": 1.0, "result": 1.0}
    out = 1 - ease(*RESET, t)
    return {
        "bubble": ease(0.2, 0.6, t) * out,
        "rows": [ease(1.1 + 0.6 * i - 0.3, 1.1 + 0.6 * i, t) * out for i in range(len(TRACE))],
        "audit": ease(4.4, 4.8, t) * out,
        "result": ease(5.0, 5.4, t) * out,
    }


def imperium_frames() -> list[tuple[float, int]]:
    """(time, milliseconds) samples: 15 fps while something moves, one long frame while it holds."""
    # 5.0-6.9 covers the result sliding in and the equalizer bouncing while it holds.
    moving = [(0.2, 0.6), (4.4, 4.8), (5.0, 6.9), RESET] + [(0.8 + 0.6 * i, 1.1 + 0.6 * i) for i in range(len(TRACE))]
    times = {0.0, LOOP}
    for a, b in moving:
        n = max(int((b - a) * 15), 1)
        times.update(round(a + (b - a) * k / n, 3) for k in range(n + 1))
    times = sorted(times)
    return [(t, round((nxt - t) * 1000)) for t, nxt in zip(times, times[1:]) if nxt > t]


def eq_bars(t: float | None) -> str:
    """Four equalizer bars; they bounce while the song plays and rest at a fixed shape on the poster."""
    import math
    rest = [0.4, 0.95, 0.6, 0.8]
    if t is None:
        heights = rest
    else:
        heights = [0.25 + 0.75 * abs(math.sin(t * (5.3 + k * 1.7) + k)) for k in range(4)]
    return "".join(f'<i style="height:{h * 100:.0f}%"></i>' for h in heights)


def imperium(t: float | None = None) -> str:
    st = imperium_state(t)
    rows = "".join(
        f'<div class="row" style="--p:{p:.3f}"><b class="{kind}">{"" if kind == "ok" else "▸"}</b>'
        f'<span class="k">{k}</span><span class="v">{esc(v)}</span></div>'
        for (k, v, kind), p in zip(TRACE, st["rows"])
    )
    fill = sum(st["rows"]) / len(TRACE)
    b = st["bubble"]
    body = f"""
<div class="wrap">
  <div class="text">
    <div class="eyebrow">01 · Featured · AI agent</div>
    <div class="title">Imperium</div>
    <div class="tag">Plain English in. <em>Real actions out.</em></div>
    <div class="desc">A FastAPI agent that turns texts from my phone into AppleScript and app actions on my Mac, built with collaborators. Security is the core feature, not an afterthought.</div>
    <div class="stats">
      <div class="stat"><div class="n v">5</div><div class="l">checkpoints<br>per command</div></div>
      <div class="stat"><div class="n">0</div><div class="l">raw model scripts<br>ever executed</div></div>
    </div>
    {pills("Python", "FastAPI", "AppleScript", "Anthropic API", "Playwright")}
  </div>
  <div class="window visual">
    <div class="chrome"><i></i><i></i><i></i><span>imperium · trace</span></div>
    <div class="inner">
      <div class="from">From phone · paired</div>
      <div class="bubble" style="opacity:{b:.3f};transform:translateY({(1 - b) * 12:.1f}px)">Play Drake on Spotify</div>
      <div class="trace" style="--f:{fill:.3f}"><i class="fill"></i>{rows}</div>
      <div class="audit" style="opacity:{0.25 + 0.75 * st['audit']:.3f}"><span class="dot live" style="opacity:{st['audit']:.3f}"></span>audit · entry written to audit.db</div>
      <div class="result" style="opacity:{st['result']:.3f};transform:translateY({(1 - st['result']) * 10:.1f}px)">
        <span class="eq">{eq_bars(t)}</span>
        <span><b>Now playing on the Mac</b><small>Spotify · Drake</small></span>
      </div>
    </div>
  </div>
</div>"""
    css = f"""
.wrap{{position:relative;display:flex;gap:56px;padding:64px 0 0 64px;height:100%}}
.text{{width:540px;flex:none}}
.visual{{width:560px;flex:none;align-self:stretch;margin-top:6px;border-bottom-right-radius:0;
  border-right:none;border-bottom:none;border-top-right-radius:0}}
.inner{{padding:30px 34px}}
.from{{font-family:'MM Mono';font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:{MUTED};text-align:right}}
.bubble{{margin:12px 0 0 auto;width:max-content;max-width:80%;background:{TEXT};color:{INK};font-size:21px;
  padding:14px 20px;border-radius:20px 20px 6px 20px;font-family:'MM Body Bold'}}
.trace{{position:relative;margin-top:30px;padding-left:4px}}
.trace:before{{content:"";position:absolute;left:13px;top:14px;bottom:14px;width:1.5px;background:{LINE}}}
.fill{{position:absolute;left:13px;top:14px;width:1.5px;height:calc(var(--f) * (100% - 28px));
  background:linear-gradient({ACCENT},{ACCENT_DIM} 70%,{SIGNAL})}}
.row{{opacity:calc(.3 + .7 * var(--p))}}
.row b.ok:before{{content:'';width:4px;height:8px;margin-top:-2px;border:solid {ACCENT};border-width:0 1.5px 1.5px 0;
  transform:rotate(45deg);opacity:var(--p)}}
.row{{position:relative;display:flex;align-items:center;gap:16px;height:52px;font-family:'MM Mono';font-size:15.5px}}
.row b{{width:20px;height:20px;border-radius:50%;display:grid;place-items:center;font-size:11px;flex:none;
  background:{PANEL};border:1.5px solid color-mix(in srgb,{ACCENT} calc(var(--p) * 100%),{LINE});color:{ACCENT};
  margin-left:0}}
.row b.run{{border-color:color-mix(in srgb,{SIGNAL} calc(var(--p) * 100%),{LINE});color:{SIGNAL};
  box-shadow:0 0 calc(var(--p) * 16px) rgba(244,240,230,.4)}}
.row .k{{width:74px;color:{TEXT};letter-spacing:.12em;font-family:'MM Mono Bold';font-size:14px}}
.row .v{{color:{SOFT};white-space:nowrap}}
.result{{display:flex;align-items:center;gap:16px;margin-top:14px;padding:16px 18px;border-radius:12px;
  background:{RAISED};border:1.5px solid {LINE}}}
.result b{{display:block;font-family:'MM Body Bold';font-weight:400;font-size:17px;color:{TEXT}}}
.result small{{display:block;margin-top:3px;font-family:'MM Mono';font-size:12.5px;letter-spacing:.14em;
  text-transform:uppercase;color:{MUTED}}}
.eq{{display:flex;align-items:flex-end;gap:3px;height:22px;width:22px}}
.eq i{{display:block;width:4px;border-radius:1px;background:{ACCENT}}}
.audit{{display:flex;align-items:center;gap:12px;margin-top:26px;padding:14px 18px;border:1.5px dashed {LINE};
  border-radius:12px;font-family:'MM Mono';font-size:14px;letter-spacing:.08em;color:{SOFT}}}
@media (max-width:700px){{
  .wrap{{flex-direction:column;gap:40px;padding:44px 36px 0}}
  .text,.visual{{width:auto}}
  .visual{{margin:0 -36px 0 0}}
  .row{{font-size:15px}} .row .v{{white-space:normal}}
}}"""
    return page(body, seed=11, extra_css=css)


# --- Screenshot cards -------------------------------------------------------

def shot_card(eyebrow: str, title: str, tag: str, desc: str, status: str, live: bool, tags: list[str],
              shot: str, crop: tuple[int, int, int, int], flip: bool, seed: int, url: str,
              tone: str | None = None) -> str:
    """`tone` turns a screenshot steel so it sits in the monochrome page: "light" for bright sites
    (dimmed duotone), "dark" for dark apps (grayscale, lifted slightly)."""
    text = f"""
  <div class="text">
    <div class="eyebrow">{eyebrow}</div>
    <div class="title">{esc(title)}</div>
    <div class="tag">{tag}</div>
    <div class="desc">{esc(desc)}</div>
    <div class="meta"><span class="status"><span class="dot{' live' if live else ''}"></span>{status}</span></div>
    {pills(*tags)}
  </div>"""
    visual = f"""
  <div class="window visual">
    <div class="chrome"><i></i><i></i><i></i><span>{esc(url)}</span></div>
    {screenshot(shot, crop, 700 if flip else 820)}
  </div>"""
    body = (f'<div class="wrap{" flip" if flip else ""}{f" toned {tone}" if tone else ""}">'
            f'{visual + text if flip else text + visual}</div>')
    css = f"""
.wrap{{position:relative;display:flex;gap:56px;height:100%;padding:64px 0 0 64px}}
.wrap.flip{{padding:64px 64px 0 0;gap:44px}}
.wrap.flip .text{{width:392px}}
.text{{width:430px;flex:none}}
.title{{font-size:92px}}
.visual{{width:820px;flex:none;align-self:flex-start;margin-top:14px}}
.wrap:not(.flip) .visual{{border-top-right-radius:0;border-right:none}}
.wrap.flip .visual{{width:700px;border-top-left-radius:0;border-left:none}}
.meta{{display:flex;flex-direction:column;gap:10px;margin-top:26px}}
.toned .shot img{{filter:grayscale(1) brightness(.74) contrast(1.18)}}
.toned.dark .shot img{{filter:grayscale(1) brightness(1.12) contrast(1.12)}}
.toned.dark .shot:after{{display:none}}
.toned .shot:after{{content:'';position:absolute;inset:0;background:linear-gradient(160deg,rgba(169,180,192,.30),rgba(10,10,10,.28));mix-blend-mode:multiply}}
.toned .shot:before{{content:'';position:absolute;inset:0;z-index:1;background:{ACCENT};mix-blend-mode:color;opacity:.22}}
.url{{font-family:'MM Mono';font-size:14px;letter-spacing:.06em;color:{MUTED}}}
@media (max-width:700px){{
  .wrap,.wrap.flip{{flex-direction:column;gap:40px;padding:44px 36px 0}}
  .text{{width:auto;order:0}}
  .visual{{order:1}}
  .title{{font-size:72px}}
  .visual,.wrap.flip .visual{{margin:0 -36px 0 0;width:auto;border-top-right-radius:0;border-right:none;
    border-top-left-radius:18px;border-left:1.5px solid {LINE}}}
  .shot{{zoom:.566}}
  .wrap.flip .shot{{zoom:.663}}
}}"""
    return page(body, seed=seed, extra_css=css)


def ledger() -> str:
    return shot_card(
        "02 · Personal finance", "Ledger.m", "Every account, <em>one calm dashboard.</em>",
        "A single-user finance app wired to my real bank accounts through Plaid. Net worth, spending and income "
        "by category, monthly budgets, subscriptions, and what's due next.",
        "Private deploy", False, ["Next.js", "Supabase", "Plaid", "Tailwind"],
        "ledger.png", (292, 0, 1708, 1011), flip=True, seed=21, url="ledgerm.vercel.app", tone="dark",
    )


def dummy() -> str:
    return shot_card(
        "04 · E-commerce", "Dummy Peptides", "Catalog to checkout, <em>live.</em>",
        "The storefront for a research-peptide business I co-own: catalog, accounts, cart, and an affiliate "
        "program, with shipping, email, and SMS built in.",
        "Live", True, ["React", "Supabase", "Shippo", "Twilio"],
        "dummypeptides.png", (186, 110, 1244, 770), flip=True, seed=31, url="dummypeptides.com", tone="light",
    )


# --- Cosmo --------------------------------------------------------------------

def cosmo() -> str:
    phone = (SHOTS / "cosmo.png").as_uri()
    body = f"""
<div class="orbit o1"></div><div class="orbit o2"></div>
<div class="wrap">
  <div class="text">
    <div class="eyebrow">03 · iOS app</div>
    <div class="title">Cosmo</div>
    <div class="tag">Your guide through the stars, <em>dreams, and destiny.</em></div>
    <div class="desc">An iOS-first astrology app with personalized AI-generated readings, user accounts, and paid subscriptions through RevenueCat.</div>
    {pills("Expo", "React Native", "TypeScript", "Supabase", "RevenueCat", "OpenAI")}
  </div>
  <img class="phone" src="{phone}">
</div>"""
    css = f"""
.card{{background:radial-gradient(620px 620px at 78% 42%,rgba(255,255,255,.09),transparent 65%),
  radial-gradient(900px 500px at 0% 110%,rgba(169,180,192,.06),transparent 60%),{INK}}}
.wrap{{position:relative;display:flex;align-items:center;gap:40px;height:100%;padding:0 40px 0 64px}}
.text{{width:560px;flex:none}}
.phone{{height:660px;margin:0 0 0 70px;filter:grayscale(1) sepia(.18) hue-rotate(175deg) saturate(.7) brightness(.96) contrast(1.08) drop-shadow(0 40px 60px rgba(0,0,0,.6))}}
.orbit{{position:absolute;border:1.5px solid rgba(255,255,255,.10);border-radius:50%}}
.o1{{width:560px;height:560px;left:672px;top:26px}}
.o2{{width:760px;height:760px;left:572px;top:-74px;border-style:dashed;border-color:rgba(255,255,255,.07)}}
@media (max-width:700px){{
  .wrap{{flex-direction:column;align-items:flex-start;padding:44px 36px 0;gap:30px}}
  .text{{width:auto}}
  .phone{{height:470px;margin:0 auto}}
  .o1{{left:-40px;top:560px}} .o2{{left:-140px;top:460px}}
}}"""
    return page(body, seed=41, extra_css=css)


# --- In progress ---------------------------------------------------------------

# Facts from each repo's commit history and status docs (StayDue README, EasyMail PROJECT_STATE.md).
STAYDUE_LOG = [
    ("done", "V1 backend: Supabase auth, storage, AI extraction"),
    ("done", "Dashboard and sign-up redesign"),
    ("done", "Google sign-in and LMS selection"),
    ("next", "Private beta"),
]
EASYMAIL_LOG = [
    ("done", "Gmail and Outlook connected"),
    ("done", "Reliability audit, 8 edge cases fixed"),
    ("done", "Landing page and motion system"),
    ("next", "Phase 13: testing"),
]
EASYMAIL_PHASE, EASYMAIL_PHASES = 12, 22


def log(rows: list[tuple[str, str]]) -> str:
    return '<div class="log">' + "".join(
        f'<div class="{kind}"><b>{"" if kind == "done" else "›"}</b>{esc(text)}</div>' for kind, text in rows
    ) + "</div>"


def progress() -> str:
    bar = "".join(f'<i class="{"on" if i < EASYMAIL_PHASE else ""}"></i>' for i in range(EASYMAIL_PHASES))
    body = f"""
<div class="wrap">
  <div class="panel">
    <div class="top"><span class="status"><span class="dot"></span>Private beta</span><span class="eyebrow">05</span></div>
    <div class="title">StayDue</div>
    <div class="tag">Syllabus in. <em>Semester sorted.</em></div>
    <div class="desc">Upload a syllabus PDF, review what it found, and every deadline lands in one dashboard and calendar. Built with a collaborator.</div>
    <div class="label">From the commit log</div>
    {log(STAYDUE_LOG)}
    {pills("Next.js", "Supabase", "OpenAI")}
  </div>
  <div class="panel">
    <div class="top"><span class="status"><span class="dot"></span>In development</span><span class="eyebrow">06</span></div>
    <div class="title">EasyMail</div>
    <div class="tag">Recap first. <em>Inbox second.</em></div>
    <div class="desc">A cross-inbox attention layer for Gmail and Outlook that shows what needs you before you open a mail client.</div>
    <div class="label">Phase {EASYMAIL_PHASE} of {EASYMAIL_PHASES} complete</div>
    <div class="bar">{bar}</div>
    {log(EASYMAIL_LOG)}
    {pills("Next.js", "Supabase", "Vitest")}
  </div>
</div>"""
    css = f"""
.wrap{{position:relative;display:flex;gap:28px;height:100%;padding:28px}}
.panel{{flex:1;border:1.5px solid {LINE};border-radius:20px;background:rgba(17,17,17,.72);padding:36px 38px}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.title{{font-size:68px;margin-top:22px}}
.tag{{font-size:31px}}
.desc{{font-size:18px;max-width:none}}
.label{{font-family:'MM Mono Bold';font-size:12px;letter-spacing:.22em;text-transform:uppercase;color:{MUTED};
  margin-top:30px}}
.bar{{display:grid;grid-template-columns:repeat(22,1fr);gap:4px;margin-top:12px}}
.bar i{{height:10px;border-radius:2px;background:{RAISED};border:1px solid {LINE}}}
.bar i.on{{background:{ACCENT};border-color:{ACCENT}}}
.bar i.on:nth-child(12){{background:{SIGNAL};border-color:{SIGNAL};box-shadow:0 0 12px rgba(244,240,230,.45)}}
.log{{margin-top:14px;border-top:1.5px solid {LINE}}}
.log div{{display:flex;align-items:center;gap:14px;padding:11px 0;border-bottom:1.5px solid {LINE};
  font-family:'MM Mono';font-size:14.5px;color:{SOFT}}}
.log b{{width:18px;font-weight:400;color:{MUTED};text-align:center;display:grid;place-items:center}}
.log .done b:before{{content:'';width:5px;height:10px;margin-top:-3px;border:solid {MUTED};border-width:0 1.5px 1.5px 0;transform:rotate(45deg)}}
.log .next{{color:{TEXT}}}
.log .next b{{color:{ACCENT}}}
.bar + .log{{margin-top:18px}}
@media (max-width:700px){{
  .wrap{{flex-direction:column;padding:20px;gap:20px;height:auto}}
  .panel{{flex:none}}
  .panel{{padding:32px 30px}}
  .title{{font-size:62px}}
  .desc{{font-size:18px}}
}}"""
    return page(body, seed=51, extra_css=css)


CARDS = {
    "imperium": (imperium, 740, 1290),
    "ledger": (ledger, 650, 790),
    "dummypeptides": (dummy, 640, 960),
    "cosmo": (cosmo, 680, 960),
    "progress": (progress, 680, 1400),
}


def main(only: list[str] | None = None) -> None:
    for name, (build, desktop_h, phone_h) in CARDS.items():
        if only and name not in only:
            continue
        if name == "imperium":  # animated: the trace plays out, holds, and resets
            frames = [(imperium(t), ms) for t, ms in imperium_frames()]
            render_anim(frames, ASSETS / "cards" / f"{name}.webp", DESKTOP_W, desktop_h, scale=2)
            render_anim(frames, ASSETS / "cards" / f"{name}-phone.webp", PHONE_W, phone_h, scale=2)
            continue
        html = build()
        render(html, ASSETS / "cards" / f"{name}.webp", DESKTOP_W, desktop_h, scale=2)
        render(html, ASSETS / "cards" / f"{name}-phone.webp", PHONE_W, phone_h, scale=2)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
