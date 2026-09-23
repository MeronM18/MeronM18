"""Project cards: HTML/CSS rendered to WebP by headless Chrome.

Each card renders twice from the same HTML: a 1200px desktop layout and a 480px
phone layout (picked by a CSS media query), both at high DPI.
"""

from __future__ import annotations

from brand import (ASSETS, INK, LINE, MUTED, PANEL, RAISED, SHOTS, SOFT, TEXT, VIOLET, VIOLET_DIM, VOLT,
                   esc, font_files_css, render, stars)

DESKTOP_W = 1200
PHONE_W = 500


def starfield(seed: int, n: int = 70) -> str:
    dots = "".join(
        f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" opacity="{o * 0.55:.2f}"/>'
        for x, y, r, o in stars(n, 1200, 1400, seed)
    )
    return f'<svg class="stars" viewBox="0 0 1200 1400" preserveAspectRatio="xMidYMin slice">{dots}</svg>'


CSS = f"""
{font_files_css()}
*{{box-sizing:border-box;margin:0;padding:0}}
html,body{{background:transparent;width:100%;height:100%}}
.card{{position:relative;width:100vw;height:100vh;border-radius:28px;overflow:hidden;color:{TEXT};
  font-family:'MM Body';border:1.5px solid {LINE};
  background:radial-gradient(900px 520px at 88% -10%,rgba(169,148,255,.20),transparent 60%),
             radial-gradient(700px 500px at -10% 120%,rgba(107,88,214,.16),transparent 60%),{INK}}}
.stars{{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}}
.grain{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.018) 1px,transparent 1px);
  background-size:100% 44px;pointer-events:none}}
.eyebrow{{font-family:'MM Mono Bold';font-size:15px;letter-spacing:.24em;text-transform:uppercase;color:{VIOLET}}}
.title{{font-family:'MM Display';font-size:104px;letter-spacing:-.035em;line-height:.95;margin-top:22px}}
.tag{{font-family:'MM Serif';font-size:38px;line-height:1.1;color:{SOFT};margin-top:14px}}
.tag em{{font-style:normal;color:{VIOLET}}}
.desc{{font-size:20px;line-height:1.55;color:{SOFT};margin-top:22px;max-width:520px}}
.pills{{display:flex;flex-wrap:wrap;gap:10px;margin-top:28px}}
.pill{{font-family:'MM Mono';font-size:13px;letter-spacing:.16em;text-transform:uppercase;color:{SOFT};
  border:1.5px solid {LINE};border-radius:999px;padding:9px 16px;background:rgba(255,255,255,.02)}}
.status{{display:inline-flex;align-items:center;gap:10px;font-family:'MM Mono Bold';font-size:14px;
  letter-spacing:.22em;text-transform:uppercase;color:{SOFT}}}
.dot{{width:10px;height:10px;border-radius:50%;background:{VIOLET};box-shadow:0 0 0 5px rgba(169,148,255,.15)}}
.dot.live{{background:{VOLT};box-shadow:0 0 0 5px rgba(212,255,79,.16),0 0 18px rgba(212,255,79,.5)}}
.stats{{display:flex;gap:48px;margin-top:30px}}
.stat .n{{font-family:'MM Display';font-size:58px;letter-spacing:-.03em;line-height:1;color:{TEXT}}}
.stat .n.v{{color:{VIOLET}}}
.stat .l{{font-family:'MM Mono';font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:{MUTED};
  margin-top:10px;line-height:1.6}}
.window{{border-radius:18px;border:1.5px solid {LINE};background:{PANEL};overflow:hidden;
  box-shadow:0 40px 90px rgba(0,0,0,.55),0 0 0 1px rgba(255,255,255,.02),0 0 120px rgba(169,148,255,.12)}}
.chrome{{display:flex;align-items:center;gap:8px;height:48px;padding:0 18px;border-bottom:1.5px solid {LINE};
  background:{RAISED};font-family:'MM Mono';font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:{MUTED}}}
.chrome i{{width:11px;height:11px;border-radius:50%;background:#3a3a48;display:block}}
.chrome i:first-child{{background:{VIOLET}}}
.chrome span{{margin-left:12px}}
.shot{{position:relative;overflow:hidden;background:#000}}
.shot img{{position:absolute;display:block}}
@media (max-width:700px){{
  .card{{border-radius:22px}}
  .title{{font-size:76px}}
  .tag{{font-size:31px}}
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
    img = (SHOTS / src).as_uri()
    full_w = 1600 * s  # the stored screenshots are 1600px wide
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


def imperium() -> str:
    rows = "".join(
        f'<div class="row"><b class="{kind}">{"✓" if kind == "ok" else "▸"}</b>'
        f'<span class="k">{k}</span><span class="v">{esc(v)}</span></div>'
        for k, v, kind in TRACE
    )
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
      <div class="bubble">Play Drake on Spotify</div>
      <div class="trace">{rows}</div>
      <div class="audit"><span class="dot live"></span>audit · entry written to audit.db</div>
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
.bubble{{margin:12px 0 0 auto;width:max-content;max-width:80%;background:{VIOLET};color:#120f24;font-size:21px;
  padding:14px 20px;border-radius:20px 20px 6px 20px;font-family:'MM Body Bold'}}
.trace{{position:relative;margin-top:30px;padding-left:4px}}
.trace:before{{content:"";position:absolute;left:13px;top:14px;bottom:14px;width:1.5px;
  background:linear-gradient({VIOLET},{VIOLET_DIM} 70%,{VOLT})}}
.row{{position:relative;display:flex;align-items:center;gap:16px;height:52px;font-family:'MM Mono';font-size:15.5px}}
.row b{{width:20px;height:20px;border-radius:50%;display:grid;place-items:center;font-size:11px;flex:none;
  background:{PANEL};border:1.5px solid {VIOLET};color:{VIOLET};margin-left:0}}
.row b.run{{border-color:{VOLT};color:{VOLT};box-shadow:0 0 16px rgba(212,255,79,.45)}}
.row .k{{width:74px;color:{TEXT};letter-spacing:.12em;font-family:'MM Mono Bold';font-size:14px}}
.row .v{{color:{SOFT};white-space:nowrap}}
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
              shot: str, crop: tuple[int, int, int, int], flip: bool, seed: int, url: str) -> str:
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
    {screenshot(shot, crop, 650 if flip else 820)}
  </div>"""
    body = f'<div class="wrap{" flip" if flip else ""}">{visual + text if flip else text + visual}</div>'
    css = f"""
.wrap{{position:relative;display:flex;gap:56px;height:100%;padding:64px 0 0 64px}}
.wrap.flip{{padding:64px 64px 0 0}}
.text{{width:430px;flex:none}}
.title{{font-size:92px}}
.visual{{width:820px;flex:none;align-self:flex-start;margin-top:14px}}
.wrap:not(.flip) .visual{{border-top-right-radius:0;border-right:none}}
.wrap.flip .visual{{width:650px;border-top-left-radius:0;border-left:none}}
.meta{{display:flex;flex-direction:column;gap:10px;margin-top:26px}}
.url{{font-family:'MM Mono';font-size:14px;letter-spacing:.06em;color:{MUTED}}}
@media (max-width:700px){{
  .wrap,.wrap.flip{{flex-direction:column;gap:40px;padding:44px 36px 0}}
  .text{{width:auto;order:0}}
  .visual{{order:1}}
  .title{{font-size:72px}}
  .visual,.wrap.flip .visual{{margin:0 -36px 0 0;width:auto;border-top-right-radius:0;border-right:none;
    border-top-left-radius:18px;border-left:1.5px solid {LINE}}}
  .shot{{zoom:.566}}
  .wrap.flip .shot{{zoom:.714}}
}}"""
    return page(body, seed=seed, extra_css=css)


