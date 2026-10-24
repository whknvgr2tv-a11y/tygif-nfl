"""Both sides of every game: fade side (against the money) and money side (follows the money).
Groups: spread = (rating, type, role); ML = (rating, type, role, Fav/Dog). Graded at the DraftKings close, flat $100, profit rounded per play."""
import os as _P_os
_B=_P_os.path.dirname(_P_os.path.abspath(__file__)); _I=_B+'/inputs'; _W=_P_os.environ.get('TYGIF_WORK',_B+'/raw'); _RR=_P_os.path.dirname(_B)+'/'

from decimal import Decimal as _Dec, ROUND_HALF_UP as _RHU
import builtins as _bi
def r0(x): return int(_Dec(str(x)).quantize(_Dec('1'),_RHU))
def round(x,n=None): return r0(x) if n is None else _bi.round(x,n)   # half-up everywhere (TG, Oct 15)
import json
import slight_grade as sg
def _opp(w,A,H,side):
    return A if sg.ALIAS.get(side,side)==sg.key(w,A,H)[2] else H
def _ml_px(w,A,H,side):
    """The price _ml grades at for this side (same sources, same order), or None."""
    x=sg.IX.get(sg.key(w,A,H))
    if not x: return None
    s=json.load(open(_W+f'/espn_sum/{x["id"]}.json')); home=sg.ALIAS.get(side,side)==sg.key(w,A,H)[2]
    for p in s.get('pickcenter',[]):
        if 'DraftKings' in p['provider']['name'] and p.get('moneyline'):
            o=((p['moneyline'].get('home' if home else 'away') or {}).get('close') or {}).get('odds')
            if not o or o=='OFF': return None
            pr=100 if o=='EVEN' else int(o.replace('+',''))
            if sg.pre_ml(w,A,H,side) is not None: pr=sg.pre_ml(w,A,H,side)
            elif w>=sg.PRE_ONLY: return None
            return pr
    return None
def _ml(w,A,H,side):
    x=sg.IX.get(sg.key(w,A,H))
    if not x: return None
    s=json.load(open(_W+f'/espn_sum/{x["id"]}.json')); home=sg.ALIAS.get(side,side)==sg.key(w,A,H)[2]
    for p in s.get('pickcenter',[]):
        if 'DraftKings' in p['provider']['name'] and p.get('moneyline'):
            o=((p['moneyline'].get('home' if home else 'away') or {}).get('close') or {}).get('odds')
            if not o or o=='OFF': return None
            pr=100 if o=='EVEN' else int(o.replace('+',''))
            if sg.pre_ml(w,A,H,side) is not None: pr=sg.pre_ml(w,A,H,side)   # last pre-kickoff DraftKings moneyline
            elif w>=sg.PRE_ONLY: return None   # weeks 6 on: nothing recorded before kickoff = no grade
            r=dict(fd=sg.fd_of(pr,_ml_px(w,A,H,_opp(w,A,H,side))),res=None,usd=None)
            if x['final']:
                a,h=int(x['a']),int(x['h']); mg=(h-a) if home else (a-h)
                r['res']='W' if mg>0 else 'L' if mg<0 else 'P'
                r['usd']=-100.0 if r['res']=='L' else 0.0 if r['res']=='P' else float(round(pr if pr>0 else 10000/-pr))
            return r
    return None
def build(games):
    """games: list of dict(week,A,H,rating,type,money,money_pct,bets,fade)"""
    rows=[];flags=[]
    for g in games:
        w,A,H=g['week'],g['A'],g['H']
        if not g['money'] or g['money_pct']<=50:
            flags.append((w,f'{A}@{H}','money split 50–50: no money side, no fade side')); continue
        ms=g['money']; fs=H if ms==A else A
        if g['rating']!='PASS': assert g['fade']==fs,(g,fs)
        for role,team in (('fade',fs),('money',ms)):
            s,_=sg.grade(w,A,H,team); m=_ml(w,A,H,team)
            rows.append(dict(week=w,game=f'{A}@{H}',team=team,role=role,rating=g['rating'],type=g['type'],
                money_pct=g['money_pct'] if role=='money' else 100-g['money_pct'],
                spread_line=s and s['line'],sp_res=s and s['res'],sp_usd=s and s['usd'],
                fd=m and m['fd'],ml_res=m and m['res'],ml_usd=m and m['usd']))
    return rows,flags
def grp(rows,rating,typ,role,fd=None,ml=False,before=None):
    rs=[r for r in rows if r['rating']==rating and r['type']==typ and r['role']==role and (before is None or r['week']<before)]
    if ml: rs=[r for r in rs if r['fd']==fd and r['ml_res']]; k='ml'
    else: rs=[r for r in rs if r['sp_res']]; k='sp'
    w=sum(r[k+'_res']=='W' for r in rs); l=sum(r[k+'_res']=='L' for r in rs); p=sum(r[k+'_res']=='P' for r in rs)
    return w,l,p,sum(r[k+'_usd'] for r in rs),len(rs)
