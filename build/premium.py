# ---------- premium redesign (presentation only; TG Oct 29) ----------
# exec'd by clean_build.py just before _deepcheck(): rewrites index.html with a uniform every-game slate
# and re-skins every other generated page with the same header + design system. No rating/grade logic here.
import html as _h
_E=_h.escape
DS_CSS='''<style id="ds">
@font-face{font-family:Inter;src:url(assets/fonts/inter-latin.woff2) format("woff2");font-weight:100 900;font-display:swap}
:root{--bg:#0d1117;--bg2:#131a23;--card:#161e29;--line:#253041;--txt:#e6edf3;--mut:#9aa7b4;--acc:#7cc4ff;--st:#3fcf8e;--le:#e3b341;--pa:#8b98a5;--txt-st:#0b2a1c;--txt-le:#2b2108;--focus:#7cc4ff;--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
html{background:var(--bg)}body{margin:0;background:var(--bg)!important;color:var(--txt)!important;font:15px/1.55 Inter,system-ui,-apple-system,Segoe UI,Roboto,sans-serif!important;-webkit-font-smoothing:antialiased}
a{color:var(--acc)}a:focus-visible,button:focus-visible,summary:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--focus)!important;outline-offset:2px;border-radius:4px}
.skip{position:absolute;left:-999px;top:8px;background:var(--acc);color:#000;padding:8px 12px;border-radius:6px;z-index:99;font-weight:700}.skip:focus{left:8px}
.ds-head{position:sticky;top:0;z-index:50;background:rgba(13,17,23,.94);backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.ds-head .in{max-width:1080px;margin:0 auto;padding:10px 16px;display:flex;flex-wrap:wrap;align-items:center;gap:6px 18px}
.ds-brand{color:var(--txt);text-decoration:none;font-weight:800;letter-spacing:-.2px;font-size:16px}.ds-brand span{color:var(--mut);font-weight:500;font-size:13px;margin-left:8px}
.ds-nav{display:flex;gap:2px;margin-left:auto;flex-wrap:wrap}.ds-nav a{color:var(--mut);text-decoration:none;font-size:14px;font-weight:600;padding:6px 10px;border-radius:6px}
.ds-nav a:hover{color:var(--txt);background:var(--bg2)}.ds-nav a[aria-current=page]{color:var(--txt);background:var(--card);box-shadow:inset 0 -2px 0 var(--acc)}
nav.tabs,header.apphead{display:none!important}
.ds-main{max-width:1080px;margin:0 auto;padding:20px 16px 48px}
.ds-main h1{font-size:26px;letter-spacing:-.5px;margin:6px 0 4px;font-weight:800}.ds-sub{color:var(--mut);margin:0 0 18px;font-size:14px}
.ds-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 22px}
.ds-strip>div{background:var(--bg2);padding:12px 14px}.ds-k{display:block;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--mut);font-weight:600}
.ds-v{display:block;font:700 18px/1.3 var(--mono);margin-top:4px}.ds-v small{font:500 12px Inter,sans-serif;color:var(--mut);margin-left:6px}.pos{color:var(--st)}.neg{color:#ff8a80}
.ds-legend{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:13px;color:var(--mut);margin:0 0 14px}
.slate{list-style:none;margin:0;padding:0;display:grid;gap:12px}
.gc{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--pa);border-radius:10px;padding:14px 16px}
.gc.r-STRONG{border-left-color:var(--st)}.gc.r-LEAN{border-left-color:var(--le)}
.gc-top{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.gc-m{font-weight:700;font-size:16px;margin:0;display:flex;align-items:center;gap:8px}
.gc-m img{width:24px;height:24px;object-fit:contain}.gc-at{color:var(--mut);font-weight:500}.gc-ko{color:var(--mut);font-size:13px;margin-left:auto;font-family:var(--mono)}
.bdg{display:inline-block;font:800 11px/1 Inter,sans-serif;letter-spacing:.08em;padding:5px 8px;border-radius:5px;text-transform:uppercase}
.bdg.STRONG{background:var(--st);color:var(--txt-st)}.bdg.LEAN{background:var(--le);color:var(--txt-le)}.bdg.PASS{background:transparent;color:var(--txt);border:1px solid var(--pa)}
.gc-play{font:700 20px/1.3 var(--mono);margin:10px 0 2px;letter-spacing:-.3px}.gc.r-PASS .gc-play{color:var(--mut)}
.gc-why{color:var(--mut);font-size:13px;margin:0 0 10px}
.gc dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px 18px;margin:0;border-top:1px solid var(--line);padding-top:10px}
.gc dl div{min-width:0}.gc dt{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);font-weight:600}.gc dd{margin:2px 0 0;font-size:14px}
.gc dd .n{font-family:var(--mono);font-weight:700}
.ds-notes{margin:24px 0 0;border:1px solid var(--line);border-radius:10px;background:var(--bg2)}.ds-notes summary{cursor:pointer;padding:12px 14px;font-weight:700}
.ds-notes ul{margin:0;padding:0 14px 14px 32px;color:var(--mut);font-size:14px}
.ds-links{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 0}.ds-links a{border:1px solid var(--line);border-radius:8px;padding:8px 12px;text-decoration:none;font-size:14px;font-weight:600}
.ds-foot{max-width:1080px;margin:0 auto;padding:18px 16px 40px;color:var(--mut);font-size:12px;border-top:1px solid var(--line)}
footer:not(.ds-foot){color:var(--mut)}
table{border-collapse:collapse}th{text-align:left}td,th{font-variant-numeric:tabular-nums}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
@media (max-width:560px){.gc-ko{margin-left:0;width:100%}.gc-play{font-size:18px}.ds-main h1{font-size:22px}}
</style>'''
_NAVI=[('index','index.html','Home'),('week','index.html#slate','This Week'),('results','tygif-tracker.html#results','Records'),('how','tygif-how.html','How')]
def ds_head(cur):
    a=''.join(f'<a href="{h}"'+(' aria-current="page"' if k==cur else '')+f'>{t}</a>' for k,h,t in _NAVI)
    return (f'<a class="skip" href="#main">Skip to content</a><header class="ds-head" role="banner"><div class="in">'
            f'<a class="ds-brand" href="index.html">tygif&#8217;s model<span>Week {GW} · as of {_E(PULL6.replace(" ET",""))} CT</span></a>'
            f'<nav class="ds-nav" aria-label="Primary">{a}</nav></div></header>')
