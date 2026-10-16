import os as _P_os
_B=_P_os.path.dirname(_P_os.path.abspath(__file__)); _I=_B+'/inputs'; _W=_P_os.environ.get('TYGIF_WORK',_B+'/raw'); _RR=_P_os.path.dirname(_B)+'/'
import json, sys, re
sys.path.insert(0,_B)
import uniform as u
from gamecards import AB, fmt
ROWS=json.load(open(_I+'/types_w14.json'))
CARD={(c['week'],c['game']):c['rating'] for c in json.load(open(_I+'/card_w14.json'))}
T={1:dict(name='Crowd piled on a big favorite',rule='65%+ of the money on a 6+ point favorite · take the underdog',bet=True),
   2:dict(name='Crowd piled on, no big favorite',rule='65%+ of the money and most bets on one side · take the other side',bet=True),
   3:dict(name='Crowd leaning',rule='55–64% of the money, or money and bets on different sides · LEAN at most',bet=True),
   4:dict(name='Books disagree',rule='All books and DraftKings have the money on different sides · no bet',bet=False),
   5:dict(name='No clear crowd',rule='Under 55% of the money on either side · no bet',bet=False)}
def wk5_type(G):
    if not G['c']: return 4
    if G['ab_m']<55: return 5
    if G['ab_m']>=65 and G['d']: return 1
    if G['ab_m']>=65 and G['a_ab']: return 2
    return 3
def trec(t):
    g=[r for r in ROWS if r['type']==t]; rr=[r['res'] for r in g if r['res']]
    w,l,p=rr.count('W'),rr.count('L'),rr.count('P')
    return dict(w=w,l=l,p=p,n=len(g),graded=len(rr),games=g)
def spell(w,l,p):
    return f"{w} win{'s' if w!=1 else ''}, {l} loss{'es' if l!=1 else ''}, {p} push{'es' if p!=1 else ''}"
def pct(r): return f"{round(100*r['w']/(r['w']+r['l']))}%" if r['w']+r['l'] else '—'
def tlabel(t): return f"Type {t} · {T[t]['name']}"
def games_list(t,R):
    items=[]
    for r in R['games']:
        mu=r['game'].replace('@',' at ')
        if r['side']:
            side=f"{r['side']} {fmt(r['line']).replace('-','−')}"
            res={'W':'win','L':'loss','P':'push'}[r['res']]; c={'W':'g','L':'r','P':''}[r['res']]
        else: side,res,c='even money','not graded',''
        pl=CARD.get((r['week'],r['game']))
        tag=f"<em class='mb {pl}'>{pl}</em>" if pl else ''
        items.append(f"<li><span>Week {r['week']} · {mu}{tag}</span><b class='{c}'>{side} · {res}</b></li>")
    return f"<details class='tbdc-games'><summary>See the {R['n']} game{'s' if R['n']!=1 else ''}</summary><ul>{''.join(items)}</ul></details>"
def type_block(t):
    R=trec(t); d=T[t]
    head=f"<div class='gt-top'><span class='gt-n'>{t}</span><div><div class='gt-k'>Game type</div><div class='gt-name'>{d['name']}</div><div class='gt-rule'>{d['rule']}</div></div></div>"
    if R['n']==0:
        rec="<div class='gt-rec'><div><b>Tracked from Week 5</b><span>Weeks 1–4 saved only one split per game</span></div></div>"
        return f"<div class='gt t{t}'>{head}{rec}</div>"
    lab='Weeks 1–4' if d['bet'] else 'Weeks 1–4 · had we bet against the money'
    cnt=f"{R['n']} games" + (f", {R['n']-R['graded']} at even money" if R['graded']<R['n'] else '')
    rec=f"<div class='gt-rec'><div><b>{spell(R['w'],R['l'],R['p'])}</b><span>{lab} · {cnt}</span></div><div class='gt-pct'>{pct(R)}<span>win rate</span></div></div>"
    return f"<div class='gt t{t}'>{head}{rec}{games_list(t,R)}</div>"
def body(G):
    full=u.body(G)
    t=wk5_type(G)
    # drop the matching-plays ladder (header + table + list) and put the type block first
    i=full.index("<div class='tbdc-h'>How plays like this") if "How plays like this" in full else full.index("<div class='tbdc-h'>If we had played it")
    core=full[:i]+'</div>'
    assert core.startswith("<div class='tbdc'>")
    core=core.replace("<div class='tbdc-h'>Rating checklist</div>","<div class='tbdc-h uc-h'>Rating checklist<span class='uc-key'>✓ helps the play · ✕ hurts it</span></div>",1)
    assert 'uc-key' in core
    return "<div class='tbdc'>"+type_block(t)+core[len("<div class='tbdc'>"):], t
