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
.ds-head .in{max-width:1200px;margin:0 auto;padding:10px 16px;display:flex;flex-wrap:wrap;align-items:center;gap:6px 18px}
.ds-brand{color:var(--txt);text-decoration:none;font-weight:800;letter-spacing:-.2px;font-size:16px}.ds-brand span{color:var(--mut);font-weight:500;font-size:13px;margin-left:8px}
.ds-nav{display:flex;gap:2px;margin-left:auto;flex-wrap:wrap}.ds-nav a{color:var(--mut);text-decoration:none;font-size:14px;font-weight:600;padding:6px 10px;border-radius:6px}
.ds-nav a:hover{color:var(--txt);background:var(--bg2)}.ds-nav a[aria-current=page]{color:var(--txt);background:var(--card);box-shadow:inset 0 -2px 0 var(--acc)}
nav.tabs,header.apphead{display:none!important}
.ds-main{max-width:1200px;margin:0 auto;padding:20px 16px 48px}
.ds-main h1{font-size:26px;letter-spacing:-.5px;margin:6px 0 4px;font-weight:800}.ds-sub{color:var(--mut);margin:0 0 18px;font-size:14px}
.ds-strip{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:10px;overflow:hidden;margin:0 0 22px}
.ds-strip>div{background:var(--bg2);padding:12px 14px}.ds-k{display:block;font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--mut);font-weight:600}
.ds-v{display:block;font:700 18px/1.3 var(--mono);margin-top:4px}.ds-v small{font:500 12px Inter,sans-serif;color:var(--mut);margin-left:6px}.pos{color:var(--st)}.neg{color:#ff8a80}
.ds-legend{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:13px;color:var(--mut);margin:0 0 14px}
.slate{list-style:none;margin:0;padding:0;display:grid;gap:12px}
.gc{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--pa);border-radius:10px;padding:14px 16px}
.gc.r-STRONG{border-left-color:var(--st)}.gc.r-LEAN{border-left-color:var(--le)}
.gc-top{display:flex;align-items:center;gap:10px;flex-wrap:wrap}.gc-m{font-weight:700;font-size:16px;margin:0;display:flex;align-items:center;gap:8px}
.gc-m img{width:24px;height:24px;object-fit:contain;background:#e9eef4;border-radius:50%;padding:3px;box-sizing:content-box}.gc-at{color:var(--mut);font-weight:500}.gc-ko{color:var(--mut);font-size:13px;margin-left:auto;font-family:var(--mono)}
.bdg{display:inline-block;font:800 11px/1 Inter,sans-serif;letter-spacing:.08em;padding:5px 8px;border-radius:5px;text-transform:uppercase}
.bdg.STRONG{background:var(--st);color:var(--txt-st)}.bdg.LEAN{background:var(--le);color:var(--txt-le)}.bdg.PASS{background:transparent;color:var(--txt);border:1px solid var(--pa)}
.gc-play{font:700 20px/1.3 var(--mono);margin:10px 0 2px;letter-spacing:-.3px}.gc.r-PASS .gc-play{color:var(--txt)}
.gc-why{color:var(--mut);font-size:13px;margin:0 0 10px}
.gc dl{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:8px 18px;margin:0;border-top:1px solid var(--line);padding-top:10px}
.gc dl div{min-width:0}.gc dt{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);font-weight:600}.gc dd{margin:2px 0 0;font-size:14px}
.gc dd .n{font-family:var(--mono);font-weight:700}
.ds-notes{margin:24px 0 0;border:1px solid var(--line);border-radius:10px;background:var(--bg2)}.ds-notes summary{cursor:pointer;padding:12px 14px;font-weight:700}
.ds-notes ul{margin:0;padding:0 14px 14px 32px;color:var(--mut);font-size:14px}
.ds-links{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 0}.ds-links a{border:1px solid var(--line);border-radius:8px;padding:8px 12px;text-decoration:none;font-size:14px;font-weight:600}
.ds-foot{max-width:1200px;margin:0 auto;padding:18px 16px 40px;color:var(--mut);font-size:12px;border-top:1px solid var(--line)}
footer:not(.ds-foot){color:var(--mut)}
.bn{display:block;margin:10px 0 0;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:var(--bg2)}.bn>span{display:block}.bn-h{padding:7px 12px;font-size:12px;color:var(--mut)}.bn-h small{margin-left:6px}.bn-view{color:var(--txt)!important;font-size:13px!important;border-bottom:1px solid var(--line)}.bn-t{padding:7px 12px 2px;font-weight:700}.bn .bn-r{display:grid!important;grid-template-columns:minmax(90px,1.3fr) minmax(110px,1.3fr) 1fr 1fr;gap:8px;padding:6px 12px;border-top:1px solid var(--line);font:13px var(--mono)}.bn-r i{font-style:normal;color:var(--st);font-size:11px;margin-left:6px}.bn-best{background:rgba(63,207,142,.08)}.cd-3{display:grid!important;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:6px 14px;margin-top:8px}.cd-3>span{display:flex;flex-direction:column;font-size:12px;color:var(--mut)}.cd-3 b{color:var(--txt);font-size:14px}.gx{margin-top:10px;border:1px solid var(--line);border-radius:8px;background:var(--bg2)}.gx>summary{display:flex;gap:12px;align-items:center;padding:9px 12px;list-style:none}.gx>summary::-webkit-details-marker{display:none}.gx>summary::after{content:'▸';margin-left:8px;color:var(--mut)}.gx[open]>summary::after{content:'▾'}.gx-k{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);font-weight:700;min-width:92px}.gx-v{font:700 14px var(--mono)}.gx-r{margin-left:auto;font-size:13px;color:var(--mut)}.gx dl{padding:10px 12px;margin:0}.gc .gc-sum{margin-top:6px}.sr-only{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}.ds-v.sm{font-size:14px}.ds-v.txt{font-family:Inter,sans-serif}.ds-pt{font-size:26px;font-weight:800;margin:18px 0 8px}.ds-h2{font-size:18px;margin:26px 0 8px;font-weight:800}table{border-collapse:collapse;width:100%;font-size:14px;background:var(--card)!important;color:var(--txt)!important}th{text-align:left;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut)!important;background:var(--bg2)!important;font-weight:600}td,th{font-variant-numeric:tabular-nums;padding:8px 10px;border-bottom:1px solid var(--line)!important}.ds-wrap{overflow-x:auto}main h1,main h2,main h3{color:var(--txt)!important;letter-spacing:-.3px}main h2{font-size:18px}main p,main li{color:var(--txt)}details>summary{cursor:pointer}main section,main .card,main details.fold{background:var(--card)!important;border-color:var(--line)!important;color:var(--txt)!important}
.bets{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin:10px 0}.bt{border:1px solid var(--line);border-radius:8px;padding:9px 12px;background:var(--bg2);border-top:3px solid var(--pa)}.bt-sp{border-top-color:#58a6ff}.bt-ml{border-top-color:#d2a8ff}.bt.t-PASS{opacity:.72}.bt-k{display:block;font:800 11px Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase}.bt-sp .bt-k{color:#58a6ff}.bt-ml .bt-k{color:#d2a8ff}.bt-v{display:block;font:700 17px/1.3 var(--mono);margin-top:3px}.bt-s{display:block;font-size:12px;color:var(--mut);margin-top:2px}.bt.t-STRONG .bt-s{color:var(--st)}.bt.t-LEAN .bt-s{color:var(--le)}
.bk{display:grid;grid-template-columns:minmax(150px,1fr) 2fr;gap:10px 16px;align-items:center;border-radius:8px;padding:10px 12px;margin:0 0 10px;border:1px solid var(--line);border-left:4px solid var(--pa);background:var(--bg2)}.bk-exposed{border-left-color:var(--st)}.bk-locked{border-left-color:var(--le)}.bk-against{border-left-color:#ff8a80}.bk-k{display:block;font:800 11px Inter,sans-serif;letter-spacing:.12em;text-transform:uppercase;color:var(--mut)}.bk-big{display:block;font:800 20px/1.2 var(--mono)}.bk-exposed .bk-big{color:var(--st)}.bk-against .bk-big{color:#ff8a80}.bk-locked .bk-big{color:var(--le)}.bk-sub{display:block;font-size:12px;color:var(--mut)}.bk-nums{display:flex;gap:16px;flex-wrap:wrap}.bk-nums span{font-size:11px;color:var(--mut);text-transform:uppercase;letter-spacing:.06em}.bk-nums b{display:block;font:700 16px var(--mono);color:var(--txt);text-transform:none;letter-spacing:0}.bk-exposed .bk-d b{color:var(--st)}.bk-against .bk-d b{color:#ff8a80}.bk-bar{position:relative;height:8px;background:var(--line);border-radius:4px;margin-top:8px}.bk-fill{position:absolute;left:0;top:0;bottom:0;background:var(--acc);border-radius:4px}.bk-tick{position:absolute;top:-4px;bottom:-4px;width:2px;background:#fff}.bk-na{grid-template-columns:1fr}.bk-lead{margin:0 0 4px;font:700 15px/1.35 Inter,sans-serif;color:var(--txt)}.bk-plain{margin:0;font-size:13px;line-height:1.45;color:var(--txt)}.bk-r .bk-sub{margin-top:4px}@media(max-width:640px){.bk{grid-template-columns:1fr}}
.mo{display:flex;flex-wrap:wrap;gap:6px 20px;font-size:14px;padding:2px 0 4px}.mo span{display:flex;flex-direction:column}.mo i{font-style:normal;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);font-weight:600}.mo b{font-family:var(--mono)}.mo b.ok{color:var(--st)}.mo b.no{color:#ff8a80}
.gc-pass{margin:4px 0 0;font-size:13px;color:var(--txt);background:rgba(139,152,165,.12);border-radius:6px;padding:6px 10px}.gx>summary{cursor:pointer;min-height:40px}.gx-sp{border-left:3px solid #58a6ff}.gx-ml{border-left:3px solid #d2a8ff}.gx-sp .gx-k{color:#58a6ff}.gx-ml .gx-k{color:#d2a8ff}.gx .bn{margin:0 12px 12px}
@media (max-width:560px){.bk{grid-template-columns:1fr}.bets{grid-template-columns:1fr}}
html{scroll-behavior:smooth}#slate{scroll-margin-top:72px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
@media (max-width:560px){.gc-ko{margin-left:0;width:100%}.gc-play{font-size:18px}.ds-main h1{font-size:22px}}
</style>'''
_NAVI=[('index','index.html#slate','This week'),('history','tygif-history.html','Past weeks'),('results','tygif-tracker.html#hub','Records'),('how','tygif-how.html','How it works')]
def ds_head(cur):
    a=''.join(f'<a href="{h}"'+(' aria-current="page"' if k==cur else '')+f'>{t}</a>' for k,h,t in _NAVI)
    return (f'<a class="skip" href="#main">Skip to content</a><header class="ds-head" role="banner"><div class="in">'
            f'<a class="ds-brand" href="index.html">tygif&#8217;s model<span>Week {GW} · as of {_E(_etlbl(max(g["split_utc"] for g in ALL6)))}</span></a>'
            f'<nav class="ds-nav" aria-label="Primary">{a}</nav></div></header>')
DS_FOOT=f'<footer class="ds-foot" role="contentinfo">{_E(FOOT)}</footer>'
def _ct(g):
    if g.get('ko_utc'): return _etlbl(g['ko_utc'])
    m=re.match(r'\w+ (\w+) (\d+) · (\d+:\d+) (AM|PM) ET',g.get('when',''))
    return _fmt(_to_ct(*m.groups()),', ')+' CT' if m else ''
def _logo(ab,name): 
    ab={'LA':'LAR','WAS':'WSH','JAC':'JAX'}.get(ab,ab); return f'<img src="assets/logos/{ab}.png" alt="{_E(name)} logo" width="24" height="24" loading="lazy">'
def _agree(g):
    if g.get('c') is None or g.get('agree')=='none': return '— (no DraftKings split on file)'
    src='bets %' if g.get('agree')=='DraftKings bets %' else 'money %'
    return f"DK {src}: {'same side' if g['c'] else 'opposite side'} ({AB[g['dk_side']]} {g['dk_m']}%)"
def _bneed(g):
    try: v=book_view(g)
    except Exception: v=None
    if not v: return 'Not recorded'
    return {'exposed':f"Book wants {v['fade']} · {v['pub']} has {v['money']}% of money vs {v['be']:.1f}% break-even",
            'locked':f"Balanced · {v['pub']} {v['money']}% inside {v['lock_lo']:.1f}–{v['be']:.1f}%",
            'against':f"Book wants {v['pub']} · {v['pub']} has {v['money']}% of money, under {v['lock_lo']:.1f}%"}[v['state']]
def _best(g):
    r=g['rating']; f=AB[g['fade']]; ln=g['sp'].get(f,'')
    c=ml_call(g)
    if c['play'] and (r=='PASS' or ['STRONG','LEAN'].index(c['rating'])<['STRONG','LEAN'].index(r)) :
        return f"{c['team']} ML", f"{FDN.get(c['fd'],'')} · moneyline {c['rating']}"+(f" · spread {r} {f} {ln}" if r!='PASS' else ' · no spread play')
    if r!='PASS': return f'{f} {ln}', f"{_fdl(g,f)} · fading the crowd on {AB[g['ab_side']]}"
    try: why=pass_reason(g)
    except Exception: why=f"{AB[g['ab_side']]} {g['ab_m']}% of the money · rating rules not met"
    return 'PASS — no edge', f"Fade side would be {f} {ln} ({_fdl(g,f)}) · "+why
def _mlc(g):
    c=ml_call(g)
    if not c['play']: return '—'
    return f"<span class=\"n\">{c['team']} ML</span> · {c['rating']}"
def _fdl(g,ab):
    ln=str(g['sp'].get(ab,'')).replace('−','-')
    return 'Favorite' if ln.startswith('-') else ('Underdog' if ln.startswith('+') else 'Pick')
def _res(g):
    f=g.get('final')
    if not f:
        if g['rating']=='PASS' and _gwk(g)<GW: return 'No play'+(f" · final {_E(g['score_txt'])}" if g.get('score_txt') else '')
        return 'Pending'
    return _E(re.sub(r'^Final:\s*','',f.get('tag') or f.get('word','Final')))
_PRE={(x['week'],x['game'],x['side']):x for x in json.load(open(R+'data/pregame_lines.json'))['lines']}
def _mlp(v): return '' if v is None else (f'+{v}' if v>0 else f'−{-v}')
def _sdr(g,kind):
    x=SDX.get((_gwk(g),f"{g['A']}@{g['H']}"),{}).get('fade') or {}
    rr=x.get(kind+'_res'); u=x.get(kind+'_usd')
    if not rr: return None
    return {'W':'Win','L':'Loss','P':'Push'}.get(rr,rr)+(f' {usd(u)}' if u is not None else '')
def _bk(g):
    try: v=book_view(g)
    except Exception: v=None
    if not v: return ('<div class="bk bk-na" data-state="none"><span class="bk-k">What the books need</span><span class="bk-big">Not recorded</span>'
                      '<span class="bk-sub">No DraftKings price on file for this game</span></div>')
    st=v['state']; m=v['money']; be=v['be']; lo=v['lock_lo']; d=round(m-be,1); P=v['pub']; F=v['fade']
    big={'exposed':f"Books need {F}",'locked':'Books are about even','against':f"Books want {P}"}[st]
    lead={'exposed':f"Books are overloaded on {P} — they need {F} to cover.",
          'locked':"Books are about even — they win either way, so no clear lean from the book.",
          'against':f"Books want the crowd side ({P}) — fading {P} is riskier."}[st]
    dd=f"{abs(round(d)):g}" if abs(d)>=1 else f"{abs(d):g}"
    if st=='exposed' and d<2:
        big=f"Slight lean to {F}"; lead=f"Books are only a little heavy on {P} — close to even, small lean to {F}."
    tail={'exposed':(f"So {P} is +{dd} over what the book needs — the book is rooting for {F}." if d>=2 else f"So {P} is just +{dd} over what the book needs — barely tilted toward {F}."),
          'locked':f"So {P} money ({m}%) sits in the book's safe range ({lo:.0f}–{be:.0f}%) — the book is happy with either side.",
          'against':f"So {P} is {dd} under break-even — the book is rooting for {P}, not us."}[st]
    nums=f"Public money on {P}: {m}%. Book break-even: ~{be:.0f}%. {tail}"
    pos=lambda x:max(0,min(100,(x-40)*100/40))   # bar shows 40%..80%
    return (f'<div class="bk bk-{st}" data-state="{st}"><div class="bk-l"><span class="bk-k">What the books need</span><span class="bk-big">{_E(big)}</span></div>'
            f'<div class="bk-r"><p class="bk-lead">{_E(lead)}</p><p class="bk-plain">{_E(nums)}</p>'
            f'<div class="bk-bar" role="img" aria-label="{_E(P)} money {m}% versus book break-even {be:.0f}%"><span class="bk-fill" style="width:{pos(m):.0f}%"></span>'
            f'<span class="bk-tick" style="left:{pos(be):.0f}%"></span></div>'
            f'<span class="bk-sub">Bar = {_E(P)} money · white line = book break-even</span></div></div>')
def _mlwhy(g):
    c=ml_call(g)
    if c['indep']: return c['why'] or ''
    if g['rating']=='PASS': return 'Game is PASS'
    r=ml_for(g,_gwk(g))
    if not r or r.get('price') is None: return 'No DK moneyline on file'
    if g['type']==3 and r['fd']=='Dog': return 'Type 3 underdog — ML is a pass'
    w,l,p,u,n=ml_at(g['rating'],g['type'],r['fd'],before=_gwk(g))
    return f"{g['rating']} Type {g['type']} {r['fd'].lower()} ML group {w}-{l}-{p}, {usd(u)} — not above $0"
def game_card(g):
    sr=g['rating']; t=g['type']; play,why=_best(g); m=AB[g['ab_side']]; f=AB[g['fade']]; gm=f"{g['A']}@{g['H']}"
    mc=ml_call(g); mlok=mc['play']; mt=mc['team']; mx=mc['row'] or {}
    r=sr if (sr!='PASS' and not (mlok and mc['rating']=='STRONG' and sr=='LEAN')) else (mc['rating'] if mlok else 'PASS')   # badge = best play of either market
    spres=_res(g)
    mlres=('No play' if not mlok else ((({'W':'Win','L':'Loss','P':'Push'}[mx['ml_res']]+f" {usd(mx['ml_usd'])}") if mx.get('ml_res') else None) or ('Pending' if _gwk(g)>=GW else '—')))
    mfd={'Fav':'Favorite','Dog':'Underdog'}.get(mc['fd'],'—')
    if sr!='PASS' and g.get('final') and _sdr(g,'sp'): spres=_sdr(g,'sp')
    ln=str(g['sp'].get(f,''))
    sp_call=(f'{f} {ln} ({_fdl(g,f)})' if sr!='PASS' else 'No spread play'); sp_tag=sr
    mlct=(f'{mt} ML ({mfd})' if mlok else 'No moneyline play'); ml_tag=(mc['rating'] if mlok else 'PASS')
    try: w,l,p,u,n=at(sr,t,before=_cb(g)); sgrp=(f'{w}-{l}-{p}, {usd(u)}' if n else 'no plays yet') if sr!='PASS' else '—'
    except Exception: sgrp='—'
    try: bn=bn_html(g)
    except Exception: bn=''
    dk=('—' if g.get('c') is None or g.get('agree')=='none' else ('✓ Same side' if g['c'] else '✕ Opposite side'))
    dkd=_agree(g)
    passbox=(f'<p class="gc-pass"><b>Why PASS:</b> {_E(why.split(" · ",1)[1] if " · " in why else why)} · fade side would be <b>{_E(f)} {_E(ln)}</b></p>' if r=='PASS' else f'<p class="gc-why">{_E(why)}</p>')
    return (f'<li class="gc r-{r}" id="{g["gid"]}"><article aria-labelledby="h-{g["gid"]}"><div class="gc-top">'
            f'<span class="bdg {r}" aria-label="Rating: {r}">{r}</span>'
            f'<h3 class="gc-m" id="h-{g["gid"]}">{_logo(g["A"],g["away"])}{_E(g["away"])} <span class="gc-at">at</span> {_logo(g["H"],g["home"])}{_E(g["home"])}</h3>'
            f'<span class="gc-ko"><span class="sr-only">Kickoff </span>{_E(_ct(g))}</span></div>'
            f'<p class="gc-play"><span class="sr-only">Best play: </span>{_E(play)}</p>{passbox}'
            f'<div class="bets"><div class="bt bt-sp t-{sp_tag}"><span class="bt-k">Spread</span><span class="bt-v">{_E(sp_call)}</span><span class="bt-s">{(_E(sp_tag)+" · "+spres) if sr!="PASS" else _E("PASS · fade would be "+f+" "+ln)}</span></div>'
            f'<div class="bt bt-ml t-{ml_tag}"><span class="bt-k">Moneyline</span><span class="bt-v">{_E(mlct)}</span><span class="bt-s">{_E(ml_tag+" · "+mlres) if mlok else _E("Not posted · "+_mlwhy(g))}</span></div></div>'
            f'{_bk(g)}'
            f'<div class="mo"><span><i>Money</i><b>{m} {g["ab_m"]}%</b></span><span><i>Bets</i><b>{m} {g["ab_b"]}%</b></span>'
            f'<span><i>DraftKings</i><b class="{"ok" if g.get("c") else ("no" if g.get("c") is False else "")}">{_E(dk)}</b></span><span><i>Type</i><b>{t} · {_E(TY[t]["name"])}</b></span></div>'
            f'<details class="gx gx-sp" data-kind="spread"><summary><span class="gx-k">Spread details</span><span class="gx-v">{_E(sp_call)}</span><span class="gx-r">{spres}</span></summary><dl>'
            f'<div><dt>Line</dt><dd><span class="n">{g["A"]} {_E(str(g["sp"].get(g["A"],"")))} · {g["H"]} {_E(str(g["sp"].get(g["H"],"")))}</span></dd></div>'
            f'<div><dt>Fade side</dt><dd>{f} ({_fdl(g,f)})</dd></div>'
            f'<div><dt>Type {t} {r} group</dt><dd>{_E(sgrp)}</dd></div>'
            f'<div><dt>DraftKings check</dt><dd>{_E(dkd)}</dd></div>'
            f'<div><dt>Result</dt><dd>{spres}</dd></div></dl>{bn}</details>'
            f'<details class="gx gx-ml" data-kind="moneyline" data-posted="{"yes" if mlok else "no"}"><summary><span class="gx-k">Moneyline details</span><span class="gx-v">{_E(mlct)}</span><span class="gx-r">{_E(mlres)}</span></summary><dl>'
            f'<div><dt>Side</dt><dd>{mt} ({mfd})</dd></div>'
            f'<div><dt>Moneyline rating</dt><dd>{_E(mc["raw"])}{(" · Type "+str(mc["type"])) if mc["indep"] else ""} · {_E(mc["m"]["why"] if mc["indep"] else "not graded: spread money split exactly 50–50, so no sides are tracked for this game")}</dd></div>'
            f'<div><dt>Posted</dt><dd>{("Yes — moneyline "+mc["rating"]) if mlok else "No — "+_E(_mlwhy(g))}</dd></div>'
            f'<div><dt>Result</dt><dd>{_E(mlres)}</dd></div></dl></details></article></li>')
def _rt(rt):
    w,l,p,u,n=at(rt); return f'<div><span class="ds-k">{rt} record</span><span class="ds-v">{w}-{l}-{p}<small class="{"pos" if u>0 else "neg"}">{usd(u)} · {n} plays</small></span></div>'
_cnt={k:sum(g['rating']==k for g in ALL6) for k in ('STRONG','LEAN','PASS')}
_dkbets=any(g.get('agree')=='DraftKings bets %' for g in ALL6)
HOME2=(f'<main id="main" class="ds-main" tabindex="-1"><h1>Week {GW} board</h1>'
  f'<p class="ds-sub">{len(ALL6)} games tracked · {_cnt["STRONG"]} STRONG · {_cnt["LEAN"]} LEAN · {_cnt["PASS"]} PASS · sorted by kickoff (CT)</p>'
  f'<section aria-label="Season records and data source" class="ds-strip">{_rt("STRONG")}{_rt("LEAN")}'
  f'<div><span class="ds-k">Data</span><span class="ds-v sm">As of {_E(_etlbl(max(g['split_utc'] for g in ALL6)))}</span></div>'
  f'<div><span class="ds-k">Agreement source</span><span class="ds-v sm txt">DraftKings {"bets % (handle unavailable)" if _dkbets else "money %"}</span></div></section>'
  f'<section aria-labelledby="slate"><h2 id="slate" class="ds-h2">Full slate</h2>'
  f'<p class="ds-legend">Each card: the play, then the Spread and Moneyline calls side by side (blue = spread, purple = moneyline), then what the book needs, then the money. Tap Spread details or Moneyline details for lines, groups and per-book prices. PASS cards name the fade side and why it does not qualify.</p>'
  f'<ol class="slate">{"".join(game_card(g) for g in ALL6)}</ol></section>'
  f'<details class="ds-notes"><summary>Notes</summary><ul><li>Calls before kickoff are previews and can change as the money moves. Graded at the DraftKings line, price and moneyline recorded at least 5 minutes before kickoff.</li><li>Crowd money = mean of all-books spread and moneyline money % on the money side (ScoresAndOdds).</li>'
  f'<li>STRONG and LEAN records are kept separate and never combined. Flat $100 per play.</li><li>Book needs compares all-books money to the DraftKings break-even; information only, never changes a rating.</li></ul></details>'
  f'<nav class="ds-links" aria-label="Downloads"><a href="tygif-week-{GW}-plays.txt">Week {GW} card (.txt)</a></nav></main>')
wr('index.html','<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
   f'<meta name="description" content="tygif\'s model — Week {GW} NFL board: every game rated STRONG, LEAN or PASS."><meta name="color-scheme" content="dark">'
   f'<title>tygif\'s model · Week {GW}</title>{DS_CSS}</head><body>{ds_head("index")}{HOME2}{DS_FOOT}</body></html>\n')
# history: every earlier week in the same uniform card layout
_HW=[(w,sorted(GBY[w],key=_kick)) for w in reversed(LIVEW) if w!=GW]+[(5,sorted(G,key=_kick))]+[(w,sorted([g for g in G14 if g['week']==w],key=_kick)) for w in (4,3,2,1)]
_hb=''
for _w,_gs in _HW:
    _cards=[]
    for _g in _gs:
        try: _cards.append(game_card(_g))
        except Exception as _e: import traceback; print('history card skipped',_w,_g.get('gid'),repr(_e),traceback.format_exc().splitlines()[-3])
    _c={k:sum(g['rating']==k for g in _gs) for k in ('STRONG','LEAN','PASS')}
    _hb+=(f'<section aria-labelledby="hw{_w}" id="w{_w}"><h2 id="hw{_w}" class="ds-h2">Week {_w}</h2>'
          f'<p class="ds-legend">{len(_gs)} games · {_c["STRONG"]} STRONG · {_c["LEAN"]} LEAN · {_c["PASS"]} PASS</p><ol class="slate">{"".join(_cards)}</ol></section>')
_jump='<nav class="ds-legend" aria-label="Jump to week">'+' · '.join(f'<a href="#w{w}">Week {w}</a>' for w,_ in _HW)+'</nav>'
wr('tygif-history.html','<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark">'
   f"<title>tygif's model · Past weeks</title>{DS_CSS}</head><body>{ds_head('history')}<main id=\"main\" class=\"ds-main\" tabindex=\"-1\"><h1>Past weeks</h1>{_jump}"
   f'<p class="ds-sub">Every game from Weeks 1–{GW-1} in the same card layout as the current board. Weeks 1–4: all-books splits only; DraftKings split not recorded.</p>{_hb}</main>{DS_FOOT}</body></html>\n')
# re-skin every other generated page: shared header, skip link, design-system CSS (appended last so it wins)
_CUR={'tygif-tracker.html':'results','tygif-how.html':'how'}
_TTL={'tygif-tracker.html':'Records','tygif-angles.html':'Angles','tygif-games-archive.html':'Games archive','tygif-deep-dive.html':'Game by game','tygif.html':'Week card','tygif-week-5-report.html':'Week 5 report'}
_STUB={'tygif.html':('Week card','This page moved. <a href="index.html">Go there now</a>.'),
       'tygif-week-5-report.html':('Week 5 report','The Week 5 report moved. <a href="tygif-tracker.html#results">Go there now</a>.')}
def _strip_skin(_x):
    _x=re.sub(r'<style id="ds">.*?</style>','',_x,flags=re.S)
    _x=re.sub(r'<a class="skip".*?</header>','',_x,flags=re.S)
    _x=re.sub(r'<header class="ds-head".*?</header>','',_x,flags=re.S)
    _x=re.sub(r'<footer class="ds-foot".*?</footer>','',_x,flags=re.S)
    return _x
for _f in _gg.glob(R+'*.html'):
    _b=os.path.basename(_f)
    if _b in ('index.html','tygif-history.html'): continue
    if _b in _STUB:
        _ti,_msg=_STUB[_b]
        wr(_b,'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark">'
           f"<title>tygif's model · {_ti}</title>{DS_CSS}</head><body>{ds_head('')}<main id=\"main\" class=\"ds-main\" tabindex=\"-1\"><h1 class=\"ds-pt\">{_ti}</h1><p>{_msg}</p></main>{DS_FOOT}</body></html>\n")
        continue
    _x=_strip_skin(open(_f,encoding='utf-8').read())
    _x=_x.replace('</head>',DS_CSS+'</head>',1)
    _x=re.sub(r'(<body[^>]*>)',lambda m:m.group(1)+ds_head(_CUR.get(_b,'')),_x,count=1)
    if 'id="main"' not in _x: _x=re.sub(r'<main(?![^>]*id=)',r'<main id="main" tabindex="-1"',_x,count=1)
    if 'id="main"' not in _x: _x=_x.replace(ds_head(_CUR.get(_b,'')),ds_head(_CUR.get(_b,''))+'<div id="main" tabindex="-1"></div>',1)
    for _a,_c in (('Tracking · not a play · ','Tracking · '),('tracking · not a play','tracking only'),(' · not a play',''),('not a play','tracking only')): _x=_x.replace(_a,_c)
    if '<h1' not in _x and _b in _TTL: _x=re.sub(r'(<main[^>]*>|<div id="main" tabindex="-1"></div>)',lambda m:m.group(1)+f'<h1 class="ds-pt">{_TTL[_b]}</h1>',_x,count=1)
    if _b=='tygif-how.html':
        _ol='<ol>'+''.join(f'<li value="{k}"><b>Type {k} · {TY[k]["name"]}:</b> '+_d+'</li>' for k,_d in ((1,'65%+ of the money on a favorite giving 6+ points. Take the underdog.'),(2,'65%+ of the money and most bets on one team. Take the other team.'),(3,'55–64% of the money on one team. LEAN at most; money and bets on different teams is a pass. Type 3 underdog: pass on the moneyline; spread unaffected.'),(4,'all books and DraftKings have the money on different teams. PASS.'),(5,'under 55% of the money on either team. PASS.')))+'</ol>'
        _x=re.sub(r'(<h2>Game types</h2>\s*<p[^>]*>[^<]*</p>\s*)<ol>.*?</ol>',lambda m:m.group(1)+_ol,_x,count=1,flags=re.S)
        _x=_x.replace('<li>Weeks 1–4: all-books splits only','<li>Every game is graded at the DraftKings line, price and moneyline we recorded last at least 5 minutes before kickoff; where nothing was recorded, at the DraftKings closing numbers.</li><li>Weeks 1–4: all-books splits only',1)
    _x=re.sub(r'<img((?![^>]*alt=)[^>]*)>',r'<img alt=""\1>',_x)
    if '<html>' in _x: _x=_x.replace('<html>','<html lang="en">',1)
    _x=_x.replace('</body>',DS_FOOT+'</body>',1) if 'ds-foot' not in _x else _x
    wr(_b,_x)
print('premium skin ok:',len(ALL6),'games',_cnt)
# Records hub (Oct 29): every graded game's best-play side, by Type 1-5 x rating x Favorite/Underdog; spread, ML posted, and no-ML-play buckets
def _gcall(k):
    o=SDX.get(k,{}); f=o.get('fade'); sp=bool(f and _ours(f)); mr=next((x for x in o.values() if ml_post(x)),None)
    g=_gk(*k); c=ml_call(g) if g is not None else None
    return f,sp,mr,c
def _bucket(k):
    f,sp,mr,c=_gcall(k)
    return 'Both' if (sp and mr) else ('Moneyline only' if mr else ('Spread only' if sp else 'PASS'))
_BK=('Spread only','Moneyline only','Both','PASS')
_BKD={'Spread only':'Spread is the play; moneyline PASS.','Moneyline only':'Moneyline is the play; spread PASS.','Both':'Spread and moneyline both played.','PASS':'Both markets PASS; tracked side graded on spread and moneyline.'}
def _rec(rs,k):
    rs=[r for r in rs if r and r[k+'_res']]
    if not rs: return '—'
    w=sum(r[k+'_res']=='W' for r in rs);l=sum(r[k+'_res']=='L' for r in rs);p=sum(r[k+'_res']=='P' for r in rs);u=sum(r[k+'_usd'] or 0 for r in rs)
    return f'{w}-{l}-{p} <small class="{"pos" if u>0 else ("neg" if u<0 else "")}">{usd(u)}</small>'
HUBN={}
def _hub():
    ks=sorted({(x['week'],x['game']) for x in SIDES if x['role']=='fade' and (x['sp_res'] or x['ml_res'])})
    _FLAGS=[f for f in json.load(open(R+'data/sides_log.json'))['flags']]
    rr=lambda r,u: '—' if not r else f'<span class="{dict(W="pos",L="neg",P="")[r]}">{dict(W="Win",L="Loss",P="Push")[r]} {usd(u or 0)}</span>'
    FD=lambda v:{'Fav':'Favorite','Dog':'Underdog'}.get(v,'—')
    summ='';det=''
    for bk in _BK:
        g=[k for k in ks if _bucket(k)==bk]; HUBN[bk]=len(g)
        sprs=[_gcall(k)[0] for k in g]; mlrs=[(_gcall(k)[2] or _gcall(k)[0]) for k in g]
        summ+=f'<tr><th scope="row">{bk}</th><td>{len(g)+(len(_FLAGS) if bk=="PASS" else 0)}</td><td>{_rec(sprs,"sp") if bk!="Moneyline only" else "—"}</td><td>{_rec(mlrs,"ml") if bk!="Spread only" else "—"}</td><td>{_BKD[bk]}</td></tr>'
        rows=''
        for k in g:
            f,sp,mr,c=_gcall(k); mrow=mr or f
            mrt=(c['raw'] if c else f['rating']); mty=(c['type'] if c else f['type'])
            rows+=(f'<tr><td>{k[0]}</td><td>{k[1].replace("@"," at ")}</td>'
                   f'<td>{f["team"]} · {f["rating"]} · Type {f["type"]} · {FD(f["fd"])}</td><td>{rr(f["sp_res"],f["sp_usd"]) if bk!="Moneyline only" else ("Tracked: "+rr(f["sp_res"],f["sp_usd"]))}</td>'
                   f'<td>{mrow["team"]} · {mrt} · Type {mty} · {FD(mrow["fd"])}{"" if (c and c["indep"]) else " · as posted"}</td><td>{rr(mrow["ml_res"],mrow["ml_usd"]) if bk!="Spread only" else ("Tracked: "+rr(mrow["ml_res"],mrow["ml_usd"]))}</td></tr>')
        if bk=='PASS':
            rows+=''.join(f'<tr><td>{w}</td><td>{gm.replace("@"," at ")}</td><td colspan="4">No side: money split 50–50, nothing to track</td></tr>' for w,gm,_ in _FLAGS)
        nn=len(g)+(len(_FLAGS) if bk=='PASS' else 0)
        det+=(f'<details class="gx" id="hub-{bk.split()[0].lower()}"><summary>{bk} · {nn} games</summary>'
              + (f'<div class="tblwrap"><table class="data"><thead><tr><th scope="col">Week</th><th scope="col">Game</th><th scope="col">Spread: side · rating · type · Fav/Dog</th><th scope="col">Spread result</th><th scope="col">Moneyline: side · rating · type · Fav/Dog</th><th scope="col">Moneyline result</th></tr></thead><tbody>{rows}</tbody></table></div>' if nn else '<p class="ds-legend">No graded games in this bucket yet.</p>')
              +'</details>')
    n=len(ks)+len(_FLAGS)
    return ('<section id="hub" aria-labelledby="hubh"><h2 id="hubh" class="ds-h2">Season records</h2>'
            f'<p class="ds-legend">All {n} graded games, each in exactly one bucket. Spread and moneyline are rated separately (STRONG 65%+, LEAN 55–64%, PASS under 55% or DraftKings disagrees or bets under 50%). Moneyline is rated on its own wherever a moneyline money split is on file (late Week 7 on); earlier games keep their as-posted moneyline call. Flat $100 per play.</p>'
            '<div class="tblwrap"><table class="data"><thead><tr><th scope="col">Bucket</th><th scope="col">Games</th><th scope="col">Spread record</th><th scope="col">Moneyline record</th><th scope="col">Meaning</th></tr></thead>'
            f'<tbody>{summ}</tbody></table></div>{det}</section>')
_tf=R+'tygif-tracker.html'; _x=open(_tf,encoding='utf-8').read()
_x=re.sub(r'<section id="hub".*?</section>','',_x,flags=re.S)
_x=re.sub(r'(<h1 class="ds-pt">Records</h1>)',lambda m:m.group(1)+_hub(),_x,count=1)
_x=_x.replace('<div class="gt-row"><b class="none">PASS: see Side groups</b></div>','<div class="gt-row"><b class="none">PASS type — records in Season records (top of page)</b></div>')
wr('tygif-tracker.html',_x)
