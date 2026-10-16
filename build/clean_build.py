import os as _P_os
_B=_P_os.path.dirname(_P_os.path.abspath(__file__)); _I=_B+'/inputs'; _W=_P_os.environ.get('TYGIF_WORK',_B+'/raw'); _RR=_P_os.path.dirname(_B)+'/'
from decimal import Decimal as _Dec, ROUND_HALF_UP as _RHU
import builtins as _bi
def r0(x): return int(_Dec(str(x)).quantize(_Dec('1'),_RHU))
def round(x,n=None): return r0(x) if n is None else _bi.round(x,n)   # half-up everywhere (TG, Oct 15)
import re, sys, json, html, os
from zoneinfo import ZoneInfo
sys.path.insert(0,_B)
from clean_data import *
from bs4 import BeautifulSoup
for _k in T: T[_k]['usd']=float(round(T[_k]['usd']))   # each play rounded to whole dollars once; all sums use these
R=_RR
import slight_grade as _sg0; _sg0.set_root(R)   # grader reads R/data/pregame_lines.json
import subprocess
PROCESS=json.load(open(R+'data/process.json'))
_S=PROCESS['sources']; _K=PROCESS['known_gaps']
SRC_STD={k:v for k,v in _S.items()}
SRC_W14=dict(SRC_STD,splits_consensus=_K['weeks_1_4']['splits_consensus'],splits_draftkings=_K['weeks_1_4']['splits_draftkings'])
def rd(f): return subprocess.run(['git','-C',R,'show','24b4216:'+f],capture_output=True,text=True,check=True).stdout
def wr(f,s): open(R+f,'w',encoding='utf-8').write(s)

def LOGO(ab,cls='lg'):
    ab={'LA':'LAR','WAS':'WSH','JAC':'JAX'}.get(ab,ab)
    return f'<img class="{cls}" src="assets/logos/{ab}.png" alt="" loading="lazy">'
def nav(cur, tracker=False):
    items=[('index','index.html','Home'),('week','tygif-tracker.html#week','This Week'),('results','tygif-tracker.html#results','Records'),('how','tygif-how.html','How')]
    out=[]
    for k,h,t in items:
        if tracker and k in('week','results'): h='#'+k
        c='tab'+(' cur' if (k==cur and not tracker) else '')
        out.append(f'<a class="{c}" href="{h}" data-tab="{k}">{t}</a>')
    return '<nav class="tabs" aria-label="Sections"><div class="tabs-in">'+''.join(out)+'</div></nav>'
NAVRE=re.compile(r'<nav[^>]*class="tabs"[^>]*>.*?</nav>|<nav[^>]*aria-label="Sections"[^>]*>.*?</nav>',re.S)

FOOT="tygif's model · free public data · records use flat $100 bets · small samples, no guarantees · not financial advice" #  small samples, no guarantees · not financial advice"
TUE="Calls posted Tuesday to Saturday can change as the money moves; only the Saturday call counts."
GRADE="Every week is rated on the money splits (all books and DraftKings) from the last pull before kickoff and graded at the DraftKings line, price and moneyline recorded before kickoff."
LOCK2="Calls posted before kickoff are previews and can change as the money moves. "+GRADE
OLDNAMES={1:TY[1]['name'],2:TY[2]['name']}
for _t,_n in ((1,'Fade the big favorite'),(2,'Fade the crowd')): TY[_t]=dict(TY[_t]); TY[_t]['name']=_n
TY[3]=dict(TY[3]); TY[3]['rule']=TY[3]['rule']+'; a money-vs-bets split is a pass'
import csv as _csv
def live_rows():
    p=R+'data/live_log.csv'
    if not os.path.exists(p): return []
    return list(_csv.DictReader(open(p)))
def live_profit(r):
    res=(r.get('result') or '').strip().upper()[:1]
    if res=='L': return -100.0
    if res=='P': return 0.0
    if res=='W':
        pr=float(r['closing_price']); return float(round(100*100/abs(pr) if pr<0 else pr))
    return None
PULL="Sat Oct 10, 8:49 PM ET"   # scripts/snapshot.py pull, 00:49 UTC Oct 11 (snap_w5_20261010_1949)
PULL_SHORT="Sat 8:49 PM ET"
SRC=f"Pulled {PULL} · splits: all books (ScoresAndOdds) and DraftKings · lines: DraftKings · they move until kickoff"
PRICE={'tbdal-card':'−112','g-mia':'−115','g-nyj':'−110','g-wsh':'−115'}
TUESDAY={}
def EVEN(g): return g['ab_m']==50 and g['type']==5
EVENTXT=lambda g:f"the money is split exactly 50–50 on all books, so no side holds it (DraftKings {g['dk_m']}% on {g['dk_side']})"

EXTRA_CSS = r'''
#week .fold.passes{margin:22px 0 8px;border-top:1px solid var(--line)}
#week .fold.passes>summary{padding:14px 2px;cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:baseline}
#week .fold.passes>summary::-webkit-details-marker{display:none}
#week .fold.passes .ft{font-weight:700;font-size:16px}
#week .fold.passes .fs{color:var(--mut);font-size:13px}
.g-final{display:block;font-size:13px;font-weight:700;color:var(--pos);margin:2px 0}

#results .rgrid.tiers{grid-template-columns:1fr;gap:0;margin:0 0 8px}
#results .rc{background:transparent;border:0;border-bottom:1px solid var(--line);padding:20px 2px 18px}
#results .rc.tier-s .rc-r,#results .rc.tier-l .rc-r{font-size:23px;font-weight:800;letter-spacing:-.4px;line-height:1.15;margin:8px 0 6px;white-space:nowrap}
#results .rc.tier-l{padding:20px 2px 18px}
#results .rc-m{font-size:15px}
#results .sh{margin:28px 0 8px}
#results .live{background:transparent;border:0;padding:0;margin:0}
#results .lv{display:flex;align-items:baseline;gap:10px;padding:4px 0 8px;font-size:16px}
#results .lv b{font-weight:700}
#results .lv em{margin-left:auto;font-style:normal;color:var(--mut);font-size:14px;text-align:right}
#results .lsum{font-size:15px;font-weight:650;margin:0 0 8px}
#results .beat{color:var(--mut);font-size:13px;margin:0 0 4px}
#results .tb{background:transparent;border:0;border-top:1px solid var(--line);padding:14px 0 6px;margin:0}
#results .tb-h{align-items:center;margin-bottom:2px}
#results .tb-h b{font-size:16px}
#results .tcard{margin:0 0 4px}
#results .tblwrap{border:0;background:transparent}
#results table.data th,#results table.data td:first-child,#results table.data th:first-child{background:transparent;box-shadow:none;border-right:0}
#results table.data th{padding-left:2px}
#results table.data td{padding-left:2px}
#results .allg{margin:18px 0 4px;font-size:15px;display:flex;flex-wrap:wrap;gap:10px 22px}
#results .allg a{color:var(--accent);font-weight:650;text-decoration:none;border-bottom:1px solid rgba(212,160,23,.4)}
#results .fine{margin:28px 0 8px}
#results .fine>summary{cursor:pointer;list-style:none;font-size:15px;font-weight:650;padding:16px 0;border-top:1px solid var(--line)}
#results .fine>summary::-webkit-details-marker{display:none}
#results .fine>summary::after{content:" +";color:var(--mut);font-weight:500}
#results .fine[open]>summary::after{content:" −"}
#results .fine .rules{background:transparent;border:0;padding:4px 0 0;margin:0}
#results .fine h4{font-size:12px;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin:18px 0 8px;font-weight:700}
#results .fine p{font-size:14px;color:#c8c6c0;line-height:1.5;margin:10px 0}
#results .sec-h{margin-bottom:2px}
#results .sub{max-width:38em}
.rules{background:var(--card);border:1px solid var(--accent);padding:12px 14px;margin:12px 0}
.rules-k{font-size:12px;font-weight:800;letter-spacing:.1em;text-transform:uppercase;color:var(--accent);margin-bottom:6px}
.rules p{font-size:13px;line-height:1.45;margin:6px 0} .rules ul{list-style:none;margin:6px 0;padding:0}
.rules li{font-size:13px;line-height:1.45;padding:5px 0;border-top:1px solid var(--line)} .rules li .tg{font-size:12px;margin-right:6px}
.rgt{flex-basis:100%;font-size:12px;color:var(--mut);margin-top:2px}
.rgt>summary{cursor:pointer;list-style:none;display:inline-block;font-size:12px;color:var(--mut);border-bottom:1px dotted var(--mut)}
.rgt>summary::-webkit-details-marker{display:none}
.rgt p{margin:4px 0 0;font-size:12px;color:var(--mut);line-height:1.4}
.tb-l li{flex-wrap:wrap}
.fn{margin-top:4px;font-size:13px;color:var(--mut)} .fn>summary{cursor:pointer;color:var(--accent);font-size:13px}
.live .gt-row{font-size:14px}
table.wk3 td small{color:var(--mut)}
.tbdc .uc-yn.na{color:var(--mut);background:rgba(154,157,164,.14)}
.tbdc .uc-yn.na i{background:transparent;color:var(--mut);font-size:14px}
.gt-rec2{margin-top:12px;padding-top:10px;border-top:1px solid var(--line)}
.gt-rk{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--mut);margin-bottom:4px}
.gt-row{display:flex;align-items:baseline;gap:8px;font-size:14px;padding:4px 0}
.gt-row .tg{flex:0 0 62px;font-size:12px;font-weight:800;letter-spacing:.06em}
.tg.STRONG{color:var(--strong)} .tg.LEAN{color:var(--lean)} .tg.PASS{color:var(--pass)}
.gt-row b{font-weight:650;color:var(--txt)} .gt-row .none{color:var(--mut);font-weight:500}
.gt-row em{font-style:normal;margin-left:auto;font-weight:700;white-space:nowrap}
.gt-link{display:inline-block;margin-top:8px;font-size:13px;font-weight:650;color:var(--accent);text-decoration:none;border-bottom:1px solid rgba(212,160,23,.4)}
.pos{color:var(--pos)} .neg{color:var(--neg)}
.lockline{background:var(--card);border-left:3px solid var(--accent);padding:10px 12px;margin:10px 0 16px;font-size:13px;line-height:1.45;color:var(--txt)}
.lockline span{display:block;color:var(--mut);margin-top:4px}
.plist{border:1px solid var(--line);background:var(--card);margin:8px 0 12px}
details.pr{border-bottom:1px solid var(--line)} details.pr:last-child{border-bottom:0}
details.pr>summary{display:flex;align-items:center;gap:10px;padding:10px 14px;list-style:none;cursor:pointer;min-height:44px;font-size:14px}
details.pr>summary::-webkit-details-marker{display:none}
details.pr>summary::after{content:"+";margin-left:auto;color:var(--mut);font-size:18px;line-height:1;padding-left:6px}
details.pr[open]>summary::after{content:"\2212"}
.pr-badge{flex:0 0 auto;font-size:12px;font-weight:800;letter-spacing:.06em;color:var(--pass);border:1px solid var(--pass);padding:2px 5px}
.pr-m{font-weight:700;white-space:nowrap}
.pr-t{color:var(--mut);font-size:12px;font-weight:700;letter-spacing:.04em;border:1px solid var(--line);padding:1px 6px;white-space:nowrap}
details.pr>summary{flex-wrap:wrap;row-gap:4px}
.pr-r span{white-space:nowrap}
.pr-r{order:5;flex:1 0 100%;font-size:12.5px;letter-spacing:-.1px;color:var(--txt);line-height:1.35;padding-left:0}
.pr-b{padding:0 14px 14px}
.pr-b .tbdc{padding:0;border:0;background:transparent}
.pr-meta{font-size:13px;color:var(--mut);margin:0 0 6px}
.pr-note{font-size:13px;color:var(--txt);margin:0 0 6px}
.sh{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:var(--accent);margin:22px 0 6px;font-weight:700}
.tb{background:var(--card);border:1px solid var(--line);padding:12px 14px;margin:8px 0;scroll-margin-top:64px}
.tb-h{display:flex;gap:10px;align-items:flex-start;margin-bottom:6px}
.tbn{flex:0 0 26px;height:26px;display:inline-flex;align-items:center;justify-content:center;border:1px solid var(--accent);color:var(--accent);font-weight:800;font-size:13px}
.tb-h b{display:block;font-size:15px;line-height:1.3} .tb-h .r{display:block;font-size:12.5px;color:var(--mut);line-height:1.35;margin-top:2px}
.tb-l>summary{font-size:13px;color:var(--accent);font-weight:650;cursor:pointer;padding:8px 0 2px}
.tb-l ul{list-style:none;margin:6px 0 0;padding:0}
.tb-l li{display:flex;justify-content:space-between;align-items:baseline;gap:8px;font-size:13px;padding:7px 0;border-top:1px solid var(--line)}
.tb-l li .w{color:var(--mut);white-space:nowrap} .tb-l li .w i{font-style:normal;font-weight:800;font-size:12px;margin-left:6px}
.tb-l li .w i.STRONG{color:var(--strong)} .tb-l li .w i.LEAN{color:var(--lean)}
.tb-l li b{white-space:nowrap;font-weight:650} .tb-l li small{display:block;font-size:12px;color:var(--mut);font-weight:400;text-align:right}
table.wk3 td,table.wk3 th{white-space:normal} table.wk3 td{font-size:13px;line-height:1.35} table.wk3 td small{display:block;font-size:12px}
.lk{display:grid;gap:8px;margin:18px 0}
.lk a{display:flex;justify-content:space-between;align-items:center;gap:10px;background:var(--card);border:1px solid var(--line);padding:12px 14px;color:var(--txt);text-decoration:none;font-weight:650;font-size:15px}
.lk a span{color:var(--mut);font-weight:500;font-size:13px}
.rgnote{font-size:12.5px;color:var(--mut);line-height:1.5;margin:10px 0}
.dg{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--pass);padding:12px 14px;margin:8px 0}
.dg.s-STRONG{border-left-color:var(--strong)} .dg.s-LEAN{border-left-color:var(--lean)}
.dg-top{display:flex;justify-content:space-between;gap:8px;align-items:baseline;flex-wrap:wrap}
.dg-mu{font-weight:750;font-size:15px} .dg-ko{font-size:12px;color:var(--mut)}
.dg-ch{display:flex;gap:6px;flex-wrap:wrap;margin:6px 0}
.chip{font-size:12px;font-weight:700;padding:2px 8px;border:1px solid var(--line);color:var(--mut)}
.chip.STRONG{color:var(--strong);border-color:var(--strong)} .chip.LEAN{color:var(--lean);border-color:var(--lean)}
.chip.W{color:var(--pos)} .chip.L{color:var(--neg)}
.dg p{font-size:14px;margin:6px 0;line-height:1.5}
.dg p.rg{font-size:12.5px;color:var(--mut)}
.dg-g{display:grid;grid-template-columns:1fr 1fr;gap:8px 12px;font-size:13.5px;margin-top:8px;padding-top:8px;border-top:1px solid var(--line)}
.dg-g span{display:block;font-size:12px;color:var(--mut);text-transform:uppercase;letter-spacing:.06em}
.hw{padding:0 0 10px}
.hw h1{font-family:Georgia,"Times New Roman",serif;font-size:28px;margin:18px 0 6px}
.hw h2{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:var(--accent);margin:24px 0 8px}
.hw p,.hw li{font-size:15px;line-height:1.55} .hw ol,.hw ul{padding-left:20px;margin:6px 0}
.hw li{margin:4px 0} .hw .sm{font-size:13px;color:var(--mut)}
.hw .pills{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0}
.hw .pills span{font-size:12px;font-weight:800;letter-spacing:.06em;padding:3px 8px;border:1px solid}
'''

# ---------- week 5 ----------
def fav_of(g):
    for a,v in g['sp'].items():
        if v.startswith(M): return a,v
    return None,None
def opener(g):
    # Monday line = TeamRankings books 2-3, last quote before Monday 12:00 AM ET (see tr_monday.py)
    m=g['mon']; t=m['team']; now=g['sp'][t]
    f=lambda v:('PK' if v==0 else f"{v:+g}".replace('-',M))
    if m['b2']==m['b3']: return f"Start-of-week line {t} {f(m['b2'])}, now {now}"
    return f"Start-of-week line {t} {f(m['b2'])} / {f(m['b3'])} (avg {f(m['avg'])}), now {now}"
old=BeautifulSoup(rd('tygif-tracker.html'),'html.parser')
FNOTE={}
for gm in old.find(id='week').find_all('details',class_='gm'):
    rows=gm.select('.uc-r'); FNOTE[gm['id']]=rows[-1].select_one('.uc-n').get_text()
def _dir(g):
    m=g['mon']; t=m['team']; d=float(g['sp'][t].replace(M,'-').replace('PK','0'))-m['avg']
    if abs(d)<0.01: return ''
    to=t if d<0 else _other(g,t); A=AB[g['ab_side']]
    return f"; moved {abs(d):g} pt{'s' if abs(d)!=1 else ''} toward {to}"+('' if to==A else ', away from the money')
def pill(ans,eff):
    # ans: True/False answer to the question; eff: 'ok' helps, 'no' hurts, 'nu' sets the type only, 'na' not recorded
    if eff=='na': return '<span class="uc-yn nu">—</span>'
    return f'<span class="uc-yn {eff}"><i>{"✓" if eff=="ok" else ("✕" if eff=="no" else "–")}</i>{"Yes" if ans else "No"}</span>'
def _other(g,a): return [x for x in (g['A'],g['H']) if x!=a][0]
def qa(g):
    """Plain yes/no answers with real numbers. Returns list of (letter, question, answer_bool, detail, effect)."""
    A=AB[g['ab_side']]; D=AB.get(g['dk_side']); m=g['ab_m']; bb=g['ab_b']; fa,fl=fav_of(g)
    even=m<=50
    cl=(' '+g.get('clbl',CLBL)) if g.get('split_at')=='closing' else ''
    rows=[]
    # a: bets agree with money
    if even: da=f"Money is split 50–50 ({A} {m}%), so there is no money side; {A} has {bb}% of the bets{cl}"
    elif bb==50: da=f"{A} has {m}% of the money; the bets are split exactly 50–50{cl}"
    elif g['a']: da=f"{A} has {m}% of the money and {bb}% of the bets{cl}"
    else: da=f"{A} has {m}% of the money but only {bb}% of the bets; {_other(g,A)} has {100-bb}%{cl}"
    rows.append(('a','Are the money and the bets on the same team?',g['a'],da,'ok' if g['a'] else 'no'))
    # b: 65%+
    if g['b']: db=f"{A} has {m}%"
    elif even: db=f"50–50 split; under 55% is a pass"
    elif m<55: db=f"{A} has {m}%; under 55% is a pass"
    else: db=f"{A} has {m}%; 55–64% is LEAN at most"
    rows.append(('b','Does one team have 65% or more of the money?',g['b'],db,'ok' if g['b'] else 'no'))
    # c: DraftKings same side
    dkn=f" ({g['dk_note_short']})" if g.get('dk_note_short') else ''
    if g['c'] is None: dc="Not recorded for Weeks 1–4"
    elif even: dc=f"All books are split 50–50, so there is no money side to match; DraftKings has {D} {g['dk_m']}%"
    elif g['c']: dc=f"DraftKings has {D} {g['dk_m']}%{dkn}"
    else: dc=f"DraftKings has {D} {g['dk_m']}%, all books have {A} {m}%"
    rows.append(('c','Does DraftKings have the money on the same team?',bool(g['c']) and not even,dc,'na' if g['c'] is None else ('ok' if (g['c'] and not even) else 'no')))
    # d: 6+ favorite holds the money
    big = fa is not None and abs(float(fl.replace(M,'-')))>=6
    yes_d = big and fa==A and not even
    assert yes_d==bool(g['d']), (g['gid'],'check d disagrees with data')
    if yes_d: dd=f"{fa} {fl} holds {m}%"+('' if g['b'] else '; type 1 also needs 65%+')
    elif fa is None: dd="Pick’em, no favorite"
    elif not big: dd=f"The favorite, {fa} {fl}, is giving under 6"
    else: dd=f"{fa} {fl} is the favorite, but the money is on {_other(g,fa)}"
    rows.append(('d','Is the favorite giving 6+ points holding the money?',yes_d,dd+'. This only picks the type, not the rating','nu'))
    # e: line steady (yes helps)
    EQ='Has the line moved 1 point or less toward the money since Monday?'
    if even: rows.append(('e',EQ,True,"money is split 50–50, so there's no money side for the line to move toward.",'ok'))
    else: rows.append(('e',EQ,not g['e'],opener(g)+_dir(g),'ok' if not g['e'] else 'no'))
    rows=[(l,t,v,(d[0].lower()+d[1:] if d.split()[0] in ('Money','All','The','Start-of-week') else d),e) for l,t,v,d,e in rows]
    # consistency: rebuild rating and type from the answers
    ans={l:v for l,_,v,_,_ in rows}
    if g['c'] is not None and not g['c'] and not even: rt,ty='PASS',4
    elif m<55: rt,ty='PASS',5
    else:
        ty=1 if (ans['b'] and ans['d']) else 2 if (ans['b'] and ans['a']) else 3
        if not ans['a']: rt='PASS'
        else:
            lvl=(2 if ans['b'] else 1)-(not ans['e']); rt=['PASS','LEAN','STRONG'][max(lvl,0)]
    assert (rt,ty)==(g['rating'],g['type']), (g['gid'],rt,ty,g['rating'],g['type'])
    # d (6+ favorite) only decides type 1 vs 2 and is shown on the card as the type; not a checklist row
    shown=[r for r in rows if r[0]!='d']
    return [('abcde'[i],)+r[1:] for i,r in enumerate(shown)]
def checks(g):
    h='<div class="tbdc-h uc-h">Rating checklist<span class="uc-key">✓ Favorable · ✕ Unfavorable</span></div><div class="uc">'
    for l,t,v,n,eff in qa(g):
        h+=f'<div class="uc-r"><span class="uc-l">{l}</span><div class="uc-t">{t}<span class="uc-n">{E(n) if eff=="na" else ("Yes" if v else "No")+": "+E(n)}</span></div>{pill(v,"na" if eff=="na" else ("ok" if v else "no"))}</div>'
    h+=f'</div><div class="uc-res"><span>{E(g["why"])}</span><b class="rb {g["rating"]}">{g["rating"]}</b></div>'
    return h
def type_keys(t,rt=None):
    ks=[k for k in sorted(CARD,key=lambda k:(k[0],k[1])) if T[k]['type']==t and (rt is None or CARD[k]['rating']==rt)]
    return ks
def type_rows(t, cur=None):
    out=''
    for rt in ('STRONG','LEAN'):
        ks=type_keys(t,rt)
        if ks:
            w,l,p,u,n=tally(ks); cls='pos' if u>0 else ('neg' if u<0 else '')
            out+=f'<div class="gt-row"><span class="tg {rt}">{rt}</span><b>{rec(w,l,p)}</b><em class="{cls}">{usd(u)}</em></div>'
        elif t==3 and rt=='STRONG':
            out+=f'<div class="gt-row"><span class="tg STRONG">STRONG</span><b class="none">none · this type is LEAN at most</b></div>'
        elif t in (4,5):
            out+=f'<div class="gt-row"><span class="tg {rt}">{rt}</span><b class="none">no plays yet · PASS sides in Side groups</b></div>'
        elif cur==rt:
            out+=f'<div class="gt-row"><span class="tg {rt}">{rt}</span><b class="none">first {rt} of this type</b></div>'
        else:
            out+=f'<div class="gt-row"><span class="tg {rt}">{rt}</span><b class="none">none · no {rt} plays of this type yet</b></div>'
    return out
def type_rows_compact(t):
    out=''
    for rt in ('STRONG','LEAN'):
        ks=type_keys(t,rt)
        if ks:
            w,l,p,u,n=tally(ks); cls='pos' if u>0 else ('neg' if u<0 else '')
            out+=f'<div class="gt-row"><span class="tg {rt}">{rt}</span><b>{rec(w,l,p)}</b><em class="{cls}">{usd(u)}</em></div>'
    if t in (4,5): out+='<div class="gt-row"><b class="none">PASS: see Side groups</b></div>'
    return out
def type_box(t, link, cur=None):
    n=len(type_keys(t))
    lk=f'<a class="gt-link" href="{link}">See {"these "+str(n)+" plays" if n else "this type"} on Records ›</a>'
    return (f'<div class="gt t{t}"><div class="gt-top"><span class="gt-n">{t}</span><div><div class="gt-k">Game type</div>'
            f'<div class="gt-name">{TY[t]["name"]}</div><div class="gt-rule">{TY[t]["rule"]}</div></div></div>'
            f'<div class="gt-rec2"><div class="gt-rk">Our plays of this type · Weeks 1–4</div>{type_rows(t,cur)}{lk}</div></div>')
def matchup(g):
    side=g.get('fade'); A,H=g['A'],g['H']
    def tm(a,right):
        on=' on' if NAME.get(a)==side and g['rating']!='PASS' else ''
        return f'<div class="tbdc-tm{on}{" r" if right else ""}">{LOGO(a,"tlg")}<div class="tbdc-ab">{a}</div><div class="tbdc-nm">{NICK[a]}</div><div class="tbdc-sp">{g["sp"][a]}</div></div>'
    return f'<div class="tbdc-match">{tm(A,False)}<div class="tbdc-at">@</div>{tm(H,True)}</div>'