DS_FOOT=f'<footer class="ds-foot" role="contentinfo">{_E(FOOT)}</footer>'
def _ct(g): return _etlbl(g['ko_utc']) if g.get('ko_utc') else g.get('when','')
def _logo(ab,name): 
    ab={'LA':'LAR','WAS':'WSH','JAC':'JAX'}.get(ab,ab); return f'<img src="assets/logos/{ab}.png" alt="{_E(name)} logo" width="24" height="24" loading="lazy">'
def _agree(g):
    if g.get('c') is None or g.get('agree')=='none': return 'DK: no split — n/a'
    src='bets %' if g.get('agree')=='DraftKings bets %' else 'money %'
    return f"DK {src}: {'same side' if g['c'] else 'opposite side'} ({AB[g['dk_side']]} {g['dk_m']}%)"
def _bneed(g):
    v=book_view(g)
    if not v: return '—'
    return {'exposed':f"Needs {v['fade']} · {v['pub']} {v['money']}% vs {v['be']:.1f}% break-even",
            'locked':f"Locked · {v['pub']} {v['money']}% inside {v['lock_lo']:.1f}–{v['be']:.1f}%",
            'against':f"Needs {v['pub']} · {v['pub']} {v['money']}% under {v['lock_lo']:.1f}%"}[v['state']]
def _best(g):
    r=g['rating']; f=AB[g['fade']]; ln=g['sp'].get(f,'')
    if r!='PASS': return f'{f} {ln}', f"Fade the crowd on {AB[g['ab_side']]}"
    return 'PASS — no edge', f"Fade candidate {f} {ln} · "+pass_reason(g)
def _mlc(g):
    if g['rating']=='PASS': return '—'
    if not ml_ok(g): return f"{AB[g['fade']]} ML · not posted (group not profitable)" if ml_for(g,_gwk(g)) else '— (no DK moneyline)'
    return f"<span class=\"n\">{AB[g['fade']]} ML</span> · posted"
def game_card(g):
    r=g['rating']; t=g['type']; play,why=_best(g); m=AB[g['ab_side']]
    return (f'<li class="gc r-{r}" id="{g["gid"]}"><article aria-labelledby="h-{g["gid"]}"><div class="gc-top">'
            f'<span class="bdg {r}" aria-label="Rating: {r}">{r}</span>'
            f'<h3 class="gc-m" id="h-{g["gid"]}">{_logo(g["A"],g["away"])}{_E(g["away"])} <span class="gc-at">at</span> {_logo(g["H"],g["home"])}{_E(g["home"])}</h3>'
            f'<span class="gc-ko"><span class="sr-only" style="position:absolute;left:-999px">Kickoff </span>{_E(_ct(g))}</span></div>'
            f'<p class="gc-play"><span style="position:absolute;left:-999px">Best play: </span>{_E(play)}</p><p class="gc-why">{_E(why)}</p><dl>'
            f'<div><dt>Crowd money (all books)</dt><dd><span class="n">{m} {g["ab_m"]}%</span> money · {g["ab_b"]}% bets</dd></div>'
            f'<div><dt>DraftKings agreement</dt><dd>{_E(_agree(g))}</dd></div>'
            f'<div><dt>Book needs</dt><dd>{_E(_bneed(g))}</dd></div>'
            f'<div><dt>Moneyline</dt><dd>{_mlc(g)}</dd></div>'
            f'<div><dt>Type</dt><dd><span class="n">{t}</span> · {_E(TY[t]["name"])}</dd></div></dl></article></li>')