def ledger() -> str:
    return shot_card(
        "02 · Personal finance", "Ledger.m", "Every account, <em>one calm dashboard.</em>",
        "A single-user finance app wired to my real bank accounts through Plaid. Net worth, spending and income "
        "by category, subscriptions, and what's due next.",
        "Private deploy", False, ["Next.js", "Supabase", "Plaid", "Tailwind"],
        "ledger.png", (49, 110, 1502, 770), flip=False, seed=21, url="ledgerm.vercel.app",
    )


def dummy() -> str:
    return shot_card(
        "03 · E-commerce", "Dummy Peptides", "From catalog to checkout, <em>live.</em>",
        "The storefront for a research-peptide business I co-own: catalog, accounts, cart, and an affiliate "
        "program, with shipping, email, and SMS built in.",
        "Live", True, ["React", "Supabase", "Shippo", "Twilio"],
        "dummypeptides.png", (49, 110, 1040, 770), flip=True, seed=31, url="dummypeptides.com",
    )


# --- Cosmo --------------------------------------------------------------------

def cosmo() -> str:
    phone = (SHOTS / "cosmo.png").as_uri()
    body = f"""
<div class="orbit o1"></div><div class="orbit o2"></div>
<div class="wrap">
  <div class="text">
    <div class="eyebrow">04 · iOS app</div>
    <div class="title">Cosmo</div>
    <div class="tag">Your guide through the stars, <em>dreams, and destiny.</em></div>
    <div class="desc">An iOS-first astrology app with personalized AI-generated readings, user accounts, and paid subscriptions through RevenueCat.</div>
    {pills("Expo", "React Native", "TypeScript", "Supabase", "RevenueCat", "OpenAI")}
  </div>
  <img class="phone" src="{phone}">
</div>"""
    css = f"""
.card{{background:radial-gradient(620px 620px at 78% 42%,rgba(126,96,255,.34),transparent 65%),
  radial-gradient(900px 500px at 0% 110%,rgba(107,88,214,.18),transparent 60%),#0B0918}}
.wrap{{position:relative;display:flex;align-items:center;gap:40px;height:100%;padding:0 40px 0 64px}}
.text{{width:560px;flex:none}}
.phone{{height:660px;margin:0 0 0 70px;filter:drop-shadow(0 40px 60px rgba(0,0,0,.6))}}
.orbit{{position:absolute;border:1.5px solid rgba(169,148,255,.18);border-radius:50%}}
.o1{{width:560px;height:560px;left:672px;top:26px}}
.o2{{width:760px;height:760px;left:572px;top:-74px;border-style:dashed;border-color:rgba(169,148,255,.12)}}
@media (max-width:700px){{
  .wrap{{flex-direction:column;align-items:flex-start;padding:44px 36px 0;gap:30px}}
  .text{{width:auto}}
  .phone{{height:470px;margin:0 auto}}
  .o1{{left:-40px;top:560px}} .o2{{left:-140px;top:460px}}
}}"""
    return page(body, seed=41, extra_css=css)