# ---------- catchup1: settle Week 5 at the close (Rules v1) ----------
import glob as _g0, datetime as _dt, csv as _c0
_NK={v:k for k,v in NICK.items()}
_SAOAB={'JAC':'JAX','WAS':'WSH','LA':'LAR'}
_ET=lambda iso:_dt.datetime.fromisoformat(iso.replace('Z','+00:00')).astimezone(ZoneInfo('America/Chicago'))   # UTC straight to Central for display
def _posted_ct(s_):
    t=_dt.datetime.strptime(s_,'%Y-%m-%d %I:%M %p').replace(tzinfo=ZoneInfo('America/New_York')).astimezone(ZoneInfo('America/Chicago'))
    return f"{int(t.strftime('%I'))}:{t.strftime('%M %p')} CT"
def _etdata(iso):   # label stored in data files stays Eastern (display converts to CT)
    t=_dt.datetime.fromisoformat(iso.replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York'))
    return f"{t.strftime('%a %b')} {t.day}, {int(t.strftime('%I'))}:{t.strftime('%M %p')} ET"
def _etlbl(iso):
    t=_ET(iso); return f"{t.strftime('%a %b')} {t.day}, {int(t.strftime('%I'))}:{t.strftime('%M %p')} CT"
def _git(*a): return subprocess.run(['git','-C',R]+list(a),capture_output=True,text=True,check=True).stdout
def _snaps(kind, local_glob):
    out=[]
    for f in _git('ls-tree','--name-only','-r','origin/snapshots','snapshots/').split():
        if f.split('/')[-1].startswith(kind+'_'):
            d=json.loads(_git('show','origin/snapshots:'+f)); out.append((d['fetched_utc'],'snapshots branch '+f.split('/')[-1],d))
    for f in _g0.glob(local_glob+kind+'_*.json'):
        d=json.load(open(f)); out.append((d['fetched_utc'],'scripts/snapshot.py pull '+f.split('/')[-1],d))
    return sorted(out,key=lambda x:x[0])
def _dk_rows(d):
    o={}
    for g in d['games']:
        sp={}
        for s in g['spread']:
            t=s['side'].split(); sp[_NK[t[1]]]=dict(line=t[-1],money=s['handle_pct'],bets=s['bets_pct'])
        o[frozenset(sp)]=sp
    return o
def _sao_rows(d):
    return {frozenset((_SAOAB.get(g['away'],g['away']),_SAOAB.get(g['home'],g['home']))):
            {_SAOAB.get(g['away'],g['away']):(g['money_away'],g['bets_away']),_SAOAB.get(g['home'],g['home']):(g['money_home'],g['bets_home'])} for g in d['games']}
def _side(two):  # {abbr:(money,bets)} -> (money side abbr, money, bets on that side)
    s=max(two,key=lambda k:two[k][0]); return s,two[s][0],two[s][1]
def rate_v1(A,H,ab,dk_side,mon,close_sp,qb_drop):
    """Rules v1. ab=(side abbr,money,bets) all books; mon=start-of-week dict; close_sp={abbr:'+7.5'}. Returns rating,type,e,d."""
    s,m,b=ab
    lnum=lambda v:float(v.replace(M,'-').replace('PK','0'))
    ms_now=lnum(close_sp[s]); ms_open=mon['avg'] if mon['team']==s else -mon['avg']
    e=(ms_open-ms_now)>1; d=ms_now<=-6 and m>50
    if dk_side!=s and m>50: return 'PASS',4,e,d
    if m<55: return 'PASS',5,e,d
    a=b>=50; bb=m>=65
    ty=1 if (bb and d) else 2 if (bb and a) else 3
    if not a: return 'PASS',ty,e,d
    lvl=(2 if bb else 1)-e-qb_drop
    return ['PASS','LEAN','STRONG'][max(lvl,0)],ty,e,d
def settle_w5():
    sb=json.load(open(_W+'/espn_sum/sb_w5.json'))
    wk=None
    import importlib.util as _iu
    _sp=_iu.spec_from_file_location('snapmod',R+'scripts/snapshot.py'); _sm=_iu.module_from_spec(_sp); _sp.loader.exec_module(_sm)
    wk=_sao_rows({'games':[g for g,_ in _sm.sao_parse(open(_W+'/sao_week5_20261013.html').read())]})
    WKAT='ScoresAndOdds week page (consensus-picks?week=2026-reg-5), fetched Tue Oct 13, 11:02 PM ET, after the games; the page keeps one split per game and is not timestamped'
    DKS=_snaps('dk',_W+'/snap_w5_*/'); SAOS=_snaps('sao',_W+'/snap_w5_*/')
    close=json.load(open(R+'data/closing_splits.json'))
    ev={}
    for e in sb['events']:
        c=e['competitions'][0]; t={x['homeAway']:x for x in c['competitors']}
        ev[frozenset((t['away']['team']['abbreviation'],t['home']['team']['abbreviation']))]=dict(id=e['id'],ko=e['date'].replace('Z',':00Z'),
            a=t['away']['score'],h=t['home']['score'],final=c['status']['type']['name']=='STATUS_FINAL')
    out={}
    for g in G:
        A,H=g['A'],g['H']; key=frozenset((A,H)); x=ev[key]; ko=x['ko']
        if g['gid']=='tbdal-card': continue
        summ=json.load(open(_W+f"/espn_sum_w5/{x['id']}.json"))
        pc=[p for p in summ['pickcenter'] if 'DraftKings' in p['provider']['name']][0]['pointSpread']
        csp={H:pc['home']['close']['line'].replace('-',M),A:pc['away']['close']['line'].replace('-',M)}
        cpr={H:pc['home']['close']['odds'].replace('-',M),A:pc['away']['close']['odds'].replace('-',M)}
        import slight_grade as _sgx
        for _t in (A,H):
            _p=_sgx.pre_line(5,A,H,_t)
            if _p:   # grading/closing number = last pre-kickoff DraftKings pull (TG, Oct 15)
                _l=_p['line']; csp[_t]=('PK' if _l==0 else (f"+{_l:g}" if _l>0 else f"{M}{abs(_l):g}")); _pp=_p['price']; cpr[_t]=(f"+{_pp}" if _pp>0 else f"{M}{abs(_pp)}")
        fade=AB[g['fade']]
        dkp=[(t,src,_dk_rows(d)[key]) for t,src,d in DKS if t<ko and key in _dk_rows(d)]
        sap=[(t,src,_sao_rows(d)[key]) for t,src,d in SAOS if t<ko and key in _sao_rows(d)]
        dk_t,dk_src,dk=dkp[-1]; dks=max(dk,key=lambda k:dk[k]['money'])
        branch_pre=[p for p in dkp if p[1].startswith('snapshots branch') and _ET(p[0])>_ET(ko)-_dt.timedelta(hours=3)]
        ab=_side(wk[key]); sa_t,sa_src,sa=sap[-1]; abp=_side(sa)
        qb=False
        # TG decision Oct 13: closing split = last real pull before kickoff; a page read after kickoff is never a closing source
        rt,ty,e,d=rate_v1(A,H,abp,dks,g['mon'],csp,qb)
        same=(rt,ty)==(g['rating'],g['type']) and abp[0]==AB[g['ab_side']]
        assert same or g['rating']=='PASS', (g['gid'],'closing rating differs from the locked card: TG decides',rt,ty)
        ent=dict(game=f'{A}@{H}',kickoff_utc=ko,locked=dict(rating=g['rating'],type=g['type']),
            all_books_week_page_not_used=dict(side=NAME[ab[0]],money=ab[1],bets=ab[2],at=WKAT,why='read after kickoff; never a closing source'),
            sao_last_before_kickoff=dict(side=NAME[abp[0]],money=abp[1],bets=abp[2],at=_etdata(sa_t),source=sa_src),
            draftkings=(dict(side=NAME[dks],money=dk[dks]['money'],bets=dk[dks]['bets'],at=_etdata(dk_t),source=dk_src) if branch_pre else None),
            draftkings_last_pull=dict(side=NAME[dks],money=dk[dks]['money'],bets=dk[dks]['bets'],at=_etdata(dk_t),source=dk_src),
            dk_close=dict(sp=csp,price=cpr[AB[NAME[H] if abp[0]==A else NAME[A]]] if rt!='PASS' else None,prices=cpr,source=f"ESPN game summary {x['id']} (DraftKings close)"),
            final=dict(score=f"{x['a']}-{x['h']}",status='final' if x['final'] else 'not final'),
            closing_rating=dict(rating=rt,type=ty,line_moved_over_1_toward_money=e,on='last all-books and DraftKings pulls before kickoff + DraftKings closing line'),
            matches_locked=same)
        if not branch_pre:
            ent['draftkings_note']=(f"DraftKings closing split not captured: no snapshot in the pre-kickoff slot. Last DraftKings pull before kickoff: "
                                    f"{_etdata(dk_t)} ({dk_src}), {NAME[dks]} {dk[dks]['money']}% of the money.")
            ent['dk_note_short']=f"last DraftKings pull {_etdata(dk_t)}; no closer split was saved"
        else:
            ent['dk_note_short']=f"DraftKings split {_etdata(dk_t)}, the last before kickoff"
        if rt!='PASS':
            ent['all_books']=dict(side=NAME[abp[0]],money=abp[1],bets=abp[2],at=_etdata(sa_t),source='ScoresAndOdds, '+sa_src,
                                  label=f"last pull before kickoff: {_etdata(sa_t)}")
        if rt=='PASS':
            ent.pop('dk_close'); ent['dk_close_line']=dict(sp=csp,source=f"ESPN game summary {x['id']} (DraftKings close)")
        out[g['gid']]=ent
    tb=close['tbdal-card']
    tb['all_books_week_page_not_used']=dict(tb.pop('all_books'),why='read after kickoff; never a closing source')
    tb['all_books']=dict(side='Dallas',money=66,bets=73,at='Thu Oct 8, 1:58 PM ET',source='ScoresAndOdds pull (week5_refresh.py, audit_src/sao_all.csv)',label='last pull before kickoff: Thu Oct 8, 1:58 PM ET')
    tb['closing_rating']=dict(rating='STRONG',type=1,line_moved_over_1_toward_money=False,on='last all-books and DraftKings pulls before kickoff + DraftKings closing line')
    close.update(out)
    close['_rule']=close.get('_rule','')
    close['_catchup1']=('Week 5 settled Tue Oct 13 from: ESPN (DraftKings closing line and price, final score), the last all-books pull before kickoff (ScoresAndOdds), '
                        'and the last DraftKings split saved before kickoff (snapshots branch or a dated scripts/snapshot.py pull). The 1:00 PM ET slot has no pre-kickoff '
                        'snapshot on the snapshots branch.')
    close['_rule']=('Closing split = the last real pull before kickoff (snapshot or our own dated pull), labeled with its exact time and source. '
                    'A page read after kickoff is never a closing source (TG, Tue Oct 13). DraftKings removes a game at kickoff.')
    json.dump(close,open(R+'data/closing_splits.json','w'),indent=1,ensure_ascii=False)
    # live log: fill closing fields for posted plays (never touch posted fields)
    p=R+'data/live_log.csv'; rows=list(_c0.DictReader(open(p))); fn=list(rows[0].keys())
    byg={f"{g['A']}@{g['H']}":g for g in G}
    for r in rows:
        if r['week']!='5': continue   # later weeks are settled by hand from their last pre-kickoff pull
        g=byg[r['game']]; c=out.get(g['gid'])
        if r['game']=='TB@DAL':
            r['close_all_money']='DAL 66'; r['close_all_bets']='DAL 73'; r['close_split_at']='last pull before kickoff: Thu Oct 8, 1:58 PM ET'; r['close_split_source']='ScoresAndOdds (all books); DraftKings splits page had dropped the game'
        if not c: continue
        side=r['our_side']; a,h=map(int,c['final']['score'].split('-'))
        ln_=float(c['dk_close']['sp'][side].replace(M,'-')); mg=(a-h if side==g['A'] else h-a)+ln_
        res='W' if mg>0 else ('L' if mg<0 else 'P'); pr=c['dk_close']['price'].replace(M,'-')
        r['closing_line']=c['dk_close']['sp'][side].replace(M,'-'); r['closing_price']=pr; r['final_score']=c['final']['score']; r['result']=res
        r['profit_usd']=f"{live_profit(r):.2f}"
        wb=c['all_books']; ws=AB[wb['side']]; dl=c['draftkings_last_pull']
        r['close_all_money']=f"{ws} {wb['money']}"; r['close_all_bets']=f"{ws} {wb['bets']}"
        r['close_dk_money']=(f"{AB[dl['side']]} {dl['money']} ({dl['at']})" if c['draftkings'] else f"not captured (last pull {dl['at']}: {AB[dl['side']]} {dl['money']})")
        r['close_split_at']=wb['label']; r['close_split_source']=wb['source']+' + DraftKings'
    w=_c0.DictWriter(open(p,'w',newline=''),fieldnames=fn,lineterminator='\n'); w.writeheader(); w.writerows(rows)
    return out
if os.path.exists(_W+'/sao_week5_20261013.html'): SETTLED=settle_w5()
# one closing number per game: every Week 5 card uses the last pull before kickoff (rating, money, bets)
CLOSE_APPLIED=[]
def _apply_close():
    cs=SETTLED if isinstance(SETTLED,dict) else {}
    for g in G:
        c=cs.get(g['gid'])
        if not c or g['gid']=='tbdal-card': continue
        sa=c.get('sao_last_before_kickoff'); dk=c.get('draftkings_last_pull'); cr=c.get('closing_rating')
        if not (sa and dk and cr): continue
        sp=(c.get('dk_close') or c.get('dk_close_line') or {}).get('sp') or g['sp']
        side=sa['side']; m,b=sa['money'],sa['bets']; fade=g['home'] if side==g['away'] else g['away']
        g.update(ab_side=side,ab_m=m,ab_b=b,dk_side=dk['side'],dk_m=dk['money'],dk_b=dk['bets'],a=b>=50,b=m>=65,c=dk['side']==side,
                 e=cr['line_moved_over_1_toward_money'],rating=cr['rating'],type=cr['type'],fade=fade,sp=dict(sp),fade_line=float(sp[AB[fade]].replace('−','-').replace('PK','0')),
                 split_at=sa['at'])
        g['d']=g['type']==1
        ty=g['type']
        g['why']=('DraftKings has the money on the other side' if ty==4 else 'Under 55% of the money on either side' if ty==5 else
                  'Money and bets on different sides' if not g['a'] else f"Starts at {'STRONG' if m>=65 else 'LEAN'}"+(' · −1 for line move' if g['e'] else ' · no drops'))
        g['wy']=f"{m}% of the money is on {side} (all books)."
        g['call']=f"{fade} {sp[AB[fade]]}"
        CLOSE_APPLIED.append((g['gid'],sa['at'],dk['at']))
_apply_close()
# ---------- weeks 6 on: one generic builder per week (card until kickoff, final after) ----------
def _live_weeks():
    # every week from 6 that has its Monday line file and a scoreboard; TYGIF_WEEK caps it (the card week)
    out=[]; w=6
    while os.path.exists(_I+f'/tr_monday_w{w}.json') and os.path.exists(_W+f'/espn_sum/sb_w{w}.json'): out.append(w); w+=1
    cap=os.environ.get('TYGIF_WEEK')
    return [w for w in out if not cap or w<=int(cap)]
class _NotReady(Exception): pass
def build_wk(WK):
    # same as settle_w5: every pull (snapshots branch + our dated pulls), per game the latest one before kickoff
    DKS6=_snaps('dk',_W+f'/snap_w{WK}_*/'); SAOS6=_snaps('sao',_W+f'/snap_w{WK}_*/')
    TRM=json.load(open(_I+f'/tr_monday_w{WK}.json'))
    sb=json.load(open(_W+f'/espn_sum/sb_w{WK}.json'))
    out=[]
    for e in sorted(sb['events'],key=lambda e:e['date']):
        c=e['competitions'][0]; t={x['homeAway']:x['team']['abbreviation'] for x in c['competitors']}
        A,H=t['away'],t['home']; key=frozenset((A,H))
        # any status other than final (scheduled, in progress, delayed, postponed) stays pending; only finals settle
        ko_s=e['date'].replace('Z',':00Z') if e['date'].count(':')==1 else e['date']
        lo_s=(_dt.datetime.fromisoformat(ko_s.replace('Z','+00:00'))-_dt.timedelta(days=8)).isoformat()
        dkp=[(t_,src,_dk_rows(d)[key]) for t_,src,d in DKS6 if lo_s<t_<ko_s and key in _dk_rows(d)]
        sap=[(t_,src,_sao_rows(d)[key]) for t_,src,d in SAOS6 if lo_s<t_<ko_s and key in _sao_rows(d)]
        if not dkp or not sap: raise _NotReady(f'week {WK}: {A}@{H} has no DraftKings/ScoresAndOdds pull before kickoff yet')
        dk_t,dk_src,dk=dkp[-1]; sa_t,sa_src,sa_row=sap[-1]
        sar={key:sa_row}
        sp={k:v['line'].replace('-',M) for k,v in dk.items()}   # DraftKings line at the last pre-kickoff pull (never an ESPN summary read after kickoff)
        dks=max(dk,key=lambda k:dk[k]['money']); abs_,abm,abb=_side(sar[key])
        mon=[v for v in TRM.values() if {v['team'],v['other']}=={A,H}][0]
        b2=mon['books'].get('2',{}).get('line'); b3=mon['books'].get('3',{}).get('line')
        mon=dict(team=mon['team'],b2=b2 if b2 is not None else b3,b3=b3 if b3 is not None else b2,avg=mon['avg'],source='TeamRankings books 2-3, last quote before Monday 12:00 AM ET')
        fade_ab=H if abs_==A else A
        drop=False; qbnote=''
        rt,ty,ee,dd=rate_v1(A,H,(abs_,abm,abb),dks,mon,sp,drop)
        ko=_ET(e['date'].replace('Z',':00Z'))
        city=c.get('venue',{}).get('address',{}).get('city','')
        when=f"{ko.strftime('%a %b')} {ko.day} · {int(ko.strftime('%I'))}:{ko.strftime('%M %p')} CT · "+', '.join(n for b in c.get('broadcasts',[]) for n in b['names'])+(' · London' if city=='London' else '')
        if ty==4: why='DraftKings has the money on the other side'
        elif ty==5: why='Under 55% of the money on either side'
        elif abb<50: why='Money and bets on different sides'
        else:
            drops=[n for n,v in (('line move',ee),) if v]
            why=f"Starts at {'STRONG' if abm>=65 else 'LEAN'}"+(''.join(f' · −1 for {x}' for x in drops) if drops else ' · no drops')
        g=dict(gid=f'w{WK}-{A.lower()}-{H.lower()}',A=A,H=H,away=NAME[A],home=NAME[H],sp=sp,ab_side=NAME[abs_],ab_m=abm,ab_b=abb,
               dk_side=NAME[dks],dk_m=dk[dks]['money'],dk_b=dk[dks]['bets'],a=abb>=50,b=abm>=65,c=dks==abs_,d=dd,e=ee,f=drop,
               fade=NAME[fade_ab],fade_line=float(sp[fade_ab].replace(M,'-')),rating=rt,type=ty,why=why,when=when,mon=mon,qbnote=qbnote,
               split_at=_etlbl(sa_t),split_utc=sa_t,dk_utc=dk_t,split_src=sa_src,dk_src=dk_src,final=None,held=False,week=WK,ko_utc=ko_s,eid=e['id'],status=c['status']['type']['name'])
        g['call']=f"{g['fade']} {sp[fade_ab]}"
        g['wy']=f"{abm}% of the money is on {NAME[abs_]} (all books)."+''
        out.append(g)
    return out
LIVEW=[]; GBY={}
for _w in _live_weeks():
    try: GBY[_w]=build_wk(_w); LIVEW.append(_w)
    except _NotReady as _e:
        if _w!=_live_weeks()[-1]: raise SystemExit(str(_e))   # only the newest week may be waiting for its card
        print(f'week {_w} not built yet (card not ready): {_e}')
GW=LIVEW[-1]   # GW = current card week
GALL=[g for w in LIVEW for g in GBY[w]]   # every game, weeks 6 on
G6=GBY[GW]                                # the current card week (name kept: G6 = current week)
PULL6=_etdata(max(g['split_utc'] for g in G6))   # newest pre-kickoff all-books pull used on the current card (stored ET; shown in CT)
# ---------- both sides of every game ----------
import sides as _sd
_SG=[dict(week=k[0],A=k[1].split('@')[0],H=k[1].split('@')[1],rating=CARD[k]['rating'] if k in CARD else 'PASS',type=T[k]['type'],
          money=T[k]['money_side'] if (T[k]['money_pct'] or 0)>50 else None,money_pct=int(T[k]['money_pct'] or 0),fade=T[k]['side'] if k in CARD else None) for k in sorted(T)]
_SG+=[dict(week=w_,A=g['A'],H=g['H'],rating=g['rating'],type=g['type'],money=AB.get(g['ab_side']) if g.get('ab_m',0)>50 else None,
          money_pct=g.get('ab_m') or 0,fade=AB.get(g['fade'])) for w_,gs_ in ((5,G),)+tuple((w,GBY[w]) for w in LIVEW) for g in gs_]
SIDES,SFLAGS=_sd.build(_SG)
json.dump({'rule':'Both sides of every game. fade = against the money (our call on STRONG/LEAN); money = follows the money. Spread groups: rating+type+side; ML groups: rating+type+side+Fav/Dog. DraftKings close, flat $100, profit rounded per play.',
           'flags':SFLAGS,'rows':SIDES},open(R+'data/sides_log.json','w'),indent=1)
SDX={}
for _r in SIDES: SDX.setdefault((_r['week'],_r['game']),{})[_r['role']]=_r
def sp_grp(r,before=None): return _sd.grp(SIDES,r['rating'],r['type'],r['role'],before=before)
def ml_grp(r,before=None): return _sd.grp(SIDES,r['rating'],r['type'],r['role'],fd=r['fd'],ml=True,before=before)
def _pos(a): return a[4]>0 and a[3]>0
SCONF=[]
def _ours(r): return r['role']=='fade' and r['rating']!='PASS'
def sp_post(r): return _ours(r)        # plays are only our STRONG/LEAN fade-side calls; money side and PASS sides are tracking only
def t3dog(r): return r['type']==3 and r['fd']=='Dog'   # Rules v3.1: Type 3 underdog = pass on the moneyline; spread unaffected
def ml_post(r): return _ours(r) and bool(r['fd']) and not t3dog(r) and _pos(ml_grp(r,r['week']))
ROLE={'fade':'fade','money':'money'}
for g in GALL: g['src']=dict(SRC_STD)
CLBL='(all books, final split; read after kickoff, page not timestamped)'
CLOSE=json.load(open(R+'data/closing_splits.json'))
for g in G:
    c=CLOSE.get(g['gid'])
    if c and c.get('all_books'):
        ab=c['all_books']; assert ab['side']==g['ab_side'], (g['gid'],'closing money flipped sides: re-rate by hand')
        old=g['ab_m']; g['ab_m'],g['ab_b']=ab['money'],ab['bets']
        g['a']=g['ab_b']>=50; g['b']=g['ab_m']>=65
        g['wy']=g['wy'].replace(f"{old}% of the money",f"{g['ab_m']}% of the money").replace('(all books)',f"(all books, {ab.get('label','last pull before kickoff')})")
        g['split_at']='closing'; g['clbl']=f"(all books, {ab['label']})" if ab.get('label') else CLBL
    else:
        pass
        g['split_at']=PULL
    g['dk_note']=(c or {}).get('draftkings_note'); g['dk_note_short']=(c or {}).get('dk_note_short') or ('last pull Thu Oct 8, 1:58 PM ET; DraftKings closing split not found' if g['dk_note'] else None)
    if c and c.get('all_books') and c.get('draftkings_last_pull'):
        dl=c['draftkings_last_pull']; assert dl['side']==g['dk_side'], (g['gid'],'DraftKings side flipped at the close: re-rate by hand'); g['dk_m']=dl['money']
    g['held']=bool(c and not c.get('all_books') and g['rating']!='PASS' and c.get('closing_rating'))
    if g.get('price'): PRICE[g['gid']]=g['price'].replace('-','−')
    if c and c.get('dk_close'):
        g['sp']=dict(c['dk_close']['sp']); PRICE[g['gid']]=c['dk_close']['price']
        g['call']=f"{g['fade']} {g['sp'][AB[g['fade']]]}"; g['fade_line']=float(g['sp'][AB[g['fade']]].replace('−','-'))
        if c.get('closing_rating'):
            fa,fl=fav_of(g); big=fa is not None and abs(float(fl.replace(M,'-')))>=6
            g['d']=big and fa==AB[g['ab_side']] and g['ab_m']>50
            g['e']=c['closing_rating']['line_moved_over_1_toward_money']
def _final(g):
    for r in live_rows():
        if int(r['week'])==g.get('week',5) and r['game']==f"{g['A']}@{g['H']}" and (r.get('result') or '').strip():
            res=live_profit(r); a,h=r['final_score'].split('-')
            word={"W":"win","L":"loss","P":"push"}[r['result'].upper()[:1]]
            return dict(r=r,score=r['final_score'],a=a,h=h,word=word,usd=res,
                        tag=f"Final: {r['our_side']} {a if r['our_side']==g['A'] else h}–{h if r['our_side']==g['A'] else a} · {word} {usd(res)}")
    return None
for g in G:
    g['final']=_final(g); g['week']=5
    g['src']=dict(SRC_STD,splits_draftkings=_K['week_5_draftkings']) if g.get('dk_note') else dict(SRC_STD)
def _settle_rows():
    """settle.py (TYGIF_SETTLE=1): add a data/live_log.csv row for every final STRONG/LEAN game, weeks 6 on, that has none.
    Graded at the DraftKings line and price from the last pull before kickoff (data/pregame_lines.json); never an ESPN summary."""
    have={(int(r['week']),r['game']) for r in live_rows()}; fn=list(live_rows()[0].keys()) if live_rows() else None
    new=[]
    for g in sorted(GALL,key=lambda g:g['ko_utc']):
        k=(g['week'],f"{g['A']}@{g['H']}")
        if g['rating']=='PASS' or g['status']!='STATUS_FINAL' or k in have: continue
        side=AB[g['fade']]; p=_sg0.pre_line(g['week'],g['A'],g['H'],side)
        if not p: raise SystemExit(f'{k}: no DraftKings line recorded before kickoff; cannot settle')
        c=[x for x in json.load(open(_W+f"/espn_sum/sb_w{g['week']}.json"))['events'] if x['id']==g['eid']][0]['competitions'][0]
        sc={x['homeAway']:int(x['score']) for x in c['competitors']}
        mg=(sc['away']-sc['home'] if side==g['A'] else sc['home']-sc['away'])+float(p['line'])
        res='W' if mg>0 else 'L' if mg<0 else 'P'; pr=int(p['price'])
        usd_=-100.0 if res=='L' else 0.0 if res=='P' else round(100*(pr/100 if pr>0 else 100/abs(pr)),2)
        ln=lambda v:('+' if v>0 else '')+format(v,'g') if v else 'PK'
        ko=_dt.datetime.fromisoformat(g['ko_utc'].replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York'))
        _ny=lambda iso:(lambda t:f"{t:%Y-%m-%d} {int(t.strftime('%I'))}:{t:%M %p}")(_dt.datetime.fromisoformat(iso.replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York')))
        at_=_etdata(g['split_utc']); dk_at=_etdata(g['dk_utc'])
        new.append(dict(week=g['week'],game=k[1],kickoff_et=f"{ko:%Y-%m-%d} {int(ko.strftime('%I'))}:{ko:%M %p}",rating=g['rating'],type=g['type'],our_side=side,
            posted_line=ln(float(p['line'])),posted_price=str(pr),posted_at_et=_ny(g['split_utc']),pulled_at_et=_ny(g['split_utc']),closing_line=ln(float(p['line'])),closing_price=str(pr),
            final_score=f"{sc['away']}-{sc['home']}",result=res,profit_usd=format(usd_,'g'),close_all_money=f"{AB[g['ab_side']]} {g['ab_m']}",close_all_bets=f"{AB[g['ab_side']]} {g['ab_b']}",
            close_dk_money=f"{AB[g['dk_side']]} {g['dk_m']} ({dk_at})",close_split_at=f"last pull before kickoff: {at_}",
            close_split_source=f"ScoresAndOdds, {g['split_src']} + DraftKings {g['dk_src'].split()[-1]}",
            card_source=f"line+price: DraftKings splits page {side} {ln(float(p['line']))} {pr} at the last pre-kickoff pull ({p['source']}); ML: {p.get('ml_source','none recorded')}"))
    if new:
        w=_csv.DictWriter(open(R+'data/live_log.csv','a',newline=''),fieldnames=fn,lineterminator='\n'); w.writerows(new)
        print('settled:',', '.join(f"W{r['week']} {r['game']} {r['our_side']} {r['closing_line']} {r['result']}" for r in new))
    return new
if os.environ.get('TYGIF_SETTLE'): _settle_rows()
for _g in GALL: _g['final']=_final(_g) if _g['status']=='STATUS_FINAL' else None   # weeks 6 on: settled in live_log; only final games
FINW={(_g['week'],f"{_g['A']}@{_g['H']}") for _g in GALL if _g['final']}
FIN6={k[1] for k in FINW if k[0]==GW}
# ---------- moneyline plays (TG, Oct 13): underdog side of every STRONG/LEAN play, DraftKings closing ML (ESPN) ----------
ML_PULL='data/pregame_lines.json'
def _espn_index():
    ix={}
    for w in _sg0.WEEKS:
        for e in json.load(open(_W+f'/espn_sum/sb_w{w}.json'))['events']:
            c=e['competitions'][0]; t={x['homeAway']:x for x in c['competitors']}
            ix[(w,t['away']['team']['abbreviation'],t['home']['team']['abbreviation'])]=dict(id=e['id'],a=t['away'].get('score'),h=t['home'].get('score'),
                final=c['status']['type']['name']=='STATUS_FINAL')
    return ix
def _ml_price(eid,side_home):
    s=json.load(open(_W+f'/espn_sum/{eid}.json'))
    for p in s.get('pickcenter',[]):
        if 'DraftKings' in p['provider']['name'] and p.get('moneyline'):
            v=((p['moneyline'].get('home' if side_home else 'away') or {}).get('close') or {}).get('odds')
            return int(v.replace('+','')) if v and v not in ('OFF','EVEN') else (100 if v=='EVEN' else None)
    return None
def ml_profit(price,res):
    if res=='L': return -100.0
    if res=='P' or res is None: return 0.0 if res=='P' else None
    return float(round(price if price>0 else 100*100/abs(price)))
def build_ml():
    ix=_espn_index(); rows=[]
    def add(week,game,rating,side,line,status):
        A,H=game.split('@'); x=ix.get((week,A,H))
        price=_ml_price(x['id'],side==H) if (x and week<_sg0.PRE_ONLY) else None   # weeks 6 on: never an ESPN summary (may be read after kickoff)
        if _sg0.pre_ml(week,A,H,side) is not None: price=_sg0.pre_ml(week,A,H,side)   # last pre-kickoff DraftKings moneyline
        r=dict(week=week,game=game,rating=rating,side=side,spread_line=line,status=status,espn_event=x['id'] if x else None,price=price,
               fd=(None if price is None else ('Dog' if price>0 else 'Fav')))
        if price is None: r['note']='no DraftKings moneyline recorded before kickoff: no ML play graded'
        if x and x['final']:
            a,h=int(x['a']),int(x['h']); mg=(a-h) if side==A else (h-a)
            r['score']=f'{a}-{h}'; r['result']='W' if mg>0 else ('L' if mg<0 else 'P')
            r['profit']=ml_profit(r['price'],r['result']) if r['price'] is not None else None
        rows.append(r)
    for k in sorted(CARD):
        add(k[0],k[1],CARD[k]['rating'],T[k]['side'],float(T[k]['line']),'look back')
    for r in live_rows():
        add(int(r['week']),r['game'].replace('LA@','LAR@'),r['rating'],r['our_side'],float((r.get('closing_line') or r['posted_line']).replace('−','-')),'live')
    for g in GALL:
        if g['rating']!='PASS' and (g['week'],f"{g['A']}@{g['H']}") not in FINW: add(g['week'],f"{g['A']}@{g['H']}",g['rating'],AB[g['fade']],g['fade_line'],'preview')
    json.dump({'source':'DraftKings moneyline recorded last before kickoff ('+ML_PULL+'); ESPN game summary close only where nothing was recorded (Weeks 1-4)',
               'rule':'Every STRONG or LEAN spread play also has our side graded on the DraftKings moneyline recorded before kickoff, favorite or underdog, flat $100, profit rounded per play. Groups: rating + type + favorite/underdog. A moneyline play is posted only when its group record over prior weeks is profitable (> $0); never on a Type 3 underdog. Never combined with spread; STRONG never combined with LEAN.',
               'plays':rows},open(R+'data/ml_log.json','w'),indent=1)
    return rows
ML=build_ml()
MLBY={(r['week'],r['game']):r for r in ML}
def all_recs():
    out=[]
    for k in CARD: out.append(dict(week=k[0],game=k[1],rating=CARD[k]['rating'],type=T[k]['type'],res=T[k]['res'],usd=T[k]['usd'],play=short_play(k),score=T[k]['score']))
    for r in live_rows():
        p=live_profit(r)
        if p is None: continue
        out.append(dict(week=int(r['week']),game=r['game'],rating=r['rating'],type=int(r['type']),res=r['result'].upper()[:1],usd=p,
                        play=f"{r['our_side']} {(r.get('closing_line') or r['posted_line']).replace('-',M)}",
                        score=(lambda A,H,a,h:f"{A} {a}, {H} {h}")(*r['game'].split('@'),*r['final_score'].split('-'))))
    return out
RECS=all_recs(); WEEKS=sorted({r['week'] for r in RECS})
def at(rt=None,ty=None,wk=None,before=None):
    rs=[r for r in RECS if (rt is None or r['rating']==rt) and (ty is None or r['type']==ty) and (wk is None or r['week']==wk) and (before is None or r['week']<before)]
    return sum(r['res']=='W' for r in rs),sum(r['res']=='L' for r in rs),sum(r['res']=='P' for r in rs),sum(r['usd'] for r in rs),len(rs)
def wlp(w,l,p): return f'{w}-{l}-{p}'
TYPEOF={(r['week'],r['game'].replace('LA@','LAR@')):r['type'] for r in RECS}
def ml_type(r):
    if r['week']>=6:
        g=[g for g in GALL if g['week']==r['week'] and f"{g['A']}@{g['H']}"==r['game']]; return g[0]['type'] if g else None
    return TYPEOF.get((r['week'],r['game']))
def ml_at(rt,ty=None,fd=None,before=None):
    rs=[r for r in ML if r['rating']==rt and r.get('profit') is not None and (ty is None or ml_type(r)==ty) and (fd is None or r['fd']==fd) and (before is None or r['week']<before)]
    return sum(r['result']=='W' for r in rs),sum(r['result']=='L' for r in rs),sum(r['result']=='P' for r in rs),sum(r['profit'] for r in rs),len(rs)
def _rows_html(rs):
    return ''.join(f'<li><span class="rl-w">Wk {r["week"]}</span><span class="rl-g">{r["game"].replace("@"," at ")}</span><span class="rl-p">{LOGO(r["play"].split()[0],"rlg")}{r["play"]}</span>'
                   f'<span class="rl-s">{r["score"]}</span><b class="rl-r {r["res"]}">{r["res"]} {usd(r["usd"])}</b></li>' for r in rs)
def spread_rows(rt,ty): return sorted([r for r in RECS if r['rating']==rt and r['type']==ty],key=lambda r:(r['week'],r['game']))
def ml_rows(rt,ty=None,fd=None):
    out=[]
    for r in ML:
        if r['rating']!=rt or r.get('profit') is None or (ty is not None and ml_type(r)!=ty) or (fd is not None and r['fd']!=fd): continue
        A,H=r['game'].split('@'); a,h=r['score'].split('-')
        out.append(dict(week=r['week'],game=r['game'],play=f"{r['side']} ML",score=f"{A} {a}, {H} {h}",res=r['result'],usd=r['profit']))
    return sorted(out,key=lambda r:(r['week'],r['game']))
def rlist(rt,ty,ml=False,cls='cd-rl',fd=None):
    rs=ml_rows(rt,ty,fd) if ml else spread_rows(rt,ty)
    if not rs: return ''
    w=sum(r['res']=='W' for r in rs); l=sum(r['res']=='L' for r in rs); p=sum(r['res']=='P' for r in rs); u=sum(r['usd'] for r in rs)
    lab=f'{rt}{" ML" if ml else ""}{f" · Type {ty}" if ty else ""}{f" · {FDN[fd]}" if fd else ""}'
    return (f'<details class="{cls}" data-k="{lab}"><summary><span>{lab} · <span class="ng">{len(rs)} game{"s" if len(rs)!=1 else ""}</span></span><b>{wlp(w,l,p)}, {usd(u)}</b></summary>'
            f'<ul class="rl">{_rows_html(rs)}</ul></details>')
FDN={'Fav':'Favorite','Dog':'Underdog'}
def ml_ok(g):
    # TG rule: post an ML play only when its rating + type + favorite/underdog group is profitable (> $0) through the last graded week
    r=ml_for(g,g.get('week',5))
    if g['rating']=='PASS' or not r or r.get('price') is None: return False
    if g['type']==3 and r['fd']=='Dog': return False   # Rules v3.1: Type 3 underdog = pass on the moneyline
    a=ml_at(g['rating'],g['type'],r['fd'],before=g.get('week',5)); return a[4]>0 and a[3]>0
def ml_games(GG,week):
    return [g for g in GG if g['rating']!='PASS' and (lambda r:r and r.get('price') is not None)(ml_for(g,week)) and ml_ok(g)]
def ml_for(g,week):
    return MLBY.get((week,f"{g['A']}@{g['H']}"))
def ml_tally(rt,status):
    rs=[r for r in ML if r['rating']==rt and r['status'] in status and r.get('profit') is not None]
    w=sum(r['result']=='W' for r in rs); l=sum(r['result']=='L' for r in rs); p=sum(r['result']=='P' for r in rs)
    return w,l,p,sum(r['profit'] for r in rs),len(rs)
plays=[g for g in G if g['rating']!='PASS']; passes=[g for g in G if g['rating']=='PASS']
plays6=[g for g in G6 if g['rating']!='PASS']; passes6=[g for g in G6 if g['rating']=='PASS']
SRC6=f"As of {PULL6}"
CARD_CSS=r"""
.cd-mn summary,.cd-mn summary b{color:var(--mut);font-weight:500}
.cd.cdg{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);column-gap:14px;align-items:start}
.cd.cdg>.cd-1,.cd.cdg>.cd-4{grid-column:1/-1}
.cd.cdg>.cd-2,.cd.cdg>.cd-m{margin-top:9px}
.cd.cdg>.cd-m{border-left:1px solid var(--line);padding-left:12px}
.cd.cdg>.cd-m small{margin-left:0}
.cdh{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:0 10px}
.cdh>details.gm{grid-column:1/-1;min-width:0}
.cdh>.cd-rl{margin:-1px 0 0;min-width:0}
.g-b .tbdc{display:grid;grid-template-columns:minmax(0,1fr);gap:8px}
.g-b .uc{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:6px 14px}
@media (min-width:481px){.cdh{grid-template-columns:1fr 1fr}}
@media (max-width:480px){.cdh{grid-template-columns:minmax(0,1fr)}}
@media (max-width:420px){.cd.cdg{column-gap:8px}.cd.cdg>.cd-m{padding-left:8px}.cd-c{white-space:normal}}
.cd{display:block;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--pass);padding:12px 14px;color:var(--txt);text-decoration:none;list-style:none;cursor:pointer}
.cd::-webkit-details-marker{display:none}
.cd.s-STRONG{border-left-color:#3fae6c}.cd.s-LEAN{border-left-color:#b8860b}
.cd-1{display:flex;align-items:center;gap:10px}
.cd-b{flex:0 0 auto;min-width:64px;text-align:center;font-size:12px;font-weight:800;letter-spacing:.07em;padding:4px 6px;border:2px solid}
.cd-b.STRONG{background:#3fae6c;border-color:#3fae6c;color:#0c0d0e}
.cd-b.PASS{background:transparent;border-color:#5b616b;color:#9a9da4;border-width:1px}
.cd-m{display:flex;flex-wrap:wrap;align-items:baseline;gap:4px 8px;margin:7px 0 0;font-size:13px}
.cd-m>b{font-size:11px;letter-spacing:.08em;color:var(--mut);font-weight:800;min-width:22px}
.cd-m .mc{font-weight:700}.cd-m small{flex-basis:100%;margin-left:30px;color:var(--mut);font-size:12px}
.fin.W{color:#3fae6c}.fin.L{color:#e07a7a}
.cd-b.LEAN{background:transparent;border-color:#b8860b;color:#d9a520;border-style:dashed}
.cd-c{font-size:19px;font-weight:800;letter-spacing:-.3px;flex:1;white-space:nowrap}
.cd-p{font-size:15px;font-weight:700;color:var(--mut);white-space:nowrap}
.cd-ar{color:var(--mut);font-size:18px;margin-left:2px}
.cd-rl{margin:-1px 0 0;border:1px solid var(--line);border-top:0;background:var(--card);font-size:13px}
.cd-rl>summary{list-style:none;cursor:pointer;display:flex;justify-content:space-between;gap:8px;padding:8px 14px;color:var(--mut)}
.cd-rl>summary::-webkit-details-marker{display:none}
.cd-rl>summary::after{content:'+';margin-left:6px}.cd-rl[open]>summary::after{content:'−'}
.cd-rl>summary b{color:var(--txt);font-weight:700;margin-left:auto;white-space:nowrap}
.cd-rl .ng{white-space:nowrap}
.rl{list-style:none;margin:0;padding:0 14px 8px}
.rl li{display:grid;grid-template-columns:40px 1fr auto;column-gap:8px;padding:6px 0;border-top:1px solid var(--line)}
.rl .rl-w{color:var(--mut)}.rl .rl-g{font-weight:600}.rl .rl-p{grid-column:2}.rl .rl-s{grid-column:2;color:var(--mut)}
.rl .rl-r{grid-column:3;grid-row:1;text-align:right;white-space:nowrap}.rl .rl-r.W{color:#3fae6c}.rl .rl-r.L{color:#e07a7a}
.tb-rl{margin:8px 0 0;border-top:1px solid var(--line)}
.cd-2{margin:9px 0 0;font-size:13px;line-height:1.35}
.cd-2 b{font-weight:700}.cd-2 .tn{color:#d4a017}
.cd-2 small{display:block;font-size:12px;color:var(--mut);margin-top:1px}
.cd-3{grid-column:1/-1;display:grid;grid-template-columns:repeat(4,1fr);gap:4px;margin:10px 0 0;padding:8px 0;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.cd-3 span{display:flex;flex-direction:column;align-items:center;font-size:12px;color:var(--mut);line-height:1.25;text-align:center}
.cd-3 b{font-size:13px;font-weight:800;white-space:nowrap}
.cd-3 .ok{color:#3fae6c}.cd-3 .md{color:#d9a520}.cd-3 .no{color:#e07a7a}
.cd-4{margin:9px 0 0;font-size:13px;color:var(--mut)}
.cd-4 .fin{color:#3fae6c;font-weight:700}.cd-4 .fin.L{color:#e07a7a}.cd-4 .fin.P{color:var(--txt)}
.cd-ml{display:block;margin:6px 0 0;font-size:13px;font-weight:700;color:var(--txt)}
.cdl{display:flex;flex-direction:column;gap:10px;margin:12px 0}
details.gm.cdw{border:0;background:transparent}
details.gm.cdw>summary{padding:0;list-style:none}
details.gm.cdw>summary::-webkit-details-marker{display:none}
details.gm.cdw>summary,details.gm.cdw[open]>summary{display:block!important;padding:0!important;margin:0;background:transparent;border:0}
details.gm.cdw>summary::after,details.gm.cdw>summary::before,details.pr>summary.ps::after,details.pr>summary.ps::before{display:none!important;content:none!important}
details.pr>summary.ps{padding:10px 12px!important;display:block!important;border:0}
details.gm.cdw[open]>summary .cd{border-bottom-color:transparent}
details.gm.cdw .g-b{border:1px solid var(--line);border-top:0;background:var(--card)}
.sec-n{font-size:12.5px;color:var(--mut);margin:-4px 0 8px;line-height:1.4}
.ps{display:block;padding:10px 2px;border-bottom:1px solid var(--line);list-style:none;cursor:pointer}
.ps::-webkit-details-marker{display:none}
.ps-1{display:flex;align-items:center;gap:10px;font-size:14px}
.ps-b{flex:0 0 auto;min-width:46px;text-align:center;font-size:12px;font-weight:800;letter-spacing:.06em;color:#9a9da4;border:1px solid #9a9da4;padding:2px 4px}
.ps-m{font-weight:700;flex:1}.ps-k{font-size:12px;color:var(--mut);white-space:nowrap}
.ps-2{display:block;font-size:12.5px;color:var(--mut);margin:4px 0 0 56px;line-height:1.35}
.ps-2 b{color:var(--txt);font-weight:700}
"""
def _gwk(g): return g.get('week',5)
def _cb(g):
    # as-posted basis: a finished card shows its groups as they stood when posted (weeks before its week);
    # an unplayed card shows every graded game so far
    return None   # user, Oct 15 11:10 PM: every card (finished or not) shows groups season-to-date, finished cards including their own game
def _steady(g): return (not g['e']) or g['ab_m']<=50
def ml_block(g):
    r=g['rating']; t=g['type']; mr=ml_for(g,_gwk(g))
    if r=='PASS' or not mr or mr.get('price') is None:
        return f'<span class="cd-m"><b class="ck">Moneyline</b><span class="mc c1 neu">{g["fade"]} ML</span><span class="c2">Type {t}</span><small class="c3">{"PASS" if r=="PASS" else "no moneyline"}</small></span>',None
    fd=mr['fd']; a=ml_at(r,t,fd,before=_cb(g)); lab=f'Type {t} · {FDN[fd]}'
    grp=f'Group: {wlp(*a[:3])}, {usd(a[3])}' if a[4] else 'Group: no games yet'
    if not ml_ok(g): call=None
    elif mr.get('result'): call=f'{g["fade"]} ML · <span class="fin {mr["result"]}">{dict(W="win",L="loss",P="push")[mr["result"]]} {usd(mr["profit"])}</span>'
    elif True: call=f'{g["fade"]} ML'
    neu=call is None
    if neu: call=f'{g["fade"]} ML'
    return f'<span class="cd-m"><b class="ck">Moneyline</b><span class="mc c1{" neu" if neu else ""}">{call}</span><span class="c2">{lab}</span><small class="c3">{grp}</small></span>',fd
_FF=json.load(open(R+'data/card_full.json'))['full']
class _All:
    def __contains__(self,x): return True
FULL=_All() if _FF=='all' else set(_FF)
def card_inner(g):
    t=g['type']; r=g['rating']
    if r!='PASS':
        side=g['fade']; ab=AB[side]; title=f'{side} {g["sp"][ab]}'
        other=g['home'] if side==g['away'] else g['away']; vs=('at ' if side==g['away'] else 'vs ')+other
        w,l,p_,u,n=at(r,t,before=_cb(g)); trec=f'Group: {wlp(w,l,p_)}, {usd(u)}' if n else 'Group: no plays yet'
    else:
        title=f'{g["away"]} at {g["home"]}'; vs=''; trec='PASS'
    m=g['ab_m']; mcls='ok' if m>=65 else 'md'
    cells=[('Money',f'{AB[g["ab_side"]]} {m}%',mcls),('Bets',f'{AB[g["ab_side"]]} {g["ab_b"]}%','ok' if g['a'] else 'no'),
           (('DraftKings','—','md') if g['c'] is None else ('DraftKings','Same' if g['c'] else 'Opposite','ok' if g['c'] else 'no')),
           ('Line','Steady' if _steady(g) else 'Moved','ok' if _steady(g) else 'no')]
    grid=''.join(f'<span>{a}<b class="{c}">{v}</b></span>' for a,v,c in cells)
    fz=g.get('final'); sc=g.get('score_txt') or _score(g)
    if fz: st=f'{vs} · <span class="fin {fz["word"][0].upper()}">{fz["tag"]}</span>'
    elif sc: st=f'Final: {sc}'
    else:
        d=g['when'].split(' · '); st=(f'{vs} · ' if vs else '')+f'Kickoff {d[0]}, {d[1]}'
    mlh,_=ml_block(g)
    fz=g.get('final'); sc1=('Pass' if r=='PASS' else title+(f' · <span class="fin {fz["word"][0].upper()}">{fz["word"]} {usd(fz["usd"])}</span>' if fz else ''))
    lgs=LOGO(g['A'])+LOGO(g['H'])
    return (f'<span class="cd-1"><span class="cd-b {r}">{r}</span><span class="cd-lg">{lgs}</span><span class="cd-c">{f'{g["away"]} at {g["home"]}' if (g['gid'] in FULL or r=='PASS') else title}</span>'
            f'<span class="cd-ar">+</span></span>'
            f'{side_rows(g,sc1,trec,mlh)}<span class="cd-3">{grid}</span><span class="cd-4">{st}</span>')
def _grec(a,lab):
    return f'{lab}: {wlp(*a[:3])}, {usd(a[3])}' if a[4] else f'{lab}: no games yet'
def side_rows(g,sc1,trec,mlh):
    t=g['type']; r=g['rating']; wk=_gwk(g); key=(wk,f"{g['A']}@{g['H']}"); o=SDX.get(key,{})
    tyl=f'Type {t} · {TY[t]["name"]}'
    mlh=mlh.replace('<b class="ck">Moneyline</b>','')
    def res(x,k):
        if x.get(k+'_res'): return f' · <span class="fin {x[k+"_res"]}">{dict(W="win",L="loss",P="push")[x[k+"_res"]]} {usd(x[k+"_usd"])}</span>'
        return ''
    rows=[]
    for team in (g['A'],g['H']):
        x=next((v for v in o.values() if v['team']==team),None)
        nm=NAME[team]; mp=x['money_pct'] if x else 50
        bp=(g['ab_b'] if team==AB[g['ab_side']] else 100-g['ab_b']) if x else None
        role=x['role'] if x else None
        srt=r if (role=='fade' and r!='PASS') else 'Pass'
        tl=(f'<span class="sd-t"><span class="sdr {srt}">{srt}</span>{LOGO(team,"slg")}<b>{team}</b><small>{mp}% of the money</small>'
            '</span>')
        if role=='fade' and r!='PASS':
            spc=f'<span class="cd-2 bet bet-{r} sdc"><span class="c1">{sc1}</span><span class="c2">{tyl}</span><small class="c3">{trec}</small></span>'
            mlc=mlh.replace('class="cd-m"',f'class="cd-m bet bet-{r} sdc"' if ml_ok(g) else 'class="cd-m sdc"')   # orange = the actual bet
        elif x:
            post=sp_post(x); a=sp_grp(x,_cb(g))
            c1=f'{nm} {g["sp"].get(team,"")}'.strip()
            cls='cd-2 sdc' if role=='fade' else 'sd-sp sdc'
            spc=f'<span class="{cls}"><span class="c1 neu">{c1}</span><span class="c2">{tyl}</span><small class="c3">{_grec(a,"Group")}</small></span>'
            mp_=ml_post(x); b=ml_grp(x,_cb(g))
            m1=f'{nm} ML'
            cls='cd-m sdc' if role=='fade' else 'sd-ml sdc'
            mlc=f'<span class="{cls}"><span class="mc c1 neu">{m1}</span><span class="c2">Type {t}{" · "+FDN[x["fd"]] if x["fd"] else ""}</span><small class="c3">{_grec(b,"Group")}</small></span>'
        else:
            first=team==g['A']
            spc=f'<span class="{"cd-2 " if first else "sd-sp "}sdc"><span class="c1 neu">{f'{nm} {g["sp"].get(team,"")}'.strip()}</span><span class="c2">{tyl}</span><small class="c3">Group: even split</small></span>'
            mlc=f'<span class="{"cd-m " if first else "sd-ml "}sdc"><span class="mc c1 neu">{nm} ML</span><span class="c2">Type {t}</span><small class="c3">Group: even split</small></span>'
        _sp=g['sp'].get(team,'')
        spc=re.sub(r'^(<span class="[^"]*sdc">)',lambda m_:m_.group(1)+f'<span class="tlab">{nm} spread {_sp}</span>',spc,count=1)
        mlc=re.sub(r'^(<span class="[^"]*sdc">)',lambda m_:m_.group(1)+f'<span class="tlab">{nm} moneyline</span>',mlc,count=1)
        rows.append(f'<span class="sd-r{" pz" if srt=="Pass" else ""}">{tl}{spc}{mlc}</span>')
    h='<span class="sd"><span class="sd-h"><span></span><span>Spread</span><span>Moneyline</span></span>'+''.join(rows)+'</span>'
    def _c3(m):
        lab,val=m.group(1),m.group(2)
        val=val.replace(', ','<span class="cx">,</span> ',1)
        p0,_,rest=lab.partition(' ')
        if rest.startswith('ML'): rest='<span class="rtw">ML'+(' </span>'+rest[3:] if rest[3:] else '</span>')
        lab=(f'<span class="rtw">{p0} </span>{rest}' if rest else f'<span class="rtw">{p0}</span>') if p0 in ('STRONG','LEAN','PASS') else lab
        return f'<small class="c3 grp">{lab}<span class="cx">:</span> <span class="nw">{val}</span></small>'
    h=re.sub(r'<small class="c3">([^<:]*): ([^<]*)</small>',_c3,h)
    h=re.sub(r'<span class="c2">Type (\d) · ',r'<span class="c2"><span class="tyl">Type \1 · </span>',h)
    return h
_IX=None
def _score(g):
    global _IX
    _IX=_IX or _espn_index(); x=_IX.get((_gwk(g),g['A'],g['H']))
    return f'{g["A"]} {x["a"]}, {g["H"]} {x["h"]}' if x and x['final'] else ''
def _srows(rs,k):
    out=[]
    for x in sorted(rs,key=lambda x:(x['week'],x['game'])):
        A,H=x['game'].split('@')
        play=f"{x['team']} {('+' if x['spread_line']>0 else ('' if x['spread_line']==0 else '−'))}{abs(x['spread_line']):g}" if k=='sp' else f"{x['team']} ML"
        out.append(dict(week=x['week'],game=x['game'],play=play.replace('−','−'),score='',res=x[k+'_res'],usd=x[k+'_usd']))
    return out
def _fb(g,x):
    # final cards: groups as of posting (earlier weeks); pending cards: every graded game so far (earlier weeks + finished games this week)
    return None   # season-to-date on every card (user, Oct 15 11:10 PM); posting (ml_post/ml_ok) stays on prior weeks
def foot_pick(g):
    """display only: per market, the better of the two teams' group records ($, then win%). Returns {'sp':(side,a,ours),'ml':...}"""
    sd=SDX.get((g.get('week',5),f"{g['A']}@{g['H']}"),{}); out={}
    for k in ('sp','ml'):
        c=[]
        for x in (sd.get('fade'),sd.get('money')):
            if not x or (k=='ml' and not x['fd']): continue
            a=_sd.grp(SIDES,x['rating'],x['type'],x['role'],fd=x['fd'],ml=True,before=_fb(g,x)) if k=='ml' else _sd.grp(SIDES,x['rating'],x['type'],x['role'],before=_fb(g,x))
            if a[4]: c.append((x,a))
        if not c: continue
        x,a=max(c,key=lambda z:(r0(z[1][3]),z[1][0]/(z[1][0]+z[1][1]) if z[1][0]+z[1][1] else 0))
        ours=x['role']=='fade' and x['rating']!='PASS' and (k=='sp' or ml_ok(g))
        out[k]=(x,a,ours)
    return out
def card_lists(g):
    h=''
    for k,(x,a,ours) in foot_pick(g).items():
        tm=NAME[x['team']]; tag=x['rating'] if ours else 'Pass'
        lab=f'{tm} {"spread" if k=="sp" else "ML"} · Type {x["type"]}'+(f' · {FDN[x["fd"]]}' if k=='ml' else '')
        rs=[y for y in SIDES if y['rating']==x['rating'] and y['type']==x['type'] and y['role']==x['role'] and (k=='sp' or y['fd']==x['fd']) and y[k+'_res'] and (_fb(g,x) is None or y['week']<x['week'])]
        w,l,p,u,n=a
        h+=(f'<details class="cd-rl cd-ft{"" if ours else " cd-mn"}" data-k="{lab}" data-m="{k}" data-team="{x["team"]}" data-role="{x["role"]}" data-g="{x["week"]}|{x["game"]}">'
            f'<summary><span><span class="tg {"PASS" if not ours else x["rating"]}">{tag}</span> {lab} · <span class="ng">{n} game{"s" if n!=1 else ""}</span></span><b>{wlp(w,l,p)}, {usd(u)}</b></summary>'
            f'<ul class="rl">{_rows_html(_srows(rs,k))}</ul></details>')
    return h
def _kick(g):
    import datetime as _d
    if g.get('ko_utc'): return g['ko_utc']
    d=g['when'].split(' · '); x=_d.datetime.strptime(f"2026 {d[0].split(' ',1)[1]} {d[1].replace(' ET','')}",'%Y %b %d %I:%M %p'); return x.isoformat()
def ml_line(g):
    r=ml_for(g,g.get('week',5))
    if not r or r.get('price') is None: return ''
    tail=''
    if r.get('result'): tail=f' · {dict(W="win",L="loss",P="push")[r["result"]]} {usd(r["profit"])}'
    return f'<span class="cd-ml">Moneyline: {g["fade"]}{tail}</span>'
def ml_txt(g):
    h=ml_line(g); return re.sub('<[^>]+>','',h)
def play_card(g,ml=False):
    r=g['rating']
    return (f'<div class="cdh"><details class="gm cdw s-{r}" id="{g["gid"]}"><summary><span class="cd cdg s-{r}{' full' if g['gid'] in FULL else ''}">{card_inner(g)}</span></summary>'
            f'<div class="g-b"><div class="tbdc">'
            f'{checks(g)}</div></div></details>'+card_lists(g)+'</div>')
def pass_reason(g):
    A=AB[g['ab_side']]; D=AB[g['dk_side']]
    if g['type']==4: return f"all books {g['ab_m']}% of the money on {A}, DraftKings {g['dk_m']}% on {D}"
    if EVEN(g): return f"money split exactly 50–50 on all books; DraftKings {g['dk_m']}% on {D}"
    O=[x for x in (g['A'],g['H']) if x!=A][0]
    if g['type'] in (1,2,3) and not g['a']: return f"{g['ab_m']}% of the money on {A}, most bets on {O}"
    if g['type'] in (1,2,3): return f"{g['ab_m']}% of the money on {A}; drops below LEAN"
    return f"money split {g['ab_m']}–{100-g['ab_m']} ({A}–{O})"
_RO={'STRONG':0,'LEAN':1}
MLS6=sorted(ml_games(G6,GW),key=lambda g:_RO[g['rating']]); MLS5=sorted([g for g in ml_games(G,5) if g.get('final')],key=lambda g:_RO[g['rating']])
_up=[g for g in plays if not g.get('final')]; _fin=[g for g in plays if g.get('final')]
FINNOTE=''
ALL6=sorted(G6,key=_kick); ALL5=sorted(G,key=_kick)
WEEK=(f'<div class="sec-h"><h2>Week {GW}</h2><p class="q">{SRC6}.</p></div>'
      f'<div class="cdl">{"".join(play_card(g) for g in ALL6)}</div>'
      +f'<p class="sec-n">Text versions: <a href="tygif-week-{GW}-plays.txt">full card</a> · <a href="tygif-week-{GW}-LOCK.txt">one-page card</a> · <a href="tygif-week-{GW}-buddy.txt">short version</a> · Week {GW-1} finals are in <a href="tygif-deep-dive.html#w{GW-1}">Game by game</a></p>')
EXTRA_CSS+=CARD_CSS

# ---------- records ----------
def tier(rt,ks,cls):
    w,l,p,u,n=at(rt)
    return f'<div class="rc {cls}"><div class="rc-k">{rt}</div><div class="rc-r">{rec(w,l,p)}</div><div class="rc-m"><span class="{"pos" if u>0 else "neg"}">{usd(u)}</span> · {n} plays</div></div>'
SK=[k for k in CARD if CARD[k]['rating']=='STRONG']; LK=[k for k in CARD if CARD[k]['rating']=='LEAN']
TIERS='<div class="rgrid tiers">'+tier('STRONG',SK,'tier-s')+tier('LEAN',LK,'tier-l')+'</div>'
def cell(ks):
    if not ks: return '<td>—</td>'
    w,l,p,u,n=tally(ks); return f'<td>{rec(w,l,p)}<small class="{"pos" if u>0 else "neg"}">{usd(u)}</small></td>'
BYWEEK='<div class="tcard"><div class="tblwrap"><table class="data wk3" id="byweek"><thead><tr><th>Week</th><th>STRONG</th><th>LEAN</th></tr></thead><tbody>'
def cell2(rt,w):
    a=at(rt,None,w)
    return '<td>—</td>' if not a[4] else f'<td>{rec(*a[:3])}<small class="{"pos" if a[3]>0 else "neg"}">{usd(a[3])}</small></td>'
for w in sorted(WEEKS,reverse=True):
    BYWEEK+=f'<tr><td>Week {w}</td>'+cell2('STRONG',w)+cell2('LEAN',w)+'</tr>'
BYWEEK+='</tbody></table></div>'
def exact_usd(k):
    # stored payouts are rounded to the cent; undo that so totals are sums of exact payouts
    u=T[k]['usd']
    if T[k]['res']!='W' or u>=100: return u
    return u
_off=[]
for _rt,_ks in (('STRONG',SK),('LEAN',LK)):
    _wk=sum(round(tally([k for k in _ks if k[0]==w])[3]) for w in (1,2,3,4) if [k for k in _ks if k[0]==w]); _tot=tally(_ks)[3]
    _ex=sum(exact_usd(k) for k in _ks)
    if _wk!=round(_tot): _off.append(f'{_rt} {"+" if _ex>=0 else "−"}${abs(_ex):.2f}')
ROUND=(f'Profits are rounded to the dollar, so the weeks can be $1 off the totals (exact: {", ".join(_off)}; per-game figures rounded to the cent).' if _off else '')
BYWEEK+='</div>'
def rgtag(k):
    return ''   # catchup1: the Oct 8 regrade notes are off the site
def li(k):
    r=T[k]; rt=CARD[k]['rating']; a,h=k[1].split('@'); u=r['usd']
    cls={'W':'pos','L':'neg','P':''}[r['res']]
    rg=rgtag(k)
    return f'<li><span class="w">Week {k[0]} · {a} at {h}<i class="{rt}">{rt}</i></span><b class="{cls}">{short_play(k)} · {resword(k)} {usd(u)}</b>{rg}</li>'
TYPES=''
for t in (1,2,3,4,5):
    rows=''.join(f'<div class="gt-row"><span class="tg {rt}">{rt}</span><b>{rec(*at(rt,t)[:3])}</b><em class="{"pos" if at(rt,t)[3]>0 else ("neg" if at(rt,t)[3]<0 else "")}">{usd(at(rt,t)[3])}</em></div>' for rt in ('STRONG','LEAN') if at(rt,t)[4])
    rows+=''.join(f'<div class="gt-row"><span class="tg {rt}">{rt} ML · {FDN[fd]}</span><b>{rec(*ml_at(rt,t,fd)[:3])}</b><em class="{"pos" if ml_at(rt,t,fd)[3]>0 else ("neg" if ml_at(rt,t,fd)[3]<0 else "")}">{usd(ml_at(rt,t,fd)[3])}</em></div>' for rt in ('STRONG','LEAN') for fd in ('Fav','Dog') if ml_at(rt,t,fd)[4])
    if t in (4,5): rows='<div class="gt-row"><b class="none">PASS: see Side groups</b></div>'
    rs=[]
    lst=''.join(f'<li><span class="w">Week {r["week"]} · {r["game"].replace("@"," at ")}<i class="{r["rating"]}">{r["rating"]}</i></span><b class="{dict(W="pos",L="neg",P="")[r["res"]]}">{r["play"]} · {dict(W="win",L="loss",P="push")[r["res"]]} {usd(r["usd"])}</b></li>' for r in rs)
    TYPES+=(f'<div class="tb" id="type-{t}"><div class="tb-h"><span class="tbn">{t}</span><b>{TY[t]["name"]}</b></div>{rows}'
            +''.join(rlist(rt,t,False,'cd-rl tb-rl') for rt in ('STRONG','LEAN'))+''.join(rlist(rt,t,True,'cd-rl tb-rl',fd) for rt in ('STRONG','LEAN') for fd in ('Fav','Dog'))+'</div>')
def _lvl_noqb(k):
    r=T[k]; ms=r['money_side']; mp=r['money_pct'] or 0
    if not ms or mp<55 or r['bets_side']!=ms: return 'PASS'
    l=2 if mp>=65 else 1
    if rc.mv_toward_money(k)>1: l-=1
    return LV[max(l,0)]
_P=[k for k in T if grade(k)[0]=='PASS']
_even=[k for k in _P if not T[k]['money_side'] or T[k]['money_pct']==50]
_spl=[k for k in _P if k not in _even and T[k]['bets_side'] and T[k]['bets_side']!=T[k]['money_side']]
_pass=[k for k in _P if k not in _even and k not in _spl]
_mv=[k for k in T if T[k]['money_side'] and (T[k]['money_pct'] or 0)>=55 and T[k]['bets_side']==T[k]['money_side'] and rc.mv_toward_money(k)>1]
print('drops rows',tally(_pass),tally(_mv))
_ty={t:tally([k for k in T if T[k]['type']==t]) for t in (1,2,3,5)}
assert [_ty[t][:3] for t in (1,2,3,5)]==[(10,3,1),(6,2,2),(13,14,1),(4,6,0)]
def _drow(lbl,ks):
    w,l,p,u,n=tally(ks); return f'<tr><td>{lbl}</td><td>{rec(w,l,p)}<small class="{"pos" if u>0 else "neg"}">{usd(u)}</small></td><td>{n}</td></tr>'
DROPS=('<div class="tcard" id="drops"><div class="tblwrap"><table class="data wk3"><thead><tr><th>Group</th><th>Record</th><th>Games</th></tr></thead><tbody>'
       +_drow('PASS games without a money-vs-bets split',_pass)+_drow('Dropped a level: line moved over 1 pt toward the money',_mv)
       +'</tbody></table></div><p>Every game by type: '+' · '.join(f'Type {t}: {rec(*_ty[t][:3])}' for t in (1,2,3,5))+' (NYJ@CHI and MIA@SF at exactly even money, not graded). Type 4 can only be spotted from Week 5: Weeks 1–4 saved one split per game.</p></div>')
N4=sum(g['type']==4 for g in G6)
LR=live_rows()
def _lrec(rt):
    rs=[r for r in LR if r['rating']==rt and live_profit(r) is not None]
    if not rs: return f'<div class="gt-row"><span class="tg {rt}">{rt}</span><b class="none">no results yet</b></div>'
    w=sum(r['result'].upper().startswith('W') for r in rs); l=sum(r['result'].upper().startswith('L') for r in rs); p=len(rs)-w-l
    u=sum(live_profit(r) for r in rs)
    return f'<div class="gt-row"><span class="tg {rt}">{rt}</span><b>{rec(w,l,p)}</b><em class="{"pos" if u>0 else ("neg" if u<0 else "")}">{usd(u)}</em></div>'
def _num(v):
    return float(v.replace('\u2212','-')) if v and v.strip() else None
def _lrow(r):
    pl=r['posted_line']; pr=r['posted_price'].replace('-','−'); cl=r.get('closing_line') or ''
    cp=(r.get('closing_price') or '').replace('-','−')
    res=live_profit(r)
    rs='pending' if res is None else f'{ {"W":"win","L":"loss","P":"push"}[r["result"].upper()[:1]]} {usd(res)}'
    return (f'<tr><td>W{r["week"]} {r["game"]}<small>{r["rating"]} · posted {r["posted_at_et"].split(" ",1)[1]} ET</small></td>'
            f'<td>{r["our_side"]} {pl.replace("-","−")}</td><td>{cl.replace("-","−") if cl else "—"}</td><td>{rs}</td></tr>')
_closed=[r for r in LR if _num(r.get('closing_line'))is not None]
_beat=sum(_num(r['posted_line'])>_num(r['closing_line']) for r in _closed)
def _m(v): return (v or '').strip().replace('-','−')
def _lineprice(r):
    if (r.get('closing_line') or '').strip(): return f'{r["our_side"]} {_m(r["closing_line"])}', 'at the close'
    return f'{r["our_side"]} {_m(r["posted_line"])}', f'posted {_posted_ct(r["posted_at_et"])} · close pending'
def _pline(r):
    res=live_profit(r); lp,lab=_lineprice(r)
    tail='pending' if res is None else f'{ {"W":"win","L":"loss","P":"push"}[r["result"].upper()[:1]]} {usd(res)}'
    return (f'<div class="lv"><span class="tg {r["rating"]}">{r["rating"]}</span><b>{lp}</b><em>{lab if res is None else lab+' · '+tail}</em></div>'
            '')
def _hl(r):
    res=live_profit(r); lp,_=_lineprice(r)
    tail='pending' if res is None else f'{ {"W":"win","L":"loss","P":"push"}[r["result"].upper()[:1]]} {usd(res)}'
    return f'{lp}, {tail}'
HOMELIVE='Live · '+('; '.join(_hl(r) for r in LR) if LR else 'no plays yet')
_beatline=f'Our posted line beat the closing line: {_beat} of {len(_closed)} (for information; plays are graded at the close).'
def _lsum(rt):
    rs=[r for r in LR if r['rating']==rt and live_profit(r) is not None]
    w=sum(r['result'].upper().startswith('W') for r in rs); l=sum(r['result'].upper().startswith('L') for r in rs); p=len(rs)-w-l
    return f'{rt} {rec(w,l,p)}'+(f', {usd(sum(live_profit(r) for r in rs))}' if rs else '')
LIVESUM=_lsum('STRONG')+' · '+_lsum('LEAN')
LIVE=(f'<h3 class="sh" id="live">Live · from Week 5</h3><p class="lsum">{LIVESUM}</p>'
      +''.join(_pline(r) for r in LR)
      )
def _mlrow(rt,st):
    w,l,p,u,n=ml_tally(rt,st)
    if not n: return f'<div class="gt-row"><span class="tg {rt}">{rt}</span><b class="none">no results yet</b></div>'
    return f'<div class="gt-row"><span class="tg {rt}">{rt}</span><b>{rec(w,l,p)}</b><em class="{"pos" if u>0 else ("neg" if u<0 else "")}">{usd(u)}</em></div>'
def _mlgrp(rt,t,fd):
    a=ml_at(rt,t,fd)
    if not a[4]: return ''
    return rlist(rt,t,True,'cd-rl tb-rl',fd)
MLGROUPS=[(rt,t,fd) for rt in ('STRONG','LEAN') for t in (1,2,3) for fd in ('Dog','Fav') if ml_at(rt,t,fd)[4]]
MLREC=('<h3 class="sh" id="moneyline">Moneyline · tracking</h3>'+_mlrow('STRONG',('look back','live'))+_mlrow('LEAN',('look back','live'))
       +'<div class="mlg">'+''.join(_mlgrp(*k) for k in MLGROUPS)+'</div>')
RULES=('<div class="rules" id="rules"><h4>Rules v3 · Oct 15, 2026</h4>'
  '<p>Rules v3: both sides of every game are tracked. The money side and PASS-game sides are tracked for trends only, never a play.</p>'
  '<p>Changed Oct 15: the quarterback factor is removed. Every game in Weeks 1–6 is rated without it.</p>'
  '<p>Changed Oct 8: the all-books gate (65%+ of the money on the all-sportsbooks split, DraftKings money on the same side), strict regrades of Weeks 1–4, and the start-of-week line restatement.</p>'
  '<ul><li><b class="tg STRONG">STRONG</b> 12 wins, 0 losses, 3 pushes (+$1,095) at the start of Oct 8 → 11 wins, 1 loss, 3 pushes (+$899) after the gate and regrades → '+f'{rec(*tally(SK)[:3])} ({usd(tally(SK)[3])}) now.</li>'
  '<li><b class="tg LEAN">LEAN</b> 11 wins, 9 losses, 1 push (+$101) → 9 wins, 8 losses, 1 push (+$32) → '+f'{rec(*tally(LK)[:3])} ({usd(tally(LK)[3])}) now.</li></ul>'
  '</div>')
FINE=(f'<details class="fine" id="fine"><summary>Fine print</summary>'
   f'<h4>Passes and drops · Weeks 1–4</h4>{DROPS}'
   f'<p>Weeks 1–4 used splits from near kickoff and couldn’t check DraftKings. This week that check is what passes {N4} of the {len(passes6)} games we passed, so live results may differ.</p>'
   +''.join(f'<p>{g["A"]}@{g["H"]}: {E(g["dk_note"])}</p>' for g in G if g.get('dk_note') and g['rating']!='PASS')
   +''.join(f'<p>{r["game"]} was posted at {r["our_side"]} {_m(r["posted_line"])} at {r["posted_at_et"].split(" ",1)[1]} ET.</p>' for r in LR)+
   f'<p>{ROUND}</p>'
   f'<p>{_beatline} Weeks 1–4 are a look back: today’s rules applied afterward to the same 64 games, graded at the DraftKings closing price. Not live bets.</p>'
   f'</details>')
def _wl(w,l,p):
    return f'<span class="wl" aria-hidden="true"><i class="w" style="flex:{w}"></i><i class="p" style="flex:{p}"></i><i class="l" style="flex:{l}"></i></span>'
def _pb(u,mx):
    x=min(100,abs(u)/mx*100) if mx else 0
    return (f'<span class="pb" aria-hidden="true"><span class="pn">{f"<i style=width:{x:.0f}%></i>" if u<0 else ""}</span>'
            f'<span class="pp">{f"<i style=width:{x:.0f}%></i>" if u>0 else ""}</span></span>')
def _tile(rt,a,cls,idattr=''):
    w,l,p,u,n=a
    return (f'<div class="rc {cls}"{idattr}><div class="rc-k"><span class="tg {rt}">{rt}</span></div><div class="rc-r">{rec(w,l,p)}</div>'
            f'<div class="rc-m"><span class="{"pos" if u>0 else "neg"}">{usd(u)}</span> · {n} plays</div>{_wl(w,l,p)}</div>')
def _mltile(rt):
    w,l,p,u,n=ml_tally(rt,('look back','live'))
    return (f'<div class="gt-row rc"><span class="tg {rt}">{rt}</span><b class="rc-r">{rec(w,l,p)}</b>'
            f'<div class="rc-m"><em class="{"pos" if u>0 else ("neg" if u<0 else "")}">{usd(u)}</em> · {n} games</div>{_wl(w,l,p)}</div>')
_GMX=max(abs(ml_at(*k)[3]) for k in MLGROUPS)
def _grow(rt,t,fd):
    w,l,p,u,n=ml_at(rt,t,fd)
    return (f'<div class="grow"><span class="tg {rt}">{rt}</span><span class="gl">Type {t} · {FDN[fd]}</span><b>{wlp(w,l,p)}</b>'
            f'{_pb(u,_GMX)}<em class="{"pos" if u>0 else ("neg" if u<0 else "")}">{usd(u)}</em></div>'+rlist(rt,t,True,'cd-rl gr-rl',fd))
def _mlwk(rt,w):
    rs=[r for r in ML if r['rating']==rt and r['week']==w and r.get('profit') is not None]
    if not rs: return '<td>—</td>'
    ww=sum(r['result']=='W' for r in rs); ll=sum(r['result']=='L' for r in rs); pp=len(rs)-ww-ll
    return f'<td>{rec(ww,ll,pp)}<small class="{"pos" if sum(r["profit"] for r in rs)>0 else "neg"}">{usd(sum(r["profit"] for r in rs))}</small></td>'
_WMX=max([abs(at(rt,None,w)[3]) for rt in ('STRONG','LEAN') for w in WEEKS]+[1])
def _wcell(rt,w):
    a=at(rt,None,w)
    if not a[4]: return '<td>—</td>'
    return f'<td>{rec(*a[:3])}<small class="{"pos" if a[3]>0 else "neg"}">{usd(a[3])}</small>{_pb(a[3],_WMX)}</td>'
BYWEEK2=('<div class="tblwrap"><table class="data wk3" id="byweek"><thead><tr><th>Week</th><th>Spread STRONG</th><th>Spread LEAN</th><th>ML STRONG</th><th>ML LEAN</th></tr></thead><tbody>'
    +''.join(f'<tr><td>Week {w}</td>{_wcell("STRONG",w)}{_wcell("LEAN",w)}{_mlwk("STRONG",w)}{_mlwk("LEAN",w)}</tr>' for w in sorted(WEEKS,reverse=True))
    +'</tbody></table></div>')
def _stally(role,rt,ml=False):
    k='ml' if ml else 'sp'; rs=[x for x in SIDES if x['role']==role and x['rating']==rt and x[k+'_res']]
    return (sum(x[k+'_res']=='W' for x in rs),sum(x[k+'_res']=='L' for x in rs),sum(x[k+'_res']=='P' for x in rs),sum(x[k+'_usd'] for x in rs),len(rs))
def _stile(role,rt,ml):
    w,l,p,u,n=_stally(role,rt,ml)
    return (f'<div class="rc sdt" data-k="{role}|{rt}|{"ml" if ml else "sp"}"><div class="rc-k"><span class="tg {rt}">{rt}</span> · {"Moneyline" if ml else "Spread"}</div><div class="rc-r">{wlp(w,l,p)}</div>'
            f'<div class="rc-m"><span class="{"pos" if u>0 else "neg"}">{usd(u)}</span> · {n} games</div>{_wl(w,l,p)}</div>')
_SGK=sorted({(x['rating'],x['type'],x['role']) for x in SIDES if not (x['role']=='fade' and x['rating']!='PASS')},key=lambda k:(k[2],['STRONG','LEAN','PASS'].index(k[0]),k[1]))
_SMX=max([abs(_sd.grp(SIDES,*k)[3]) for k in _SGK]+[abs(_sd.grp(SIDES,*k,fd=fd,ml=True)[3]) for k in _SGK for fd in ('Fav','Dog')]+[1])
def _sgrow(k,fd=None):
    ml=fd is not None; a=_sd.grp(SIDES,*k,fd=fd,ml=ml)
    if not a[4]: return ''
    rs=[x for x in SIDES if (x['rating'],x['type'],x['role'])==k and (not ml or x['fd']==fd) and x[('ml' if ml else 'sp')+'_res']]
    lab=f'{k[0]} {k[2]}{" ML" if ml else ""} · Type {k[1]}{" · "+FDN[fd] if ml else ""}'
    w,l,p,u,n=a
    return (f'<div class="grow" data-k="{lab}"><span class="tg {k[0]}">{k[0]}</span><span class="gl">{k[2].capitalize()} · {"ML · " if ml else ""}Type {k[1]}{" · "+FDN[fd] if ml else ""}</span><b>{wlp(w,l,p)}</b>'
            f'{_pb(u,_SMX)}<em class="{"pos" if u>0 else ("neg" if u<0 else "")}">{usd(u)}</em></div>'
            f'<details class="sd-rl gr-rl" data-k="{lab}"><summary><span>{lab} · <span class="ng">{n} game{"s" if n!=1 else ""}</span></span><b>{wlp(w,l,p)}, {usd(u)}</b></summary><ul class="rl">{_rows_html(_srows(rs,"ml" if ml else "sp"))}</ul></details>')
SIDEREC=(f'<h3 class="sh" id="trends">Trend tracking · not bets</h3><p class="sub">The money side (the team holding most of the money) and both sides of PASS games are tracked for trends only. They are never plays.</p><h3 class="sh" id="moneyside">Money side · tracking</h3>'
   f'<div class="rgrid r3">{"".join(_stile("money",rt,False) for rt in ("STRONG","LEAN","PASS"))}{"".join(_stile("money",rt,True) for rt in ("STRONG","LEAN","PASS"))}</div>'
   f'<h3 class="sh" id="passfade">PASS games · fade side · tracking</h3><p class="sub">The team against the money in a PASS game. Tracking only.</p>'
   f'<div class="rgrid">{_stile("fade","PASS",False)}{_stile("fade","PASS",True)}</div>'
   f'<h3 class="sh" id="sidegroups">Side groups · tracking</h3><div class="groups">{"".join(_sgrow(k) for k in _SGK)}{"".join(_sgrow(k,fd) for k in _SGK for fd in ("Fav","Dog"))}</div>')
def _pt(xs,k):
    return (sum(x[k+'_res']=='W' for x in xs),sum(x[k+'_res']=='L' for x in xs),sum(x[k+'_res']=='P' for x in xs),sum(x[k+'_usd'] for x in xs),len(xs))
_GR=[x for x in SIDES if x['sp_res']]
_OUR=lambda x:x['role']=='fade' and x['rating']!='PASS'
POSTED={'sp|STRONG':_pt([x for x in _GR if _OUR(x) and x['rating']=='STRONG'],'sp'),'sp|LEAN':_pt([x for x in _GR if _OUR(x) and x['rating']=='LEAN'],'sp'),
        'ml|STRONG':_pt([x for x in _GR if _OUR(x) and x['rating']=='STRONG' and ml_post(x)],'ml'),'ml|LEAN':_pt([x for x in _GR if _OUR(x) and x['rating']=='LEAN' and ml_post(x)],'ml'),
}
def _ptile(k,lab,tag):
    w,l,p,u,n=POSTED[k]
    return (f'<div class="rc pst" data-k="{k}"><div class="rc-k">{tag}{lab}</div><div class="rc-r">{wlp(w,l,p)}</div>'
            f'<div class="rc-m"><span class="{"pos" if u>0 else "neg"}">{usd(u)}</span> · {n} posted</div>{_wl(w,l,p)}</div>')
POSTREC=(f'<h3 class="sh" id="posted">As posted</h3><p class="sub">What actually posted each week: our STRONG and LEAN spread calls, plus our moneyline when its group was above $0 from earlier weeks.</p>'
   f'<div class="rgrid r3">{_ptile("sp|STRONG"," · Spread","<span class=\"tg STRONG\">STRONG</span>")}{_ptile("sp|LEAN"," · Spread","<span class=\"tg LEAN\">LEAN</span>")}'
   f'{_ptile("ml|STRONG"," · Moneyline","<span class=\"tg STRONG\">STRONG</span>")}{_ptile("ml|LEAN"," · Moneyline","<span class=\"tg LEAN\">LEAN</span>")}'
   f'</div>'
   f'<p class="sub">Everything below is tracking: every graded side, posted or not.</p>')
# season breakdown: every completed game in exactly one bucket
_DONE=[(x['week'],f"{x['A']}@{x['H']}") for x in _SG if x['week']<=5 or (x['week'],f"{x['A']}@{x['H']}") in FINW]
_EVEN={(w_,g_) for w_,g_,_ in SFLAGS}
def _bucket(k):
    o=SDX.get(k,{}); f=o.get('fade')
    if f and _ours(f): return 'both' if ml_post(f) else 'spread'
    return 'pass_money' if k not in _EVEN and o.get('money') else 'pass_even'
BUCKETS={b:[k for k in _DONE if _bucket(k)==b] for b in ('spread','ml','both','pass_money','pass_even')}
def _brec(ks,rt,k,role='fade'):
    xs=[SDX[x][role] for x in ks if x in SDX and SDX[x][role]['rating']==rt] if rt else [SDX[x][role] for x in ks if x in SDX]
    xs=[x for x in xs if x[k+'_res']]
    if not xs: return '—'
    w,l,p,u,_=_pt(xs,k); return f'{wlp(w,l,p)} <small class="{"pos" if u>0 else "neg"}">{usd(u)}</small>'
def _brow(lab,b,cells):
    return f'<tr data-b="{b}"><td>{lab}</td><td class="num">{len(BUCKETS[b])}</td>{cells}</tr>'
SEASON=('<h3 class="sh" id="season">Season breakdown</h3><p class="sub">Every completed game, Weeks 1 to '+str(max(w for w,_ in _DONE))+', in exactly one row.</p>'
  '<div class="tblwrap"><table class="data season"><thead><tr><th>Games</th><th>Count</th><th>STRONG</th><th>LEAN</th></tr></thead><tbody>'
  +_brow('Spread play only','spread',f'<td>Spread {_brec(BUCKETS["spread"],"STRONG","sp")}</td><td>Spread {_brec(BUCKETS["spread"],"LEAN","sp")}</td>')
  +_brow('Moneyline play only','ml','<td>—</td><td>—</td>')
  +_brow('Spread + moneyline play','both',f'<td>Spread {_brec(BUCKETS["both"],"STRONG","sp")}<br>ML {_brec(BUCKETS["both"],"STRONG","ml")}</td><td>Spread {_brec(BUCKETS["both"],"LEAN","sp")}<br>ML {_brec(BUCKETS["both"],"LEAN","ml")}</td>')
  +_brow('Pass · money-side trend tracked','pass_money',f'<td colspan="2"><span class="tg trk">Tracking · not bets</span><span class="nw bl">Spread {_brec(BUCKETS["pass_money"],None,"sp","money")}</span><span class="nw bl">ML {_brec(BUCKETS["pass_money"],None,"ml","money")}</span></td>')
  +_brow('Pass · no clear side','pass_even','<td colspan="2">—</td>')
  +f'<tr class="tot"><td><b>Total games played</b></td><td class="num"><b>{len(_DONE)}</b></td><td colspan="2"></td></tr></tbody></table></div>')
RESULTS=(f'<div class="sec-h" id="audit"><h2>Records</h2><p class="sub">Weeks 1 to {max(x["week"] for x in SIDES if x["sp_res"])}, flat $100 a bet at the DraftKings close. Fade side = against the money (our STRONG and LEAN calls). Money side = with the money, tracked for trends only, never a play.</p></div>'
   f'{POSTREC}{SEASON}'
   f'<div class="rgrid"><h3 class="sh">Spread · all calls</h3>{_tile("STRONG",at("STRONG"),"tier-s")}{_tile("LEAN",at("LEAN"),"tier-l")}</div>'
   f'<div class="rgrid"><h3 class="sh" id="moneyline">Moneyline · tracking</h3>{_mltile("STRONG")}{_mltile("LEAN")}</div>'
   f'<h3 class="sh" id="mlgroups">Moneyline by group</h3><p class="sub">An ML play is posted only when its group is above $0 from earlier weeks.</p>'
   f'<div class="groups">{"".join(_grow(*k) for k in MLGROUPS)}</div>'
   f'{SIDEREC}'
   f'<h3 class="sh">By week</h3>{BYWEEK2}'
   f'<h3 class="sh" id="types">By game type</h3><div class="types">{TYPES}</div>'
   f'<p class="sub fine-s">Weeks 1–4: all-books splits only; DraftKings split not recorded.</p>'
   f'<p class="allg"><a href="tygif-deep-dive.html">Game by game</a><a href="tygif-games-archive.html">All games</a></p>')

# ---------- tracker assemble ----------
s=BeautifulSoup(rd('tygif-tracker.html'),'html.parser')
OLDIDS=set()
for pid in ('results','research'):
    p=s.find(id=pid)
    if p: OLDIDS|={e['id'] for e in p.find_all(id=True)}|{pid}
s.find(id='week').clear(); s.find(id='week').append(BeautifulSoup(WEEK,'html.parser'))
s.find(id='results').clear(); s.find(id='results').append(BeautifulSoup(RESULTS,'html.parser'))
s.find(id='research').decompose()
s.find('footer').string=FOOT
st=s.new_tag('style',id='clean1-css'); st.string=EXTRA_CSS; s.head.append(st)
x=str(s)
x=NAVRE.sub(nav('week',tracker=True),x,count=1)
NEWIDS=set(re.findall(r'id="([^"]+)"',x))
ALIAS=sorted(i for i in OLDIDS if i not in NEWIDS)
js_alias='var OLD = '+json.dumps(ALIAS)+';\n  function fix(id){ return OLD.indexOf(id) >= 0 ? \'results\' : id; }\n'
x=x.replace("  var boot = (location.hash || '#week').slice(1);", "  "+js_alias+"  var boot = fix((location.hash || '#week').slice(1));")
x=x.replace("go(location.hash.slice(1) || 'week', false)","go(fix(location.hash.slice(1)) || 'week', false) || go('week', false)")
assert 'fix(' in x
wr('tygif-tracker.html',x)
TRACKER_CSS=''.join(re.findall(r'<style[^>]*>.*?</style>',x,re.S))
print('aliases',len(ALIAS),ALIAS[:50])

def page(title, cur, body, extra_head=''):
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title>{TRACKER_CSS}{extra_head}</head><body>'
            '<header class="apphead"><a class="logo" href="index.html">tygif\'s model</a></header>'
            f'{nav(cur)}<main>{body}</main><footer>{FOOT}</footer></body></html>\n')

# ---------- index ----------
ix=rd('index.html')
head=ix[:ix.index('</head>')]
HOME=(f'<div class="wrap">\n  <h1>Week {GW}</h1>\n'
      f'  <p class="q">{SRC6}.</p>\n'
      f'  <div class="cdl">{"".join(play_card(g) for g in ALL6)}</div>\n'
      +f'  <nav class="hl"><a href="tygif-tracker.html#results">Records <span>›</span></a><a href="tygif-how.html">How it works <span>›</span></a>'
      f'<a href="tygif-week-{GW}-plays.txt">Week {GW} card as text <span>›</span></a><a href="tygif-week-{GW}-buddy.txt">Short version to share <span>›</span></a></nav>\n'
      f'  <footer>{FOOT}</footer>\n</div>\n')
lockcss='<style>.hfin{font-size:13px;letter-spacing:.12em;text-transform:uppercase;color:var(--mut);margin:26px 0 8px;font-family:inherit}.hl{display:grid;margin:26px 0 8px;border-top:1px solid var(--line)}.hl a{display:flex;justify-content:space-between;padding:14px 2px;border-bottom:1px solid var(--line);color:var(--txt);text-decoration:none;font-weight:600;font-size:15px}.hl a span{color:var(--mut)}.pf{display:block;font-size:13px;font-weight:700;color:#3fae6c;margin:2px 0}.lockline{margin:18px 0;font-size:14px;line-height:1.45;color:var(--mut)}.lockline a{color:#d4a017}.rc-m .neg{color:#e07a7a}.allg{margin:14px 0 22px;font-size:15px}.allg a{color:var(--accent);font-weight:650;text-decoration:none;border-bottom:1px solid rgba(212,160,23,.4)}.rgrid.tiers{gap:0;margin:0}.rc,.rc.tier-s,.rc.tier-l{background:transparent;border:0;border-bottom:1px solid var(--line);padding:16px 2px 14px}.rc-r,.rc.tier-s .rc-r,.rc.tier-l .rc-r{font-size:23px;font-weight:800;letter-spacing:-.4px;white-space:nowrap;margin:6px 0 4px}.rc-m{font-size:14px}</style>'
wr('index.html',head+lockcss+'<style>'+CARD_CSS+'</style>'+'</head>\n<body>\n<header class="apphead"><a class="logo" href="index.html">tygif\'s model</a></header>\n'+nav('index')+'\n'+HOME+'</body>\n</html>\n')

# ---------- how ----------
HOW=f'''<div class="hw">
<h1>How it works</h1>
<h2>The rule</h2>
<ul>
<li>Fade side: the team against most of the money. Our STRONG and LEAN spread calls are always the fade side.</li>
<li>Money side: the team holding most of the money (tracking only).</li>
<li>The money side is tracked for trends only. It is never a play.</li>
<li>Spreads and moneylines, favorite or underdog.</li>
<li>Money and bets: all books (ScoresAndOdds). DraftKings must have the money on the same team.</li>
</ul>
<h2>Game types</h2>
<p class="sm">Checked in this order: 4, 5, 1, 2, 3.</p>
<ol>
<li><b>{TY[1]['name']}:</b> 65%+ of the money on a favorite giving 6+ points. Take the underdog.</li>
<li><b>{TY[2]['name']}:</b> 65%+ of the money and most bets on one team. Take the other team.</li>
<li><b>Crowd leaning:</b> 55–64% of the money on one team. LEAN at most; money and bets on different teams is a pass.</li>
<li><b>Type 3 underdog:</b> pass on the moneyline; spread unaffected.</li>
<li><b>Grading:</b> Every game is graded at the DraftKings line, price and moneyline we recorded last before kickoff; where nothing was recorded, at the DraftKings closing numbers.</li>
<li><b>Books disagree:</b> all books and DraftKings have the money on different teams. PASS.</li>
<li><b>No clear crowd:</b> under 55% of the money on either team. PASS.</li>
</ol>
<h2>Ratings</h2>
<ul>
<li><b>STRONG:</b> 65%+ of the money, most bets on the same team, DraftKings money on the same team (its bets need not agree).</li>
<li><b>LEAN:</b> 55–64% of the money, or a STRONG that drops one level.</li>
<li><b>PASS:</b> types 4 and 5, money and bets on different teams, or a LEAN that drops.</li>
<li><b>Drop one level</b> if the line moves more than 1 point toward the money from the Monday line This never changes the type.</li>
<li><b>Monday line:</b> average of TeamRankings books 2 and 3, each book’s last quote before Monday 12:00 AM ET (quotes older than 7 days skipped).</li>
</ul>
<h2>Moneyline</h2>
<ul>
<li>Same team as every STRONG or LEAN play, favorite or underdog, graded at the DraftKings moneyline recorded before kickoff.</li>
<li>Grouped by rating, type, and favorite or underdog. Posted only when that group has a profitable moneyline record to date.</li>
<li>A tie on the moneyline is a push, $0.</li>
</ul>
<h2 id="records">Records</h2>
<ul>
<li>Flat $100 per play, graded at the DraftKings line and price recorded before kickoff. A loss is −$100; a push is $0.</li>
<li>Every week to date. STRONG, LEAN, PASS, fade side, money side and moneyline are kept separate, never combined.</li>
<li>Weeks 1–4: all-books splits only; DraftKings split not recorded.</li>
<li>Rules v3 · Oct 15, 2026: both sides of every game tracked, grouped by rating, type and side (fade/money; moneyline also favorite/underdog). Plays are only our STRONG/LEAN spread calls and our moneyline on the same team, posted when its group is above $0 from earlier weeks. The money side and PASS-game sides are tracked for trends only and are never a play. If both teams qualify on the spread, only our original call posts.</li>
</ul>
<h2>Sources</h2>
<p class="sm">ScoresAndOdds · DraftKings · TeamRankings · ESPN · nflverse</p>
</div>'''
wr('tygif-how.html',page("tygif's model · How it works",'how',HOW))
print('index/how ok')

# ---------- deep dive ----------
import datetime
def kick(k):
    a=ARCH[k]; d=datetime.date.fromisoformat(a['Date']); t=a['Kickoff (ET)'].split(' ',1)[1].replace(' ET','')
    hh,rest=t.split(':'); return f"{d.strftime('%a %b')} {d.day} · {int(hh)}:{rest} ET"
def why(k):
    r=T[k]; ms=r['money_side']; mp=int(r['money_pct'] or 0); t=r['type']
    rt,steps=grade(k)
    if not ms: return 'The money was split evenly. Type 5: no clear crowd, so no bet.'
    MS=NAME[ms]
    if mp<55: return f'{MS} had {mp}% of the money, under 55%. Type 5: no clear crowd, so no bet.'
    bp=bets_pct(k)
    if not r['bets_side']:
        return f'{MS} had {mp}% of the money, but the bets were split evenly, so money and bets aren’t on the same side. No bet.'
    if r['bets_side']!=ms:
        return f'{MS} had {mp}% of the money, but most bets ({bp}%) were on {NAME[r["bets_side"]]}. Money and bets on different sides, so no bet.'
    start='STRONG' if mp>=65 else 'LEAN'
    out=f'{MS} had {mp}% of the money and {bp}% of the bets. Type {t}: {TY[t]["name"].lower()}.'
    if start=='LEAN' and not steps: out+=' Under 65% of the money, so LEAN.'
    if steps:
        out+=f' Starts at {start}.'
        for kind,v in steps:
            if kind=='move': out+=f' The line moved {v:g} points toward {MS} from the Monday line: down one level.'
            else: out+=f' {v[0]} started for {NAME[r["side"]]} instead of QB1 {v[1]}: down one level.'
        out+=f' Rated {rt}.' if rt!='PASS' else ' That makes it a PASS.'
    return out
ORD={'STRONG':0,'LEAN':1,'PASS':2}
def w14_g(k):
    r=T[k]; a=ARCH[k]; A,H=k[1].split('@'); w=k[0]
    fav=a['Favorite']; fl=float(a['Spread']); dog=a['Underdog']
    sp={fav:ln(fl),dog:ln(-fl)} if fl else {A:'PK',H:'PK'}
    ms=r['money_side'] if (r['money_pct'] or 0)>50 else ''
    abs_=ms or H; m=int(r['money_pct'] or 50)
    fb=float(a['Fav bet % (spread)'].rstrip('%')); bb=round(fb if abs_==fav else 100-fb)
    rt=CARD[k]['rating'] if k in CARD else 'PASS'
    side=r['side'] if rt!='PASS' else (dog if abs_==fav else fav)
    mon=MONDAY[k]; mv=rc.mv_toward_money(k) if ms else 0
    sc=r['score'].replace(',','').split(); sa,sh=int(sc[1]),int(sc[3])
    d0=_dt.date.fromisoformat(a['Date']); ko=a['Kickoff (ET)'].split()
    g=dict(gid=f'w{w}-{A.lower()}-{H.lower()}',week=w,A=A,H=H,away=NAME[A],home=NAME[H],sp=sp,ab_side=NAME[abs_],ab_m=m,ab_b=bb,
           dk_side=None,dk_m=None,dk_b=None,a=(r['bets_side']==ms) if ms else bb>=50,b=m>=65,c=None,
           d=bool(ms) and ms==fav and fl<=-6,e=mv>1,f=k in QBD,fade=NAME[side],fade_line=float(sp[side].replace(M,'-').replace('PK','0')),
           rating=rt,type=r['type'],why='',when=f"{ko[0]} {d0.strftime('%b')} {d0.day} · {int(ko[1][:2])}:{ko[1][3:]} {ko[2]} ET",
           mon=dict(team=fav,b2=mon['book2_fav'] if mon['book2_fav'] is not None else mon['book3_fav'],b3=mon['book3_fav'] if mon['book3_fav'] is not None else mon['book2_fav'],avg=mon['monday_line_fav']),
           qbnote='',split_at='closing',
           score_txt=f'{A} {sa}, {H} {sh}',src=dict(SRC_W14))
    g['call']=f"{g['fade']} {sp[side]}"
    if rt!='PASS':
        x,y=(sa,sh) if side==A else (sh,sa); word={'W':'win','L':'loss','P':'push'}[r['res']]
        g['final']=dict(word=word,usd=r['usd'],score=f'{sa}-{sh}',a=str(sa),h=str(sh),tag=f"Final: {side} {x}–{y} · {word} {usd(r['usd'])}")
    return g
G14=[w14_g(k) for k in T]
DD=(f'<div class="sec-h"><h2>Game by game</h2></div>{TIERS}')
CS=json.load(open(R+'data/closing_splits.json'))
_DDW=[w for w in reversed(LIVEW) if any(g['final'] for g in GBY[w])]   # weeks 6 on: finished games only
for w in _DDW+[5,4,3,2,1]:
    gs=sorted([g for g in GBY[w] if g['final']] if w>=6 else G if w==5 else [g for g in G14 if g['week']==w],key=_kick)
    DD+=(f'<details class="fold" id="w{w}"{" open" if w==(_DDW+[5])[0] else ""}><summary><span class="ft">Week {w}</span>'
         f'<span class="fs">{len(gs)} game{"s" if len(gs)!=1 else ""}<br>STRONG: {rec(*at("STRONG",None,w)[:3])}, {usd(at("STRONG",None,w)[3])}<br>LEAN: {rec(*at("LEAN",None,w)[:3])}, {usd(at("LEAN",None,w)[3])}</span></summary>'
         f'<div class="fold-b cdl">{"".join(play_card(g) for g in gs)}</div></details>')
wr('tygif-deep-dive.html',page("tygif's model · Game by game",'results',DD))

# ---------- archive ----------
ar=rd('tygif-games-archive.html')
def th(cols):
    return '<thead><tr>'+''.join(f'<th class="sortable{" num" if i else ""}" data-col="{i}">{c}</th>' for i,c in enumerate(cols))+'</tr></thead>'
COLS=['Game','Kickoff','Line','Score','Covered','Money','Bets','Type','Play','Result']
def _sideplays(w,game):
    out=[]
    for x in SDX.get((w,game),{}).values():
        if x['role']=='fade' and x['rating']!='PASS':
            if ml_post(x): out.append(f"{x['team']} ML")
            continue
        if sp_post(x):
            v=x['spread_line']; out.append(f"{x['team']} {'PK' if v==0 else ('+' if v>0 else '−')+format(abs(v),'g')} ({x['role']})")
        if ml_post(x): out.append(f"{x['team']} ML ({x['role']})")
    return ''.join(f'<br><small>{p}</small>' for p in out)
def _mlres(w,game):
    for x in SDX.get((w,game),{}).values():
        if x['role']=='fade' and x['rating']!='PASS' and ml_post(x) and x.get('ml_res'):
            return f'<br><small>ML {dict(W="win",L="loss",P="push")[x["ml_res"]]} {usd(x["ml_usd"])}</small>'
    return ''
def _ascore(k,a):
    # same score format everywhere: 'AWAY a, HOME h' (ESPN final); archive source only if ESPN lacks the game
    global _IX
    _IX=_IX or _espn_index(); A,H=[_sg0.ALIAS.get(t,t) for t in k[1].split('@')]; x=_IX.get((k[0],A,H))
    return f'{A} {x["a"]}, {H} {x["h"]}' if x and x['final'] else a['Score']
def arow(k):
    r=T[k]; a=ARCH[k]; rt=CARD[k]['rating'] if k in CARD else 'PASS'
    money=f"{r['money_side']} {int(r['money_pct'])}%" if r['money_side'] else 'Even'
    bets=f"{r['bets_side']} {bets_pct(k)}%" if r['bets_side'] else 'Even'
    call=(f'<b class="tg {rt}">{rt}</b> {short_play(k)}' if rt!='PASS' else '<b class="tg PASS">PASS</b>')+_sideplays(k[0],k[1])
    res=f'{resword(k)} {usd(r["usd"])}'+_mlres(k[0],k[1]) if rt!='PASS' else '—'
    cls={'W':'pos','L':'neg'}.get(r['res'],'') if rt!='PASS' else ''
    return (f'<tr data-final="1"><td>{a["Game"]}</td><td>{kick(k).replace(" ET","")}</td><td>{a["Line"]}</td><td>{_ascore(k,a)}</td><td>{a["Cover"]}</td>'
            f'<td>{money}</td><td>{bets}</td><td>{r["type"]}</td><td>{call}</td><td class="{cls}">{res}</td></tr>')
def w5row(g):
    fa,fl=fav_of(g); A=AB[g['ab_side']]
    bs=A if g['ab_b']>=50 else [x for x in (g['A'],g['H']) if x!=A][0]; bp=g['ab_b'] if g['ab_b']>=50 else 100-g['ab_b']
    rt=g['rating']; call=f'<b class="tg {rt}">{rt}</b>'+(f' {AB[g["fade"]]} {g["sp"][AB[g["fade"]]]}' if rt!='PASS' else '')+_sideplays(g.get('week',5),f"{g['A']}@{g['H']}")
    ko=' · '.join(g['when'].split(' · ')[:2]).replace(' ET','')
    f=g.get('final')
    if f:
        mg=int(f['a'])-int(f['h'])+float(g['sp'][g['A']].replace('−','-'))
        cov=g['A'] if mg>0 else (g['H'] if mg<0 else 'Push')
        return (f'<tr data-final="1"><td>{g["A"]} @ {g["H"]}</td><td>{ko}</td><td>{fa} {fl}</td><td>{_score(g) or f["score"]}</td><td>{cov}</td>'
                f'<td>{A} {g["ab_m"]}%</td><td>{bs} {bp}%</td><td>{g["type"]}</td><td>{call}</td><td class="{"pos" if f["usd"]>0 else ("neg" if f["usd"]<0 else "")}">{f["word"]} {usd(f["usd"])}{_mlres(_gwk(g),f"{g['A']}@{g['H']}")}</td></tr>')
    sc=_score(g) if g.get('week',5)==5 else ''
    if sc:
        return (f'<tr data-final="1"><td>{g["A"]} @ {g["H"]}</td><td>{ko}</td><td>{fa} {fl}</td><td>{sc}</td><td>—</td>'
                f'<td>{A} {g["ab_m"]}%</td><td>{bs} {bp}%</td><td>{g["type"]}</td><td>{call}</td><td>—</td></tr>')
    return (f'<tr data-final="0"><td>{g["A"]} @ {g["H"]}</td><td>{ko}</td><td>{fa} {fl}</td><td>—</td><td>—</td>'
            f'<td>{A} {g["ab_m"]}%</td><td>{bs} {bp}%</td><td>{g["type"]}</td><td>{call}</td><td>not played</td></tr>')
def wk(w,rows,fs):
    return (f'<details class="fold wk" open><summary><span class="ft">Week {w}</span><span class="fs">{fs}</span></summary><div class="fold-b"><div class="tcard"><div class="tblwrap">'
            f'<table class="data games">{th(COLS)}<tbody>{rows}</tbody></table></div></div></div></details>')
ARC=(f'<section class="pane on" id="games"><div class="sec-h"><h2>All games</h2><p class="sub">Newest week first. Lines: DraftKings, recorded last before kickoff (Week {GW} upcoming games: lines as of {PULL6}). Results from our side, $100 per play.</p></div>'
     f'<p class="sub2"><a href="tygif-tracker.html#results">‹ Back to Records</a></p>'
     f'<div class="games-controls"><input aria-label="Search games" autocomplete="off" id="games-q" placeholder="Search a team, e.g. DAL" type="search"/>'
     f'<label class="chk"><input id="games-final-only" type="checkbox"/> Final only</label></div><p class="legend"><span class="js-only">Tap a column name to sort</span></p>')
_nf=sum(1 for g in G if g.get('final'))
for w in reversed(LIVEW):
    _nfw=sum(1 for g in GBY[w] if g['final'])
    ARC+=wk(w,''.join(w5row(g) for g in sorted(GBY[w],key=_kick)),f'{len(GBY[w])} games · '+('final' if _nfw==len(GBY[w]) else f'{_nfw} final, {len(GBY[w])-_nfw} upcoming' if _nfw else 'upcoming'))
ARC+=wk(5,''.join(w5row(g) for g in G),f'{len(G)} games · final')
for w in (4,3,2,1):
    ks=sorted([k for k in T if k[0]==w],key=lambda k:(ARCH[k]['Date'],ARCH[k]['Kickoff (ET)']))
    ARC+=wk(w,''.join(arow(k) for k in ks),f'{len(ks)} games · final')
ARC+='<p class="empty-msg" hidden="" id="games-none">No games match that search.</p></section>'
i0=ar.index('<main>'); i1=ar.index('</main>')
ar=ar[:i0]+'<main>\n'+ARC+'\n'+ar[i1:]
ar=re.sub(r'<footer>.*?</footer>',f'<footer>{FOOT}</footer>',ar,flags=re.S)
ar=NAVRE.sub(nav('results'),ar,count=1)
ar=ar.replace('</head>','<style>.tg{font-size:12px;font-weight:800;letter-spacing:.04em}.tg.STRONG{color:#3fae6c}.tg.LEAN{color:#b8860b}.tg.PASS{color:#9a9da4}.pos{color:#3fae6c}.neg{color:#e07a7a}table.games td,table.games th{font-size:13px}</style></head>',1)
wr('tygif-games-archive.html',ar)

# ---------- angles stub ----------
stub=rd('tygif.html').replace('index.html','tygif-tracker.html#results').replace('"tygif-tracker.html#results"+(location.hash&&"tygif-tracker.html#results".indexOf("#")<0?location.hash:"")','"tygif-tracker.html#results"')
wr('tygif-angles.html',stub)

# ---------- live log ----------
import os
os.makedirs(R+'data',exist_ok=True)
assert os.path.exists(R+'data/live_log.csv'), 'live_log.csv missing: the routines own it; never regenerate'
print('dd/archive/stub/log ok')

# ---------- txt files ----------
QBL={}
def marks(g):
    short={'a':'money and bets same team','b':'65%+ of the money','c':'DraftKings same team','d':'line steady'}
    return ' · '.join(f"{short[l]}: {'yes' if v else 'no'}" for l,_,v,_,_ in qa(g))
P=[f"tygif's model | Week 5 plays (final: called on the {PULL} pull; graded at the DraftKings close with the last splits before kickoff)",
   "Play = against the money. All sportsbooks first (ScoresAndOdds); DraftKings must have the money on the same side.",
   f"{sum(g['rating']=='STRONG' for g in G)} STRONG, {sum(g['rating']=='LEAN' for g in G)} LEAN, {len(passes)} passes.",""]
L=[f"tygif's model · Week 5 card", f"Splits: all books (ScoresAndOdds) and DraftKings (final: called on the {PULL} pull; graded at the DraftKings close with the last splits before kickoff). Lines from DraftKings at the same time.",""]
B=[f"week 5 — {sum(g['rating']=='STRONG' for g in G)} strong, {sum(g['rating']=='LEAN' for g in G)} lean. same money rule. numbers as of sat night ({PULL_SHORT.lower()}).",""]
for g in plays:
    side=g['fade']; ab=AB[side]; call=f"{side} {g['sp'][ab]}"; t=g['type']
    FT=(f" · {g['final']['tag']}" if g.get('final') else '')
    P+=[f"{g['rating']}: {call} · Type {t} ({TY[t]['name']}). DraftKings {g['sp'][ab]}. {g['when']}{FT}",
        f"  Checks: {marks(g)}",
        (f"  {g['ab_side']} holds most of the money: {g['ab_m']}% {g.get('clbl',CLBL)}, with {g['ab_b']}% of the bets. DraftKings: {g['dk_m']}% on {g['dk_side']} ({g.get('dk_note_short') or PULL}). Play {side}." if g.get('split_at')=='closing' else f"  {g['ab_side']} holds most of the money (all books {g['ab_m']}%, DraftKings {g['dk_m']}%{('; '+g['dk_note_short']) if g.get('dk_note_short') else ''}) and most of the bets (all books {g['ab_b']}%). Play {side}.")]
    if g['gid'] in QBL: P.append('  '+QBL[g['gid']])
    P.append('  '+opener(g)+'.')
    if ml_txt(g): P.append('  '+ml_txt(g))
    L+=[f"{g['rating']}: {call}{FT}",f"  {g['away']} at {g['home']} · {g['when']}",
        f"  All books: {g['ab_m']}% of the money on {g['ab_side']} ({g['ab_b']}% of bets){' '+g.get('clbl',CLBL) if g.get('split_at')=='closing' else ''} · DraftKings: {g['dk_m']}% of the money on {g['dk_side']}{(' ('+g['dk_note_short']+')') if g.get('dk_note_short') else ''}",
        f"  Line: {call} at DraftKings · Type {t}"]+([ '  '+QBL[g['gid']]] if g['gid'] in QBL else [])+(['  '+ml_txt(g)] if ml_txt(g) else [])+[""]
    B.append(f"{call}{' (thu)' if g['gid']=='tbdal-card' else ''}{(' — '+g['final']['tag'].lower()) if g.get('final') else ''} — {g['rating']}. {g['ab_m']}% of the money on {g['ab_side']}{' '+g.get('clbl',CLBL) if g.get('split_at')=='closing' else ''}."+(' '+QBL[g['gid']].split('.')[0].lower()+'.' if g['gid'] in QBL else '')+((' '+ml_txt(g).lower()+'.') if ml_txt(g) else ''))
_g={x['gid']:x for x in G}; _da=_g['g-detroit-at-arizona']; _ht=_g['g-ten']
CHG=[f"  Houston at Tennessee: a pass on Thursday (books disagreed). Now all books have {_ht['ab_m']}% of the money and {_ht['ab_b']}% of the bets on {_ht['ab_side']}, DraftKings {_ht['dk_m']}% on {_ht['dk_side']}: "+(f"{_ht['rating']} {_ht['call']}." if _ht['rating']!='PASS' else f"still a pass ({_ht['call']} is a Type 3 underdog)."),
     f"  Detroit at Arizona: a pass on Thursday (only 53% of the money, on Arizona). Now all books have {_da['ab_m']}% of the money and {_da['ab_b']}% of the bets on {_da['ab_side']}, DraftKings {_da['dk_m']}% on {_da['dk_side']}: "+(f"{_da['rating']} {_da['call']}." if _da['rating']!='PASS' else f"still a pass ({_da['call']} is a Type 3 underdog).")]
P+=["",
    "Passes:"]
for g in passes:
    t=g['type']
    r={4:f"all books have the money on {g['ab_side']} ({g['ab_m']}%), DraftKings on {g['dk_side']} ({g['dk_m']}%)",5:f"only {g['ab_m']}% of the money on {g['ab_side']}",3:f"{g['ab_m']}% of the money on {g['ab_side']}, and our side, {g['call']}, is the underdog (Type 3 underdogs are passes)"}[t]
    if EVEN(g): r=EVENTXT(g)
    P.append(f"  {g['away']} at {g['home']}: Type {t} ({TY[t]['name'].lower()}) — {r}. No bet.")
P+=["","Small samples, no guarantees."]
L+=[
    "PASS / DO NOT BET: "+', '.join(f"{g['A']}@{g['H']}" for g in passes)+"."]
B+=["","lines move. we fade the money, not the vibes."]
for f,lines in (('tygif-week-5-plays.txt',P),('tygif-week-5-LOCK.txt',L),('tygif-week-5-buddy.txt',B)):
    open(R+f,'w').write('\n'.join(lines).replace('-','-')+'\n')

def txt_week(GG,wk,pull,pull_short):
    pl=[g for g in GG if g['rating']!='PASS']; ps=[g for g in GG if g['rating']=='PASS']
    ns=sum(g['rating']=='STRONG' for g in GG); nl=sum(g['rating']=='LEAN' for g in GG)
    P=[f"tygif's model | Week {wk} plays (splits and lines pulled {pull}; they move until kickoff; final games graded at the close)",
       "Play = against the money. All sportsbooks first (ScoresAndOdds); DraftKings must have the money on the same side.",
       f"{ns} STRONG, {nl} LEAN, {len(ps)} passes.",""]
    L=[f"tygif's model · Week {wk} card", f"Splits: all books (ScoresAndOdds) and DraftKings, pulled {pull}. Lines from DraftKings at the same time.",""]
    B=[f"week {wk} — {ns} strong, {nl} lean. same money rule. numbers as of {pull_short.lower()}.",""]
    for g in pl:
        side=g['fade']; ab=AB[side]; call=f"{side} {g['sp'][ab]}"; t=g['type']
        qn=''
        P+=[f"{g['rating']}: {call} · Type {t} ({TY[t]['name']}). DraftKings {g['sp'][ab]}. {g['when']}",
            f"  Checks: {marks(g)}",
            f"  {g['ab_side']} holds most of the money (all books {g['ab_m']}%, DraftKings {g['dk_m']}%) and most of the bets (all books {g['ab_b']}%). Play {side}."]
        if qn: P.append('  '+qn)
        P.append('  '+opener(g)+'.')
        if ml_txt(g): P.append('  '+ml_txt(g))
        L+=[f"{g['rating']}: {call}",f"  {g['away']} at {g['home']} · {g['when']}",
            f"  All books: {g['ab_m']}% of the money on {g['ab_side']} ({g['ab_b']}% of bets) · DraftKings: {g['dk_m']}% of the money on {g['dk_side']}",
            f"  Line: {call} at DraftKings · Type {t}"]+(['  '+qn] if qn else [])+(['  '+ml_txt(g)] if ml_txt(g) else [])+[""]
        B.append(f"{call} — {g['rating']}. {g['ab_m']}% of the money on {g['ab_side']}."+(' '+qn.lower() if qn else '')+((' '+ml_txt(g).lower()+'.') if ml_txt(g) else ''))
    P+=["","Passes:"]
    for g in ps:
        t=g['type']
        r={4:f"all books have the money on {g['ab_side']} ({g['ab_m']}%), DraftKings on {g['dk_side']} ({g['dk_m']}%)",5:f"only {g['ab_m']}% of the money on {g['ab_side']}"}.get(t,f"money on {g['ab_side']} but most bets on the other side")
        P.append(f"  {g['away']} at {g['home']}: Type {t} ({TY[t]['name'].lower()}) — {r}. No bet.")
    P+=["","Small samples, no guarantees."]
    L+=["PASS / DO NOT BET: "+', '.join(f"{g['A']}@{g['H']}" for g in ps)+"."]
    B+=["","lines move. we fade the money, not the vibes."]
    for f,lines in ((f'tygif-week-{wk}-plays.txt',P),(f'tygif-week-{wk}-LOCK.txt',L),(f'tygif-week-{wk}-buddy.txt',B)):
        open(R+f,'w').write('\n'.join(lines)+'\n')
txt_week(G6,GW,PULL6,PULL6)
# posted card for scripts/line_alerts.py (spreads only, no prices)
json.dump({'week':GW,'posted_at_et':PULL6,'source':'clean_build.py G6 (DraftKings line at the posted pull)',
           'plays':[{'game':f"{g['A']}@{g['H']}",'team':AB[g['fade']],'name':g['fade'],'nick':NICK[AB[g['fade']]],'rating':g['rating'],'line':g['sp'][AB[g['fade']]].replace(M,'-'),'kickoff_utc':g['ko_utc']}
                     for g in plays6]},open(R+'data/current_card.json','w'),indent=1)
print('txt ok')

# ---------- txt files: one clean template for every week ----------
def txt_clean(GG,wk,asof):
    pl=[g for g in GG if g['rating']!='PASS']; ps=[g for g in GG if g['rating']=='PASS']
    fin=all(g.get('final') for g in pl)
    head=[f"TYGIF'S MODEL · WEEK {wk}", ('Final' if fin else f'Lines as of {asof}'),'']
    def rec_line(g):
        a=at(g['rating'],g['type'],before=_cb(g)); return f"Type {g['type']} · {TY[g['type']]['name']} · {g['rating']}: {wlp(*a[:3])}, {usd(a[3])}" if a[4] else f"Type {g['type']} · {TY[g['type']]['name']} · {g['rating']}: no plays yet"
    def res(g): return f" · {g['final']['tag'].replace('Final: ','Final ')}" if g.get('final') else ''
    P=list(head); L=list(head); B=[f"Week {wk}"+(' · Final' if fin else f' · Lines as of {asof}'),'']
    for rt in ('STRONG','LEAN'):
        gs=[g for g in pl if g['rating']==rt]
        if not gs: continue
        P.append(rt); L.append(rt)
        for g in gs:
            side=g['fade']; call=f"{side} {g['sp'][AB[side]]}"; when=' · '.join(g['when'].split(' · ')[:2])
            P+=[f"  {call}  ·  {g['away']} at {g['home']}, {when}{res(g)}",f"    {rec_line(g)}",
                "    "+' · '.join(f"{l}: {'Yes' if v else 'No'}" for l,_,v,_,_ in qa(g))]
            L.append(f"  {call}  ·  {when}{res(g)}")
            B.append(f"{rt} {call}{res(g)}")
        P.append(''); L.append('')
    mg=sorted(ml_games(GG,wk),key=lambda g:{'STRONG':0,'LEAN':1}[g['rating']])
    if mg:
        P.append('MONEYLINE'); L.append('MONEYLINE')
        for g in mg:
            r=ml_for(g,wk); side=g['fade']; when=' · '.join(g['when'].split(' · ')[:2])
            rr=f" · Final {g['final']['tag'].split(' · ')[0].replace('Final: ','').split(' ',1)[1]} · {dict(W='win',L='loss',P='push')[r['result']]} {usd(r['profit'])}" if r.get('result') else ''
            a=ml_at(g['rating'],g['type'],r['fd'],before=_cb(g)); mrec=f"Type {g['type']} · {TY[g['type']]['name']} · {g['rating']} ML · {FDN[r['fd']]}: "+(f"{wlp(*a[:3])}, {usd(a[3])}" if a[4] else 'no plays yet')
            P+=[f"  {g['rating']} {side} ML  ·  {g['away']} at {g['home']}, {when}{rr}",f"    {mrec}","    "+' · '.join(f"{l}: {'Yes' if v else 'No'}" for l,_,v,_,_ in qa(g))]
            L.append(f"  {g['rating']} {side} ML  ·  {when}{rr}"); B.append(f"{g['rating']} {side} ML{rr}")
        P.append(''); L.append('')
    osd=[]
    for g in sorted(GG,key=_kick):
        for x in SDX.get((wk,f"{g['A']}@{g['H']}"),{}).values():
            ours=x['role']=='fade' and x['rating']!='PASS'
            def rr(k): return f" · {dict(W='win',L='loss',P='push')[x[k+'_res']]} {usd(x[k+'_usd'])}" if x.get(k+'_res') else ''
            if not ours and sp_post(x): osd.append((g,f"{x['rating']} {x['role']} side · {NAME[x['team']]} {g['sp'][x['team']]}{rr('sp')}",sp_grp(x,_cb(g)),'sp'))
            if not ours and ml_post(x): osd.append((g,f"{x['rating']} {x['role']} side · {NAME[x['team']]} ML{rr('ml')}",ml_grp(x,_cb(g)),'ml'))
    if osd:
        P.append('MONEY SIDE AND PASS-GAME SIDES'); L.append('MONEY SIDE AND PASS-GAME SIDES')
        for g,t_,a_,k in osd:
            when=' · '.join(g['when'].split(' · ')[:2])
            P+=[f"  {t_}  ·  {g['away']} at {g['home']}, {when}",f"    group: {wlp(*a_[:3])}, {usd(a_[3])}"]
            L.append(f"  {t_}  ·  {when}"); B.append(t_)
        P.append(''); L.append('')
    P+=['PASS']+[f"  {g['away']} at {g['home']}" for g in ps]
    L+=['PASS']+[f"  {g['away']} at {g['home']}" for g in ps]
    for f,lines in ((f'tygif-week-{wk}-plays.txt',P),(f'tygif-week-{wk}-LOCK.txt',L),(f'tygif-week-{wk}-buddy.txt',B)):
        open(R+f,'w').write('\n'.join(lines).rstrip()+'\n')
txt_clean(G,5,'')
for _w in LIVEW: txt_clean(GBY[_w],_w,_etdata(max(g['split_utc'] for g in GBY[_w])))
# ---------- wording polish on rendered text (text nodes only; numbers untouched) ----------
POLISH=[('(all books, last pull before kickoff: ','(as of '),('last DraftKings pull ','DraftKings as of '),('; no closer split was saved',''),
        ('DraftKings split ','DraftKings as of '),(', the last before kickoff',''),(' (all books)',''),('(all books, final split)',''),
        ('all books','consensus'),('All books','Consensus'),('all-books','consensus'),('start-of-week line','Monday line'),('Start-of-week line','Monday line'),
        (' pts ',' points '),('Last DraftKings pull','Last DraftKings read'),('last pull Thu Oct 8, 1:58 PM ET; DraftKings closing split not found','as of Thu Oct 8, 1:58 PM ET')]
def _polish(x,dd=False):
    for a,b in (('(all books, final split; read after kickoff, page not timestamped)','(all books)'),('All books are split 50–50','all books are split 50–50')): x=x.replace(a,b)
    P2=[p for p in POLISH if p[1] not in ('consensus','Consensus') and p[0]!=' (all books)']
    KEEP='Weeks 1–4: all-books splits only; DraftKings split not recorded.'
    x=x.replace(KEEP,'\x00')
    for a,b in P2: x=x.replace(a,b)
    return x.replace('\x00',KEEP)
for _f in _gl_pol(R) if False else __import__('glob').glob(R+'*.html'):
    _s=BeautifulSoup(open(_f).read(),'html.parser')
    for _n in _s.find_all(string=True):
        if _n.parent.name in ('style','script'): continue
        _y=_polish(str(_n),_f.endswith('tygif-deep-dive.html'))
        if _y!=str(_n): _n.replace_with(_y)
    open(_f,'w').write(str(_s))

import glob as _gl
for _f in _gl.glob(R+'*.html'):
    _x=open(_f).read()
    _y2=re.sub(r'<span class="updated">[^<]*</span>','',_x)
    if _y2!=_x: open(_f,'w').write(_y2)
print('done')
for _f in _gl.glob(R+'*.html')+_gl.glob(R+'*.txt'):
    _x=open(_f).read(); _y=_x
    for _t in (1,2):
        _y=re.sub(re.escape(OLDNAMES[_t]),TY[_t]['name'],_y,flags=re.I) if False else _y.replace(OLDNAMES[_t],TY[_t]['name']).replace(OLDNAMES[_t].lower(),TY[_t]['name'].lower())
    if _y!=_x: open(_f,'w').write(_y)

# ---------- self-check: every card, checklist and pass row agrees with the data ----------
_GD={g['gid']:g for g in G+GALL+G14}
# ---------- redesign: one light stylesheet for every page ----------
from zoneinfo import ZoneInfo as _ZI
import datetime as _dtm
_ETZ=_ZI('America/New_York'); _CTZ=_ZI('America/Chicago')
_MON={m:i for i,m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'],1)}
SEASON_YR=min(int(g['ko_utc'][:4]) for g in GALL)   # season year derived from the data (first live week's kickoffs); Jan/Feb games belong to the next calendar year
def _to_ct(mon,day,hm,ap):
    h,mi=map(int,hm.split(':')); h=h%12+(12 if ap=='PM' else 0); mo=_MON[mon]
    t=_dtm.datetime(SEASON_YR+(1 if mo<=2 else 0),mo,int(day),h,mi,tzinfo=_ETZ).astimezone(_CTZ)
    return t
def _fmt(t,sep): return f"{t.strftime('%a %b')} {t.day}{sep}{int(t.strftime('%I'))}:{t.strftime('%M %p')}"
_TRX=re.compile(r'\b(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{1,2})(, | · )(\d{1,2}:\d{2}) (AM|PM) ET\b')
_TDX=re.compile(r'<td>(Mon|Tue|Wed|Thu|Fri|Sat|Sun) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (\d{1,2}) · (\d{1,2}:\d{2}) (AM|PM)</td>')
def _ct_text(x):
    x=_TRX.sub(lambda m:_fmt(_to_ct(m.group(2),m.group(3),m.group(5),m.group(6)),m.group(4))+' CT',x)
    x=_TDX.sub(lambda m:'<td>'+_fmt(_to_ct(m.group(2),m.group(3),m.group(4),m.group(5)),' · ')+' CT</td>',x)
    x=x.replace('before Monday 12:00 AM ET','before Sunday 11:00 PM CT').replace('before Mon Oct 12 12:00 AM ET','before Sun Oct 11 11:00 PM CT')
    return x
def _theme():
    css=open(_I+'/site.css').read()
    head=('<link rel="preload" href="assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>'
          '<meta name="theme-color" content="#f6f6f4"><style id="site">'+css+'</style>')
    for f in _gg.glob(R+'*.html'):
        x=open(f,encoding='utf-8').read()
        x=re.sub(r'<style[^>]*>.*?</style>','',x,flags=re.S)
        x=re.sub(r'<link[^>]+fonts\.(googleapis|gstatic)[^>]*>','',x)
        x=re.sub(r'<link[^>]*inter-latin\.woff2[^>]*>','',x); x=re.sub(r'<meta[^>]*theme-color[^>]*>','',x)
        x=x.replace('</head>',head+'</head>',1)
        x=_ct_text(x)
        open(f,'w',encoding='utf-8').write(x)
import glob as _gg
_theme()
for _f in _gg.glob(R+'tygif-week-*.txt'):
    _x=open(_f,encoding='utf-8').read(); open(_f,'w',encoding='utf-8').write(_ct_text(_x))
def _selfcheck():
    errs=[]
    faces={}
    for f in ('index.html','tygif-tracker.html'):
        t=BeautifulSoup(open(R+f).read(),'html.parser')
        for _r in t.select('.uc-r'):
            if not _r.select_one('.uc-yn'): errs.append((f,'pill missing'))
            if 'favorite giving 6+' in _r.get_text(): errs.append((f,'6+ favorite row still shown'))
        for p in t.select('.uc-yn'):
            ans=p.get_text(strip=True)[1:]; icon=p.i.get_text() if p.i else ''; cls=[c for c in p['class'] if c!='uc-yn']
            ok=(ans=='Yes' and cls==['ok'] and icon=='✓') or (ans=='No' and cls==['no'] and icon=='✕') or (p.get_text(strip=True)=='—' and cls==['nu'] and p.i is None)
            if not ok: errs.append((f,'pill',ans,cls,icon))
        for c in t.select('.cd'):
            gid=(c.get('href') or '').split('#')[-1] if c.name=='a' else c.find_parent('details')['id']
            g=_GD[gid[:-3] if gid.endswith('-ml') else gid]; r=g['rating']; A=AB[g['ab_side']]
            if c.select_one('.cd-b').get_text()!=r or f's-{r}' not in c['class'] or r not in c.select_one('.cd-b')['class']: errs.append((f,gid,'badge'))
            if c.select_one('.cd-c').get_text()!=(f"{g['away']} at {g['home']}" if (g['rating']=='PASS' or gid in FULL) else f"{g['fade']} {g['sp'][AB[g['fade']]]}") or ('full' in c['class'])!=(gid in FULL): errs.append((f,gid,'call'))
            if c.select_one('.cd-2 .c2').get_text()!=f"Type {g['type']} · {TY[g['type']]['name']}": errs.append((f,gid,'type'))
            cells={s.contents[0]:(s.b.get_text(),s.b['class'][0]) for s in c.select('.cd-3 span')}
            want={'Money':f"{A} {g['ab_m']}%",'Bets':f"{A} {g['ab_b']}%",'DraftKings':'Same' if g['c'] else 'Opposite','Line':'Steady' if _steady(g) else 'Moved'}
            for k,v in want.items():
                if cells[k][0]!=v: errs.append((f,gid,k,cells[k],v))
            faces.setdefault(gid,set()).add(c.select_one('.cd-b').get_text()+c.select_one('.cd-c').get_text()+c.select_one('.cd-2').get_text()+str([(s.get_text(),s.b['class']) for s in c.select('.cd-3 span')]))
        if f=='tygif-tracker.html':
            for d in t.select('details.gm, details.pr'):
                g=_GD[d['id'][:-3] if d['id'].endswith('-ml') else d['id']]; ans={r.select_one('.uc-l').get_text():r.select_one('.uc-n').get_text().split(':')[0]=='Yes' for r in d.select('.uc-r')}
                exp={l:v for l,_,v,_,_ in qa(g)}
                if ans!=exp: errs.append((d['id'],'checklist',ans,exp))
                if d.select_one('.uc-res b').get_text()!=g['rating']: errs.append((d['id'],'result badge'))
                face=d.select_one('.cd')
                if face:
                    cells={s.contents[0]:s.b.get_text() for s in face.select('.cd-3 span')}
                    if (cells['Bets'] and ans['a'])!=ans['a'] or (cells['DraftKings']=='Same')!=ans['c'] or (cells['Line']=='Steady')!=ans['d'] or sorted(ans)!=list('abcd'):
                        errs.append((d['id'],'face vs checklist',cells,ans))
                if 'pr' in d['class']:
                    if d.select_one('.ps-b').get_text()!='PASS' or g['rating']!='PASS' or f"Type {g['type']}" not in d.select_one('.ps-2').get_text(): errs.append((d['id'],'pass row'))
    for gid,v in faces.items():
        if len(v)!=1: errs.append((gid,'home and This Week cards differ'))
    assert not errs, errs
    print('self-check ok:', len(_GD), 'games')
_selfcheck()

# ---------- deep check (ML, prices, notes, Home vs This Week) ----------
def _deepcheck():
    import glob as _gg
    errs=[]
    # 1) ML records recomputed independently from the raw ESPN files and the play lists
    raw={}
    for w in _sg0.WEEKS:
        for e in json.load(open(_W+f'/espn_sum/sb_w{w}.json'))['events']:
            c=e['competitions'][0]; tm={x['homeAway']:x for x in c['competitors']}
            raw[(w,tm['away']['team']['abbreviation']+'@'+tm['home']['team']['abbreviation'])]=(e['id'],tm,c['status']['type']['name'])
    def _bqi(w,game):
        # as-posted basis, worked out here from the raw scoreboard + live_log (not from _cb/_fb): finished -> weeks before w; else None
        fin=w<=5 or (raw.get((w,game),(0,0,''))[2]=='STATUS_FINAL' and any(int(r['week'])==w and r['game']==game and (r.get('result') or '').strip() for r in live_rows()))
        # user, Oct 15 11:10 PM: displayed groups are season-to-date on every card; finished cards must include their own game
        return None
    want={}
    src=[(k[0],k[1],CARD[k]['rating'],T[k]['side'],T[k]['type']) for k in CARD]
    src+=[(int(r['week']),r['game'],r['rating'],r['our_side'],int(r['type'])) for r in live_rows()]
    grp={}
    for w,gm,rt,side,ty in src:
        eid,tm,stat=raw[(w,gm)]; home=tm['home']['team']['abbreviation']==side
        pc=[p for p in json.load(open(_W+f'/espn_sum/{eid}.json'))['pickcenter'] if p['provider']['name']=='DraftKings'][0]['moneyline']
        o=pc['home' if home else 'away']['close']['odds']; pr=100 if o=='EVEN' else int(o)
        _q=_sg0.pre_ml(w,*gm.split('@'),side)
        if _q is not None: pr=_q   # last pre-kickoff DraftKings moneyline
        us=int(tm['home' if home else 'away']['score']); th=int(tm['away' if home else 'home']['score'])
        u=round(pr if pr>0 else 10000/-pr) if us>th else (-100 if us<th else 0)
        for kk in ((rt,'all'),(rt,ty,'Dog' if pr>0 else 'Fav')):
            a=(want if kk[1]=='all' else grp).setdefault(kk,[0,0,0,0.0]); a[0 if us>th else (1 if us<th else 2)]+=1; a[3]+=u
    for (rt,ty,fd),(w,l,p,u) in grp.items():
        if ml_at(rt,ty,fd)[:4]!=(w,l,p,u): errs.append(('ML group',rt,ty,fd,ml_at(rt,ty,fd),(w,l,p,u)))
    for rt in ('STRONG','LEAN'):
        if sum(v[3] for k,v in grp.items() if k[0]==rt)!=want[(rt,'all')][3]: errs.append(('ML groups≠total',rt))
    for (rt,st),(w,l,p,u) in want.items():
        got=ml_tally(rt,('look back','live'))
        if got[:3]!=(w,l,p) or abs(got[3]-u)>0.01: errs.append(('ML record',rt,st,got,(w,l,p,u)))
    tr=BeautifulSoup(open(R+'tygif-tracker.html').read(),'html.parser')
    mtxt=tr.find(id='moneyline').find_next_sibling
    for (rt,st),(w,l,p,u) in want.items():
        sec=tr.find(id='moneyline'); txt=' '.join(x.get_text(' ',strip=True) for x in sec.find_next_siblings('div',class_='gt-row',limit=2))
        if f'{rt} {w}-{l}-{p} {usd(u)}' not in txt: errs.append(('ML record not shown',rt,st,txt))
    # 2) every game has exactly one card; each card's ML call matches the data and the group rule
    for f,games in (('index.html',G6),('tygif-tracker.html',G6)):
        t=BeautifulSoup(open(R+f).read(),'html.parser')
        ids=[((c.get('href') or '').split('#')[-1] if c.name=='a' else c.find_parent('details')['id']) for c in t.select('.cdh > .cd, .cdh > details > summary > .cd')]
        if sorted(ids)!=sorted(g['gid'] for g in games): errs.append((f,'one card per game',len(ids),len(games)))
        for c in t.select('.cd'):
            gid=(c.get('href') or '').split('#')[-1] if c.name=='a' else c.find_parent('details')['id']
            g=_GD[gid]; mr=ml_for(g,g.get('week',5)); m=c.select_one('.cd-m'); mt=m.get_text(' ',strip=True) if m else ''
            if not m: errs.append((f,gid,'no ML line')); continue
            if g['rating']=='PASS' or not mr or mr.get('price') is None:
                if g['rating']!='PASS' and 'neu' not in m.select_one('.mc')['class']: errs.append((f,gid,'ML should be neutral',mt))
                continue
            a=ml_at(g['rating'],g['type'],mr['fd'],before=_bqi(g.get('week',5),f"{g['A']}@{g['H']}")); lab="Group"
            want_g=f"{lab}: {wlp(*a[:3])}, {usd(a[3])}" if a[4] else f"{lab}: no games yet"
            if m.small.get_text()!=want_g or m.select_one('.c2').get_text()!=f"Type {g['type']} · {FDN[mr['fd']]}": errs.append((f,gid,'ML group record',m.small.get_text(),want_g))
            ap=ml_at(g['rating'],g['type'],mr['fd'],before=g.get('week',5)); posted=ap[4]>0 and ap[3]>0
            if posted!=('neu' not in m.select_one('.mc')['class']) or not m.select_one('.mc').get_text().startswith(f"{g['fade']} ML"): errs.append((f,gid,'ML posted rule'))
            if posted and mr.get('result') and usd(mr['profit']) not in m.select_one('.mc').get_text(): errs.append((f,gid,'ML result'))
            if re.search(r'(?<![\d$,])[+−-]\d{3}\b',c.get_text(' ')): errs.append((f,gid,'price on card'))
    def face(c):
        for z in c.select('.cd-ar'): z.decompose()
        return c.get_text(' ',strip=True)
    hm={d['id']:face(d.select_one('.cd')) for d in BeautifulSoup(open(R+'index.html').read(),'html.parser').select('details.gm')}
    tw={d['id']:face(d.select_one('.cd')) for d in tr.select('details.gm') if d.select_one('.cd')}
    for gid,txt in hm.items():
        if tw.get(gid)!=txt: errs.append(('home vs week',gid,txt,tw.get(gid)))
    # 3) no prices or odds anywhere visible, no update/revision notes
    # all-weeks spread records recomputed straight from the data files
    import csv as _cv
    TW={(r['week'],r['game']):r for r in json.load(open(_I+'/types_w14.json'))}
    raw2=[(k[0],CARD[k]['rating'],TW[k]['type'],TW[k]['res'],TW[k]['usd']) for k in CARD]
    for r in _cv.DictReader(open(R+'data/live_log.csv')):
        if r['result']: 
            pr=float(r['closing_price']); res=r['result'][0]
            raw2.append((int(r['week']),r['rating'],int(r['type']),res,(-100.0 if res=='L' else 0.0 if res=='P' else (10000/abs(pr) if pr<0 else pr))))
    page=tr.get_text(' ')
    # logs must match the card data
    _cg={(g['week'],f"{g['A']}@{g['H']}"):g for g in G+GALL}
    for r in _cv.DictReader(open(R+'data/live_log.csv')):
        g=_cg.get((int(r['week']),r['game'].replace('LA@','LAR@')))
        if g is None or (r['rating'],int(r['type']))!=(g['rating'],g['type']): errs.append(('live_log vs card',r['week'],r['game'],r['rating'],r['type'],g and (g['rating'],g['type'])))
    for p in json.load(open(R+'data/ml_log.json'))['plays']:
        g=_cg.get((p['week'],p['game']))
        if p['week']>=5 and (g is None or p['rating']!=g['rating']): errs.append(('ml_log vs card',p['week'],p['game'],p['rating'],g and g['rating']))
        if p['week']<=4:
            k=(p['week'],p['game'].replace('LAR@','LA@')); k=k if k in CARD else (p['week'],p['game'])
            if k not in CARD or CARD[k]['rating']!=p['rating']: errs.append(('ml_log vs card W1-4',p['game'],p['rating']))

    # process: every game W1-6 has every field and uses only the listed sources (or a recorded gap)
    allowed={k:{v} for k,v in _S.items()}
    for k,v in SRC_W14.items(): allowed[k].add(v)
    allowed['splits_draftkings'].add(_K['week_5_draftkings'])
    nG={1:16,2:16,3:16,4:16,5:15}
    for w in _sg0.WEEKS:
        gs=[g for g in (G14+G+GALL) if g.get('week')==w]
        if w>max(LIVEW): continue
        if len(gs)!=nG.get(w,len(gs)) or len(gs)!=len({x for (ww,x) in raw if ww==w}): errs.append(('process: game count',w,len(gs)))
    for g in G14+G+GALL:
        for f in PROCESS['required_fields']['all']:
            if g.get(f) is None and not (f=='a' and False): errs.append(('process: missing',g['gid'],f))
        if set(g['src'])!=set(_S) or any(v not in allowed[k] for k,v in g['src'].items()): errs.append(('process: source',g['gid'],g['src']))
        if g['week']<=4 and g['src']!=SRC_W14: errs.append(('process: W1-4 source differs',g['gid']))
        if g['week']>=5 and any(g['src'][k]!=_S[k] for k in ('splits_consensus','spread_line','moneyline','monday_line')): errs.append(('process: source differs',g['gid']))
        if g['rating']!='PASS':
            mr=ml_for(g,g['week'])
            if not mr or mr.get('price') is None: errs.append(('process: no ML price',g['gid']))
            if (g['week']<=5 or g.get('final')) and (not g.get('final') or mr.get('result') is None): errs.append(('process: ungraded',g['gid']))
    # every games list (cards and Records) sums exactly to its record, and the card shows that record
    def _P(x):
        q=re.search(r'([+−]?)\$(\d+)',x); return 0 if not q else (-1 if q.group(1)=='−' else 1)*int(q.group(2))
    def _exp(k):
        rt=k.split()[0]; ml=' ML' in k; ty=int(re.search(r'Type (\d)',k).group(1)) if 'Type' in k else None
        fd={'Favorite':'Fav','Underdog':'Dog'}.get(k.split(' · ')[-1])
        return (ml_at(rt,ty,fd) if ml else at(rt,ty)),rt,ml,fd
    for f in ('index.html','tygif-tracker.html','tygif-deep-dive.html'):
        t=BeautifulSoup(open(R+f).read(),'html.parser')
        for h in t.select('div.cdh'):
            c=h.select_one('.cd'); gid=(c.get('href') or '').split('#')[-1] if c.name=='a' else c.find_parent('details')['id']; g_=_GD[gid]
            if g_['type']==3 and g_['rating']!='PASS' and ml_block(g_)[1]=='Dog' and ml_ok(g_): errs.append((f,'T3 underdog ML play on card',gid))
            _fw=foot_pick(g_); got_={L['data-m']:L for L in h.select(':scope > details.cd-ft')}
            if set(got_)!=set(_fw) or len(h.select(':scope > details.cd-rl'))!=len(_fw): errs.append((f,'footer set',gid,sorted(got_),sorted(_fw))); continue
            for k,(x,a,ours) in _fw.items():
                L=got_[k]; sm=' '.join(L.select_one('summary').get_text(' ').split()); tm=NAME[x['team']]
                # max of the two teams' groups
                sd=SDX[(x['week'],x['game'])]
                # basis computed here, not from _fb: a card is finished when its week is graded (W1-5) or ESPN shows the game final
                # and live_log has its result; finished = groups before its week, pending = every graded game so far
                _bq=_bqi(x['week'],x['game'])
                def _cnt(y):
                    rs=[z for z in SIDES if z['rating']==y['rating'] and z['type']==y['type'] and z['role']==y['role'] and (k=='sp' or z['fd']==y['fd']) and z[k+'_res'] and (_bq is None or z['week']<_bq)]
                    return (sum(z[k+'_res']=='W' for z in rs),sum(z[k+'_res']=='L' for z in rs),sum(z[k+'_res']=='P' for z in rs),sum(z[k+'_usd'] for z in rs),len(rs))
                _gs=[_cnt(y) for y in sd.values() if k=='sp' or y['fd']]
                vals=[r0(z[3]) for z in _gs if z[4]]
                if not vals: errs.append((f,'footer shown but no group',gid,k)); continue
                _a=_cnt(x)
                if tuple(_a[:3])!=tuple(a[:3]) or r0(_a[3])!=r0(a[3]) or _a[4]!=a[4] or len(L.select('li'))!=_a[4]: errs.append((f,'footer group differs from the independent count',gid,k,_bq,_a,a))
                _own=x['week']<=5 or (raw.get((x['week'],x['game']),(0,0,''))[2]=='STATUS_FINAL' and any(int(r['week'])==x['week'] and r['game']==x['game'] and (r.get('result') or '').strip() for r in live_rows()))
                _mine=[z for z in SIDES if z['week']==x['week'] and z['game']==x['game'] and z['rating']==x['rating'] and z['type']==x['type'] and z['role']==x['role'] and (k=='sp' or z['fd']==x['fd']) and z[k+'_res']]
                if _own and _mine and not any(li.select_one('.rl-w').get_text().split()[-1]==str(x['week']) and li.select_one('.rl-g').get_text()==x['game'].replace('@',' at ') for li in L.select('li')): errs.append((f,'finished footer missing its own game',gid,k))
                if L['data-team']!=x['team'] or r0(a[3])!=max(vals) or L.select_one('summary b').get_text()!=f"{wlp(*a[:3])}, {usd(a[3])}": errs.append((f,'footer not max',gid,k,sm))
                if ours:
                    if not sm.startswith(f"{x['rating']} {tm}") or 'cd-mn' in L['class'] or not L.select(f'.tg.{x["rating"]}'): errs.append((f,'footer play styling',gid,k,sm))
                elif not sm.startswith(f'Pass {tm}') or 'cd-mn' not in L['class'] or L.select('.tg.STRONG,.tg.LEAN') or re.search(r'STRONG|LEAN',sm): errs.append((f,'footer pass styling',gid,k,sm))
                if tm not in sm: errs.append((f,'footer team name',gid,k))
        for L in t.select('.cd-rl'):
            if 'cd-ft' in L['class']: continue   # card footers: checked above
            if 'cd-mn' in L['class']:
                # money-side ML footer (our ML a T3-underdog pass): muted, says Pass, never STRONG/LEAN, record = that group
                h=L.find_parent(class_='cdh'); g_=_GB6.get(h.select_one('details.gm')['id'])
                m=SDX[(g_.get('week',5),f"{g_['A']}@{g_['H']}")]['money']; a=_sd.grp(SIDES,m['rating'],m['type'],'money',fd=m['fd'],ml=True)
                sm=' '.join(L.select_one('summary').get_text(' ').split())
                if not (g_['type']==3 and ml_block(g_)[1]=='Dog') or 'Pass' not in sm or re.search(r'STRONG|LEAN',sm) or L.select('.tg.STRONG,.tg.LEAN') \
                   or not sm.startswith('Pass '+NAME[m['team']]+' ML') or L.select_one('summary b').get_text()!=f"{wlp(*a[:3])}, {usd(a[3])}":
                    errs.append((f,'money-side ML footer',L['data-k'],sm))
                continue
            a,rt,ml,fd=_exp(L['data-k']); rs=L.select('li')
            cnt=tuple(sum(x.select_one('.rl-r')['class'][-1]==k for x in rs) for k in 'WLP'); tot=sum(_P(x.select_one('.rl-r').get_text()) for x in rs)
            rec_s=f"{wlp(*a[:3])}, {usd(a[3])}"
            if cnt!=a[:3] or tot!=a[3] or len(rs)!=a[4] or L.select_one('summary b').get_text()!=rec_s: errs.append((f,'list≠record',L['data-k']))
            h=L.find_parent(class_='cdh')
            if h:
                c=h.select_one('.cd'); src=(c.select_one('.cd-m') if ml else c.select_one('.cd-2')).get_text()
                if not src.endswith(rec_s) or (ml and FDN[fd] not in src): errs.append((f,'card≠list',L['data-k'],src))
            if re.search(r'(?<![\d$,])[+−-]1\d\d\b|(?<![\d$,])[+−]\d{3}\b',L.get_text()): errs.append((f,'price in list'))
        for h in t.select('.cdh'):
            c=h.select_one('.cd'); g=_GD[(c.get('href') or '').split('#')[-1] if c.name=='a' else c.find_parent('details')['id']]
            ks=[L['data-k'] for L in h.select(':scope > .cd-rl')]
            pass   # W1 cards now show season-to-date footers (user, Oct 15 11:10 PM)
            if g['rating']!='PASS' and _sd.grp(SIDES,g['rating'],g['type'],'fade',before=g.get('week',5))[4] and not h.select(':scope > .cd-ft[data-m="sp"]'): errs.append((f,g['gid'],'spread list missing'))
    # every displayed breakdown sums exactly to its displayed total
    D=lambda v:round(v)
    def P(t): 
        m=re.search(r'([+−])\$(\d[\d,]*)',t); return 0 if not m else (1 if m.group(1)=='+' else -1)*int(m.group(2).replace(',',''))
    for rt in ('STRONG','LEAN'):
        tot=D(at(rt)[3])
        if any(r['usd']!=round(r['usd']) for r in RECS): errs.append(('unrounded play',rt))
        if sum(D(at(rt,None,w)[3]) for w in WEEKS)!=tot: errs.append(('weeks≠total',rt))
        if sum(D(at(rt,t)[3]) for t in (1,2,3))!=tot: errs.append(('types≠total',rt))
        if sum(D(r['usd']) for r in RECS if r['rating']==rt)!=tot: errs.append(('plays≠total',rt))
        col=1 if rt=='STRONG' else 2
        tb=tr.find('table',class_='wk3')
        if tb:
            cells=[r.find_all('td')[col].get_text(' ') for r in tb.find_all('tr') if len(r.find_all('td'))>col and r.find_all('td')[0].get_text().startswith('Week')]
            if sum(P(c) for c in cells)!=tot: errs.append(('displayed weeks≠total',rt,sum(P(c) for c in cells),tot))
        ws,ts=ml_tally(rt,('look back','live')),None
        mrs=[r for r in ML if r['rating']==rt and r.get('profit') is not None]
        if any(r['profit']!=round(r['profit']) for r in mrs): errs.append(('unrounded ML',rt))
        mt=D(sum(r['profit'] for r in mrs))
        if sum(D(ml_at(rt,t)[3]) for t in (1,2,3))!=D(ml_at(rt)[3]) or D(ml_at(rt)[3])!=mt: errs.append(('ML types≠total',rt))
        if sum(D(sum(r['profit'] for r in mrs if r['week']==w)) for w in {r['week'] for r in mrs})!=mt: errs.append(('ML weeks≠total',rt))
    for rt in ('STRONG','LEAN'):
        xs=[x for x in raw2 if x[1]==rt]; w,l,p=(sum(x[3]==c for x in xs) for c in 'WLP'); u=sum(round(x[4]) for x in xs)
        if at(rt)[:3]!=(w,l,p) or abs(at(rt)[3]-u)>0.01 or f'{w}-{l}-{p} {usd(u)}' not in re.sub(r'\s+',' ',page): errs.append(('all-weeks record',rt,at(rt),(w,l,p,u)))
        for t in (1,2,3):
            ys=[x for x in xs if x[2]==t]
            if ys:
                w,l,p=(sum(x[3]==c for x in ys) for c in 'WLP'); u=sum(round(x[4]) for x in ys)
                if at(rt,t)[:3]!=(w,l,p) or abs(at(rt,t)[3]-u)>0.01: errs.append(('type record',rt,t))
    for c in tr.select('.cd'):
        _id=c.find_parent('details')['id']; _m=_id.endswith('-ml'); g=_GD[_id[:-3] if _m else _id];
        if g['rating']=='PASS': continue
        a=(ml_at if _m else at)(g['rating'],g['type'],before=_bqi(g.get('week',5),f"{g['A']}@{g['H']}")); _k=g['rating']+(' ML' if _m else '')
        want_t=f"Group: {wlp(*a[:3])}, {usd(a[3])}" if a[4] else "Group: no plays yet"
        if want_t not in c.select_one('.cd-2').get_text(): errs.append(('card record',g['gid']))
    PR=re.compile(r'(?<![\d.$])[+\-−][1-9]\d{2}(?![\d.%])')
    NOTE=re.compile(r'\bconsensus\b|\bpull(ed|s)?\b|snapshot|\bagrees\b|start-of-week|vibes|\bpts\b|weeks 1–4|weeks 1-4|look[- ]?back|backtest|\blive\b|calls can change|updated|changed since|rated differently|regrad|was (lean|strong) before|restated',re.I)
    for f in _gg.glob(R+'*.html')+_gg.glob(R+'*.txt'):
        x=open(f).read()
        if f.endswith('.html'):
            t=BeautifulSoup(x,'html.parser')
            for z in t(['style','script']): z.decompose()
            x=t.get_text(' ')
        for m in PR.finditer(x): errs.append((f.split('/')[-1],'price-like',x[max(0,m.start()-30):m.end()+5]))
        _keep=[(q.start(),q.end()) for q in re.finditer(re.escape('Weeks 1–4: all-books splits only; DraftKings split not recorded.'),x)]
        for m in NOTE.finditer(x):
            if any(a0<=m.start()<b0 for a0,b0 in _keep): continue
            if re.match(r'weeks 1–4',m.group(0),re.I) and (x[max(0,m.start()-17):m.start()]=='Not recorded for ' or x[m.end():m.end()+28].startswith(': all-books splits only')): continue
            errs.append((f.split('/')[-1],'note',x[max(0,m.start()-30):m.end()+20]))
        x2=' '.join(x.split())
        x2=x2.replace('no guarantees','').replace('LOCK.txt','')
        LK=re.compile(r'\b(lock(s|ed)?|guarantee[sd]?)\b',re.I)
        for m in LK.finditer(x2):
            if x2[max(0,m.start()-5):m.end()]=='Drew Lock': continue
            errs.append((f.split('/')[-1],'lock/guarantee',x2[max(0,m.start()-30):m.end()+20]))
    # sides_log: both sides of every game
    for rt in ('STRONG','LEAN'):
        if _stally('fade',rt)[:4]!=at(rt)[:4]: errs.append(('sides: fade spread != record',rt,_stally('fade',rt),at(rt)))
        if _stally('fade',rt,True)[:3]!=ml_tally(rt,('look back','live'))[:3] or abs(_stally('fade',rt,True)[3]-ml_tally(rt,('look back','live'))[3])>0.01: errs.append(('sides: fade ML != record',rt))
    _even={(w_,g_) for w_,g_,_ in SFLAGS}
    for g in G14+G+GALL:
        k=(g['week'],f"{g['A']}@{g['H']}"); o=SDX.get(k,{})
        if k in _even: continue
        if sorted(o)!=['fade','money']: errs.append(('sides: missing side',k)); continue
        if (k[0]<=5 or k in FINW) and not all(x['sp_res'] and x['ml_res'] for x in o.values()): errs.append(('sides: ungraded',k))
        if sum(sp_post(x) for x in o.values())>1: errs.append(('sides: two spread plays',k))
        for x in o.values():
            if x['role']=='fade' and x['rating']!='PASS' and not sp_post(x): errs.append(('sides: our call blocked',k))
    for f in ('index.html','tygif-tracker.html','tygif-deep-dive.html'):
        t=BeautifulSoup(open(R+f).read(),'html.parser')
        for d in t.select('details.gm'):
            g=_GD.get(d['id']) or next((x for x in G14 if x['gid']==d['id']),None)
            if g is None: continue
            k=(g['week'],f"{g['A']}@{g['H']}"); o=SDX.get(k,{})
            rows=d.select('.sd-r')
            if len(rows)!=2: errs.append((f,d['id'],'sides: rows')); continue
            for row in rows:
                tm=row.select_one('.sd-t b').get_text(); x=next((v for v in o.values() if v['team']==tm),None)
                sp,ml=row.select('.sdc')
                if not sp.select_one('.tlab').get_text().startswith(f"{NAME[tm]} spread") or ml.select_one('.tlab').get_text()!=f"{NAME[tm]} moneyline": errs.append((f,d['id'],tm,'team labels'))
                if x is None:
                    if 'neu' not in sp.select_one('.c1')['class'] or 'neu' not in ml.select_one('.c1')['class']: errs.append((f,d['id'],'sides: even game posted'))
                    continue
                ours=x['role']=='fade' and x['rating']!='PASS'
                if not ours:
                    if sp.select_one('.c1').get_text()!=f"{NAME[tm]} {g['sp'].get(tm,'')}".strip() or ml.select_one('.c1').get_text()!=f"{NAME[tm]} ML" or 'neu' not in sp.select_one('.c1')['class'] or 'neu' not in ml.select_one('.c1')['class'] or sp_post(x) or ml_post(x): errs.append((f,d['id'],tm,'sides: tracking side label/neutral'))
                    a1=sp_grp(x,_bqi(g.get('week',5),f"{g['A']}@{g['H']}")); a2=ml_grp(x,_bqi(g.get('week',5),f"{g['A']}@{g['H']}"))
                    if not sp.select_one('.c3').get_text().endswith(f"{a1[0]}-{a1[1]}-{a1[2]}, {usd(a1[3])}" if a1[4] else 'no games yet'): errs.append((f,d['id'],tm,'sides: spread group record'))
                    if not ml.select_one('.c3').get_text().endswith(f"{a2[0]}-{a2[1]}-{a2[2]}, {usd(a2[3])}" if a2[4] else 'no games yet'): errs.append((f,d['id'],tm,'sides: ML group record'))
            for row in rows:
                tm=row.select_one('.sd-t b').get_text(); x_=next((v for v in o.values() if v['team']==tm),None)
                exp='Pass' if not (x_ and x_['role']=='fade' and x_['rating']!='PASS') else x_['rating']
                words=re.findall(r'\b(STRONG|LEAN|Pass|PASS)\b',row.get_text(' '))
                if (exp=='Pass')!=('pz' in row['class']): errs.append((f,d['id'],tm,'Pass section must be muted'))
                if words!=[exp] or row.select_one('.sd-t .sdr').get_text()!=exp: errs.append((f,d['id'],tm,'team rating words',words,exp))
                _tx=row.get_text(' ')
                if re.search(r'\bfade\b(?! the)',_tx,re.I) or re.search(r'(?<!of the )\bmoney\b',_tx,re.I) or 'spread' not in _tx or 'moneyline' not in _tx: errs.append((f,d['id'],tm,'team labels must name the market',_tx[:80]))
                for cc,want_l in zip(row.select('.sdc'),(f"{NAME[tm]} {g['sp'].get(tm,'')}".strip(),f"{NAME[tm]} ML")):
                    c1=cc.select_one('.c1')
                    if c1.get_text() in ('Pass','Tracking') or ('neu' in c1['class'] and c1.get_text()!=want_l): errs.append((f,d['id'],tm,'neutral label',c1.get_text(),want_l))
            if sum('neu' not in r.select('.sdc')[0].select_one('.c1')['class'] for r in rows)>1: errs.append((f,d['id'],'sides: two spread plays shown'))
    if 'If both teams qualify on the spread, only our original call posts.' not in open(R+'tygif-how.html').read(): errs.append(('How v3 sentence missing',))
    _all=[k for b in BUCKETS.values() for k in b]
    if len(_all)!=len(set(_all)) or set(_all)!=set(_DONE) or len(_all)!=len(_DONE): errs.append(('season buckets',len(_all),len(set(_all)),len(_DONE)))
    if len(_DONE)!=sum(1 for x in G14+G+GALL if x['week']<=5 or x.get('final')): errs.append(('season: games',len(_DONE)))
    _rows=tr.select('table.season tr[data-b]')
    if sum(int(r.select_one('.num').get_text()) for r in _rows)!=len(_DONE) or tr.select_one('table.season tr.tot .num').get_text()!=str(len(_DONE)): errs.append(('season: counts on page',))
    print('season ok:',{b:len(v) for b,v in BUCKETS.items()},'total',len(_DONE))
    for tl in tr.select('.pst'):
        a=POSTED[tl['data-k']]
        if tl.select_one('.rc-r').get_text()!=f"{a[0]}-{a[1]}-{a[2]}" or usd(a[3]) not in tl.get_text(): errs.append(('posted tile',tl['data-k']))
    _wkp=sum(POSTED['ml|STRONG'][3] for _ in [0])
    for k_,v_ in POSTED.items():
        rt_=k_.split('|')[1]
        if k_.startswith('sp|') and rt_ in ('STRONG','LEAN') and v_[:4]!=at(rt_)[:4]: errs.append(('posted spread != record',rt_))
    for tl in tr.select('.sdt'):
        role,rt,m=tl['data-k'].split('|'); a=_stally(role,rt,m=='ml')
        if tl.select_one('.rc-r').get_text()!=f"{a[0]}-{a[1]}-{a[2]}" or usd(a[3]) not in tl.get_text(): errs.append(('sides tile',tl['data-k']))
    for L in tr.select('.sd-rl'):
        rs=L.select('li'); tot=sum(_P(x.select_one('.rl-r').get_text()) for x in rs)
        if L.select_one('summary b').get_text()!=f"{sum(x.select_one('.rl-r')['class'][-1]=='W' for x in rs)}-{sum(x.select_one('.rl-r')['class'][-1]=='L' for x in rs)}-{sum(x.select_one('.rl-r')['class'][-1]=='P' for x in rs)}, {usd(tot)}": errs.append(('side list≠record',L['data-k']))
    print('sides check ok:',len(SIDES),'sides,',len(SFLAGS),'even-money games, no tracking side posted')
    # one shared card template: every card on every page has the same sections in the same order
    SECT=['cdh','gm','cd','cd-1','cd-b','cd-c','cd-ar','cd-2','cd-m','cd-3','cd-4','g-b','tbdc','tbdc-match','tbdc-meta','uc-h','uc','uc-r','uc-res']
    sigs={}
    for f in _gg.glob(R+'*.html'):
        for h in BeautifulSoup(open(f).read(),'html.parser').select('.cdh'):
            sig=[]
            for el in [h]+h.find_all(class_=True):
                c=[x for x in el.get('class',[]) if x in SECT]
                if c and (not sig or sig[-1]!=c[0]) and c[0] not in sig: sig.append(c[0])
            if h.select_one('.cd.full'): sig.append('mode:full')
            sigs.setdefault(tuple(sig),[]).append(f.split('/')[-1]+'#'+(h.details['id'] if h.details else '?'))
    _base={tuple(x for x in k if x!='mode:full') for k in sigs}
    if len(_base)!=1: errs.append(('card structure differs',{k:v[:3] for k,v in sigs.items()}))
    print('card template ok:',sum(len(v) for v in sigs.values()),'cards, 1 structure,',len(sigs),'mode(s)')
    # Site Auditor figures (data/audit_expected.txt): every figure must match
    def _f(t): return f"{t[0]}-{t[1]}-{t[2]} {usd(t[3])} n{t[4]}"
    def _pb(ks,rt,k,role='fade'):
        xs=[SDX[x][role] for x in ks if x in SDX and SDX[x][role]['rating']==rt and SDX[x][role][k+'_res']]; return _pt(xs,k)
    _mt=ml_tally
    def _figs():
        got={}
        for rt in ('STRONG','LEAN'):
            got[f'{rt} spread']=_f(at(rt)); got[f'{rt} fadeML']=_f(_mt(rt,('look back','live'))); got[f'{rt} postedML']=_f(POSTED['ml|'+rt])
            got[f'{rt} money sp']=_f(_stally('money',rt)); got[f'{rt} money ML']=_f(_stally('money',rt,True))
            got[f'{rt} bucket spread only']=_f(_pb(BUCKETS['spread'],rt,'sp')); got[f'{rt} bucket spread+ML']=_f(_pb(BUCKETS['both'],rt,'sp')); got[f'{rt} bucket spread+ML ML']=_f(_pb(BUCKETS['both'],rt,'ml'))
            for t in (1,2,3):
                if at(rt,t)[4]: got[f'{rt} T{t} spread']=_f(at(rt,t))
                for fd in ('Fav','Dog'):
                    if ml_at(rt,t,fd)[4]: got[f'{rt} T{t} {fd} ML']=_f(ml_at(rt,t,fd))
            for w in WEEKS:
                if at(rt,None,w)[4]: got[f'{rt} W{w} spread']=_f(at(rt,None,w))
        got['PASS money sp']=_f(_stally('money','PASS')); got['PASS money ML']=_f(_stally('money','PASS',True))
        got['PASS fade sp']=_f(_stally('fade','PASS')); got['PASS fade ML']=_f(_stally('fade','PASS',True))
        _bx={'spread only':len(BUCKETS['spread']),'pass money trend':len(BUCKETS['pass_money']),'spread+ML':len(BUCKETS['both']),'pass no clear side':len(BUCKETS['pass_even'])}
        return got,_bx
    # signed-off games (data/signed_off_games.json): their per-side rows are frozen, and every Site Auditor figure is
    # recomputed over exactly those games and must match data/audit_expected.txt on every build (never skipped).
    # Games settled since then may only add to the totals: all-games figure = signed-off figure + new-games figure.
    _nk=lambda w,g:(int(w),g.replace('LA@','LAR@'))
    _SO=json.load(open(R+'data/signed_off_games.json')); FZ={_nk(*k) for k in _SO['games']}
    _row=lambda x:[x['week'],x['game'],x['team'],x['role'],x['rating'],x['type'],x['fd'],x['sp_res'],x['sp_usd'],x['ml_res'],x['ml_usd']]
    _now=sorted(_row(x) for x in SIDES if _nk(x['week'],x['game']) in FZ)
    if _now!=sorted(_SO['rows']): errs.append(('signed-off per-game rows changed',[r for r in _now if r not in _SO['rows']][:5],[r for r in _SO['rows'] if r not in _now][:5]))
    if not FZ<={_nk(*k) for k in _DONE}: errs.append(('signed-off game no longer settled',sorted(FZ-{_nk(*k) for k in _DONE})))
    _G0=dict(RECS=RECS,ML=ML,SIDES=SIDES,POSTED=POSTED,BUCKETS=BUCKETS)
    def _subset(keep):
        gl=globals(); gl['RECS']=[r for r in _G0['RECS'] if keep(_nk(r['week'],r['game']))]; gl['ML']=[r for r in _G0['ML'] if keep(_nk(r['week'],r['game']))]
        gl['SIDES']=[x for x in _G0['SIDES'] if keep(_nk(x['week'],x['game']))]; gr=[x for x in gl['SIDES'] if x['sp_res']]
        gl['POSTED']={f'{m}|{rt}':_pt([x for x in gr if _OUR(x) and x['rating']==rt and (m=='sp' or ml_post(x))],m) for m in ('sp','ml') for rt in ('STRONG','LEAN')}
        gl['BUCKETS']={b:[k for k in v if keep(_nk(*k))] for b,v in _G0['BUCKETS'].items()}
        try: return _figs()
        finally: gl.update(_G0)
    got,_bx=_subset(lambda k:k in FZ); gotn,_=_subset(lambda k:k not in FZ); gota,_bxa=_figs()
    def _parse(v):
        q=re.match(r'(\d+)-(\d+)-(\d+) ([+−]?)\$([\d,]+) n(\d+)',v); return (int(q[1]),int(q[2]),int(q[3]),(-1 if q[4]=='−' else 1)*int(q[5].replace(',','')),int(q[6]))
    for k_,v_ in gota.items():
        a_=_parse(got[k_]) if k_ in got else (0,)*5; n_=_parse(gotn[k_]) if k_ in gotn else (0,)*5; t_=_parse(v_)
        if any(t_[i]!=a_[i]+n_[i] for i in (0,1,2,4)) or abs(t_[3]-a_[3]-n_[3])>len(gota): errs.append(('total is not signed-off + newly settled',k_,v_,got.get(k_),gotn.get(k_)))
    _exp={}
    for ln in open(R+'data/audit_expected.txt',encoding='utf-8'):
        if ' : ' in ln: k_,v_=ln.rstrip('\n').split(' : ',1); _exp[k_.strip()]=v_.strip()
    if int(_exp.pop('settled games','0'))!=len(FZ): errs.append(('audit_expected settled games != signed_off_games.json',len(FZ)))
    _new=len(_DONE)-len(FZ)
    if _new:
        _pend=[f'{k_} : {gota.get(k_)}   (signed off: {v_})' for k_,v_ in _exp.items() if k_!='buckets' and gota.get(k_)!=v_]
        open(R+'data/audit_pending.txt','w').write(f'settled games : {len(_DONE)} (signed off: {len(FZ)})\n'+''.join(x+'\n' for x in _pend))
        print(f'audit: {_new} newly settled game(s) on top of the {len(FZ)} signed off; all-games figures in data/audit_pending.txt')
    elif os.path.exists(R+'data/audit_pending.txt'): os.rename(R+'data/audit_pending.txt','/tmp/audit_pending.old.txt')
    for k_,v_ in _exp.items():
        if k_=='buckets':
            if eval(v_)!=_bx: errs.append(('audit mismatch','buckets',_bx,v_))
        elif got.get(k_)!=v_: errs.append(('audit mismatch',k_,got.get(k_),v_))
    # Rules v3.1: spread records over the signed-off games stay frozen; no Type 3 underdog moneyline ever posts
    for k_,v_ in (('STRONG spread','17-5-4 +$1,065 n26'),('LEAN spread','11-9-1 +$112 n21')):   # ca32973 + W6 SEA@DEN settled (DEN +2.5 −105 W)
        if got.get(k_)!=v_: errs.append(('spread records changed',k_,got.get(k_),v_))
    got=gota
    for r_ in SIDES:
        if r_['role']=='fade' and r_['type']==3 and r_['fd']=='Dog' and ml_post(r_): errs.append(('T3 underdog ML posted',r_['week'],r_['game']))
    for g_ in GALL:
        if g_['type']==3 and g_['rating']!='PASS' and g_['fade_line']>0 and re.search(r'ml-post|ML play',str(g_.get('mlhtml',''))): errs.append(('T3 underdog ML on W6 card',g_['gid']))
    if 'Type 3 underdog: pass on the moneyline; spread unaffected.' not in re.sub(r'<[^>]+>','',open(R+'tygif-how.html').read()): errs.append(('How missing T3 underdog rule',))
    # play highlight (STRONG green, LEAN orange) sits exactly on the posted play cells (our spread call; our ML when it posts)
    for f_ in ('index.html','tygif-tracker.html','tygif-deep-dive.html'):
        for h_ in BeautifulSoup(open(R+f_).read(),'html.parser').select('div.cdh'):
            g_=_GD[h_.select_one('details.gm')['id']]
            _ow={'sp'} if g_['rating']!='PASS' else set()
            if g_['rating']!='PASS' and ml_ok(g_): _ow.add('ml')
            got_={('sp' if 'cd-2' in c['class'] else 'ml' if 'cd-m' in c['class'] else 'other') for c in h_.select('.bet')}
            if got_!=_ow or len(h_.select('.bet'))!=len(_ow): errs.append(('orange cells',f_,g_['gid'],sorted(got_),sorted(_ow)))
            for c in h_.select('.bet'):
                if f'bet-{g_["rating"]}' not in c['class'] or len([k for k in c['class'] if k.startswith('bet-')])!=1: errs.append(('highlight hue',f_,g_['gid'],c['class']))
                if 'Pass' in c.select_one('.c1').get_text() or 'neu' in c.select_one('.c1')['class']: errs.append(('orange on a pass cell',f_,g_['gid']))
    _p6=_etlbl(max(g_['split_utc'] for g_ in G6))
    if f'As of {_p6}' not in re.sub(r'<[^>]+>','',open(R+'index.html').read()): errs.append(('W6 As of does not match the W6 pull',_p6))
    if 'Every game is graded at the DraftKings line, price and moneyline we recorded last before kickoff; where nothing was recorded, at the DraftKings closing numbers.' not in re.sub(r'<[^>]+>','',open(R+'tygif-how.html').read()): errs.append(('How grading sentence missing',))
    import slight_grade as _sgc
    for r_ in SIDES:   # graded at the last pre-kickoff DraftKings line wherever we saved one
        p_=_sgc.pre_line(r_['week'],*r_['game'].split('@'),r_['team'])
        if p_ and r_['sp_res'] and float(r_['spread_line'])!=float(p_['line']): errs.append(('not graded at pre-kickoff line',r_['week'],r_['game'],r_['team']))
    import pregame as _pg
    if _pg.build(R)!=json.load(open(R+'data/pregame_lines.json')): errs.append(('pregame_lines.json differs from the raw pulls',))
    for p_ in ML:
        q_=_sgc.pre_ml(p_['week'],*p_['game'].split('@'),p_['side'])
        if q_ is not None and p_['price']!=q_: errs.append(('ML not graded at pre-kickoff price',p_['game'],p_['price'],q_))
    for r_ in SIDES:
        q_=_sgc.pre_ml(r_['week'],*r_['game'].split('@'),r_['team'])
        if q_ is not None and r_['ml_res']=='W' and r_['ml_usd']!=r0(q_ if q_>0 else 10000/abs(q_)): errs.append(('side ML not at pre-kickoff price',r_['game'],r_['team']))
    for r_ in live_rows():
        p_=_sgc.pre_line(int(r_['week']),*r_['game'].split('@'),r_['our_side'])
        if p_ and r_['result'] and (float(r_['closing_line'].replace('−','-'))!=float(p_['line']) or int(r_['closing_price'].replace('−','-'))!=int(p_['price'])): errs.append(('live_log close != pre-kickoff pull',r_['game']))
    print('audit figures ok:',len(_exp),'matched')
    # closing rule: every W5 card uses the last pull before kickoff
    for gid_,sa_at,dk_at in CLOSE_APPLIED:
        c_=SETTLED[gid_]
        if c_['sao_last_before_kickoff']['at']!=sa_at: errs.append(('closing pull',gid_))
    if len(CLOSE_APPLIED)!=len(G)-1: errs.append(('closing rule not applied to every W5 game',len(CLOSE_APPLIED)))
    for g in GALL:
        if not (g['split_utc']<g['ko_utc'] and g['dk_utc']<g['ko_utc']): errs.append(('split after kickoff',g['gid'],g['split_utc'],g['dk_utc'],g['ko_utc']))
        for t_,src,d in _snaps('sao',_W+f"/snap_w{g['week']}_*/"):
            k_=frozenset((g['A'],g['H']))
            if g['split_utc']<t_<g['ko_utc'] and k_ in _sao_rows(d): errs.append(('W6 newer pre-kickoff pull ignored',g['gid'],t_))
        for t_,src,d in _snaps('dk',_W+f"/snap_w{g['week']}_*/"):
            if g['dk_utc']<t_<g['ko_utc'] and frozenset((g['A'],g['H'])) in _dk_rows(d): errs.append(('W6 newer pre-kickoff DraftKings pull ignored',g['gid'],t_))
    print(f'W{GW} pulls ok:',sorted({_etlbl(g['split_utc']) for g in G6}))
    if _etlbl('2026-11-08T18:00Z')!='Sun Nov 8, 12:00 PM CT': errs.append(('DST: 2026-11-08T18:00Z',_etlbl('2026-11-08T18:00Z')))
    if _etlbl('2026-10-18T18:00Z')!='Sun Oct 18, 1:00 PM CT': errs.append(('DST: 2026-10-18T18:00Z',_etlbl('2026-10-18T18:00Z')))
    if _fmt(_to_ct('Jan','10','1:00','PM'),', ')!='Sun Jan 10, 12:00 PM' : errs.append(('January year',_fmt(_to_ct('Jan','10','1:00','PM'),', ')))
    for f in _gg.glob(R+'*.html')+_gg.glob(R+'*.txt'):
        x=open(f,encoding='utf-8').read()
        if f.endswith('.html'):
            t=BeautifulSoup(x,'html.parser')
            for z in t(['style','script']): z.decompose()
            x=t.get_text(' ')
        for m in re.finditer(r' ET\b|Eastern',x): errs.append((f.split('/')[-1],'Eastern time shown',x[max(0,m.start()-40):m.end()+5]))
    assert not errs, errs
    print('deep check ok:', sum(n for v in want.values() for n in v[:3]), 'ML plays graded')
import os as _os
if _os.environ.get('SIGNOFF'):
    json.dump({'note':'Games Site Auditor signed off (2da0581). Per-side rows: week, game, team, role, rating, type, fd, sp_res, sp_usd, ml_res, ml_usd. Frozen: the build fails if any changes.',
               'games':sorted([list(k) for k in _DONE]),'rows':sorted([x['week'],x['game'],x['team'],x['role'],x['rating'],x['type'],x['fd'],x['sp_res'],x['sp_usd'],x['ml_res'],x['ml_usd']] for x in SIDES if (x['week'],x['game']) in set(_DONE))},open(_os.environ['SIGNOFF'],'w'),indent=0)
_deepcheck()

import os as _os
if _os.environ.get('DUMP'):
    _o=[]
    for g in G14+G+GALL:
        _o.append(dict(w=g.get('week'),gid=g['gid'],r=g.get('rating'),t=g.get('type'),side=g.get('fade'),line=g.get('fade_line'),res=(g.get('final') or {}).get('tag'),ml=bool(ml_ok(g)) if g.get('rating')!='PASS' else None))
    json.dump(_o,open(_os.environ['DUMP'],'w'),indent=0,default=str)
if _os.environ.get('DUMP'):
    json.dump({f'{r}{t}{fd}':ml_at(r,t,fd) for r in ('STRONG','LEAN') for t in (1,2,3) for fd in ('Fav','Dog')},open(_os.environ['DUMP']+'.grp','w'),default=str)
if _os.environ.get('POSTED'):
    def _t(xs,k): return (sum(x[k+'_res']=='W' for x in xs),sum(x[k+'_res']=='L' for x in xs),sum(x[k+'_res']=='P' for x in xs),sum(x[k+'_usd'] for x in xs))
    gr=[x for x in SIDES if x['week']<=5]
    oth=[x for x in gr if not (x['role']=='fade' and x['rating']!='PASS')]
    print('side spread posted',_t([x for x in oth if sp_post(x)],'sp'))
    print('side ML posted',_t([x for x in oth if ml_post(x)],'ml'))
    print('fade ML posted',_t([x for x in gr if x['role']=='fade' and x['rating']!='PASS' and ml_post(x)],'ml'))
    for rt in ('STRONG','LEAN'): print(rt,'fade ML posted',_t([x for x in gr if x['role']=='fade' and x['rating']==rt and ml_post(x)],'ml'))
if _os.environ.get('W6P'):
    for g in sorted(G6,key=_kick): print(f"{g['A']}@{g['H']}", 'splits', g['split_at'], g['split_src'].split()[-1], '| DK', _etlbl(g['dk_utc']), g['dk_src'].split()[-1], '| kickoff', g['ko_utc'])