def _rt(rt):
    w,l,p,u,n=at(rt); return f'<div><span class="ds-k">{rt} record</span><span class="ds-v">{w}-{l}-{p}<small class="{"pos" if u>0 else "neg"}">{usd(u)} · {n} plays</small></span></div>'
_cnt={k:sum(g['rating']==k for g in ALL6) for k in ('STRONG','LEAN','PASS')}
_dkbets=any(g.get('agree')=='DraftKings bets %' for g in ALL6)
HOME2=(f'<main id="main" class="ds-main" tabindex="-1"><h1>Week {GW} board</h1>'
  f'<p class="ds-sub">{len(ALL6)} games tracked · {_cnt["STRONG"]} STRONG · {_cnt["LEAN"]} LEAN · {_cnt["PASS"]} PASS · sorted by kickoff (CT)</p>'
  f'<section aria-label="Season records and data source" class="ds-strip">{_rt("STRONG")}{_rt("LEAN")}'
  f'<div><span class="ds-k">Data</span><span class="ds-v" style="font-size:14px">As of {_E(_etlbl(max(g['split_utc'] for g in ALL6)))}</span></div>'
  f'<div><span class="ds-k">Agreement source</span><span class="ds-v" style="font-size:14px;font-family:Inter,sans-serif">DraftKings {"bets % (handle unavailable)" if _dkbets else "money %"}</span></div></section>'
  f'<section aria-labelledby="slate-h"><h2 id="slate-h" style="font-size:18px;margin:0 0 10px">Full slate <span id="slate"></span></h2>'
  f'<p class="ds-legend">Every card shows the same fields. Best play is always the fade side; PASS cards name the fade candidate and why it does not qualify.</p>'
  f'<ol class="slate">{"".join(game_card(g) for g in ALL6)}</ol></section>'
  f'<details class="ds-notes"><summary>Notes</summary><ul><li>Calls before kickoff are previews and can change as the money moves. Graded at the DraftKings line, price and moneyline recorded at least 5 minutes before kickoff.</li><li>Crowd money = mean of all-books spread and moneyline money % on the money side (ScoresAndOdds).</li>'
  f'<li>STRONG and LEAN records are kept separate and never combined. Flat $100 per play.</li><li>Book needs compares all-books money to the DraftKings break-even; information only, never changes a rating.</li></ul></details>'
  f'<nav class="ds-links" aria-label="More"><a href="tygif-tracker.html#results">Records</a><a href="tygif-how.html">How it works</a><a href="tygif-week-{GW}-plays.txt">Week {GW} card (text)</a><a href="tygif-week-{GW}-buddy.txt">Short version</a><a href="tygif-deep-dive.html">Game by game</a></nav></main>')
wr('index.html','<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
   f'<meta name="description" content="tygif\'s model — Week {GW} NFL board: every game rated STRONG, LEAN or PASS."><meta name="color-scheme" content="dark">'
   f'<title>tygif\'s model · Week {GW}</title>{DS_CSS}</head><body>{ds_head("index")}{HOME2}{DS_FOOT}</body></html>\n')
# re-skin every other generated page: shared header, skip link, design-system CSS (appended last so it wins)
_CUR={'tygif-tracker.html':'results','tygif-how.html':'how'}
for _f in _gg.glob(R+'*.html'):
    _b=os.path.basename(_f)
    if _b=='index.html': continue
    _x=open(_f,encoding='utf-8').read()
    if 'id="ds"' in _x: _x=re.sub(r'<style id="ds">.*?</style>','',_x,flags=re.S); _x=re.sub(r'<a class="skip".*?</header>','',_x,flags=re.S); _x=re.sub(r'<footer class="ds-foot".*?</footer>','',_x,flags=re.S)
    _x=_x.replace('</head>',DS_CSS+'</head>',1)
    _x=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+ds_head(_CUR.get(_b,'')),_x,count=1)
    if 'id="main"' not in _x: _x=re.sub(r'<main(?![^>]*id=)',r'<main id="main" tabindex="-1"',_x,count=1)
    if 'id="main"' not in _x: _x=_x.replace(ds_head(_CUR.get(_b,'')),ds_head(_CUR.get(_b,''))+'<div id="main" tabindex="-1"></div>',1)
    _x=re.sub(r'<img((?![^>]*alt=)[^>]*)>',r'<img alt=""\1>',_x)
    if '<html>' in _x: _x=_x.replace('<html>','<html lang="en">',1)
    _x=_x.replace('</body>',DS_FOOT+'</body>',1) if 'ds-foot' not in _x else _x
    wr(_b,_x)
print('premium skin ok:',len(ALL6),'games',_cnt)