# --- In progress ---------------------------------------------------------------

def progress() -> str:
    cal = "".join(f'<i class="{c}"></i>' for c in
                  ["", "", "h", "", "", "", "", "", "", "", "", "h2", "", "", "", "", "", "", "", "", "",
                   "", "", "", "h", "", "", ""])
    body = f"""
<div class="wrap">
  <div class="panel">
    <div class="top"><span class="status"><span class="dot"></span>Private beta</span><span class="eyebrow">05</span></div>
    <div class="title">StayDue</div>
    <div class="tag">Syllabus in. <em>Semester sorted.</em></div>
    <div class="desc">Upload a syllabus PDF, review what it found, and every deadline lands in one dashboard and calendar. Built with a collaborator.</div>
    <div class="art">
      <div class="doc"><b>PDF</b><i></i><i></i><i class="s"></i><i></i></div>
      <div class="arrow">→</div>
      <div class="cal">{cal}</div>
    </div>
    {pills("Next.js", "Supabase", "OpenAI")}
  </div>
  <div class="panel">
    <div class="top"><span class="status"><span class="dot"></span>In development</span><span class="eyebrow">06</span></div>
    <div class="title">EasyMail</div>
    <div class="tag">Recap first. <em>Inbox second.</em></div>
    <div class="desc">A cross-inbox attention layer for Gmail and Outlook that shows what needs you before you ever open a mail client.</div>
    <div class="art mail">
      <div class="src"><span>Gmail</span><span>Outlook</span></div>
      <div class="arrow">→</div>
      <div class="recap"><b>Recap</b><i></i><i class="s"></i><i></i></div>
    </div>
    {pills("Next.js", "Supabase", "Vitest")}
  </div>
</div>"""
    css = f"""
.wrap{{position:relative;display:flex;gap:28px;height:100%;padding:28px}}
.panel{{flex:1;border:1.5px solid {LINE};border-radius:20px;background:rgba(18,18,26,.72);padding:36px 38px}}
.top{{display:flex;justify-content:space-between;align-items:center}}
.title{{font-size:68px;margin-top:22px}}
.tag{{font-size:31px}}
.desc{{font-size:18px;max-width:none}}
.art{{display:flex;align-items:center;gap:22px;margin-top:28px;height:120px}}
.arrow{{font-family:'MM Mono';font-size:26px;color:{VIOLET}}}
.doc{{width:90px;height:116px;border-radius:10px;border:1.5px solid {LINE};background:{RAISED};padding:14px 12px;
  display:flex;flex-direction:column;gap:9px}}
.doc b{{font-family:'MM Mono Bold';font-size:12px;letter-spacing:.14em;color:{VIOLET}}}
.doc i,.recap i{{display:block;height:6px;border-radius:3px;background:#34344a}}
.doc i.s,.recap i.s{{width:60%}}
.cal{{display:grid;grid-template-columns:repeat(7,26px);gap:6px}}
.cal i{{width:26px;height:26px;border-radius:7px;background:{RAISED};border:1.5px solid {LINE}}}
.cal i.h{{background:{VIOLET};border-color:{VIOLET}}}
.cal i.h2{{background:{VOLT};border-color:{VOLT};box-shadow:0 0 14px rgba(212,255,79,.45)}}
.src{{display:flex;flex-direction:column;gap:10px}}
.src span{{font-family:'MM Mono';font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:{SOFT};
  border:1.5px solid {LINE};border-radius:10px;padding:10px 14px;background:{RAISED}}}
.recap{{width:210px;border-radius:12px;border:1.5px solid {VIOLET_DIM};background:{RAISED};padding:14px 16px;
  display:flex;flex-direction:column;gap:10px;box-shadow:0 0 30px rgba(169,148,255,.15)}}
.recap b{{font-family:'MM Mono Bold';font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:{VIOLET}}}
@media (max-width:700px){{
  .wrap{{flex-direction:column;padding:20px;gap:20px;height:auto}}
  .panel{{flex:none}}
  .panel{{padding:32px 30px}}
  .title{{font-size:62px}}
  .desc{{font-size:18px}}
}}"""
    return page(body, seed=51, extra_css=css)


CARDS = {
    "imperium": (imperium, 700, 1190),
    "ledger": (ledger, 620, 790),
    "dummypeptides": (dummy, 620, 960),
    "cosmo": (cosmo, 680, 960),
    "progress": (progress, 620, 1110),
}


def main(only: list[str] | None = None) -> None:
    for name, (build, desktop_h, phone_h) in CARDS.items():
        if only and name not in only:
            continue
        html = build()
        render(html, ASSETS / "cards" / f"{name}.webp", DESKTOP_W, desktop_h, scale=2)
        render(html, ASSETS / "cards" / f"{name}-phone.webp", PHONE_W, phone_h, scale=2)


if __name__ == "__main__":
    import sys
    main(sys.argv[1:] or None)
