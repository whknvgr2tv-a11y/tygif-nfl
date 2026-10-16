import os as _P_os
_B=_P_os.path.dirname(_P_os.path.abspath(__file__)); _I=_B+'/inputs'; _W=_P_os.environ.get('TYGIF_WORK',_B+'/raw'); _RR=_P_os.path.dirname(_B)+'/'
from decimal import Decimal as _Dec, ROUND_HALF_UP as _RHU
import builtins as _bi
def r0(x): return int(_Dec(str(x)).quantize(_Dec('1'),_RHU))
def round(x,n=None): return r0(x) if n is None else _bi.round(x,n)   # half-up everywhere (TG, Oct 15)
import json,os as _os
PRE_ONLY=6   # from Week 6 on, grade only from numbers recorded before kickoff (never an ESPN summary)
WEEKS=[]
while _os.path.exists(_W+f'/espn_sum/sb_w{len(WEEKS)+1}.json'): WEEKS.append(len(WEEKS)+1)
def _ix():
    ix={}
    for w in WEEKS:
        for e in json.load(open(_W+f'/espn_sum/sb_w{w}.json'))['events']:
            c=e['competitions'][0]; t={x['homeAway']:x for x in c['competitors']}
            ix[(w,t['away']['team']['abbreviation'],t['home']['team']['abbreviation'])]=dict(id=e['id'],a=t['away'].get('score'),h=t['home'].get('score'),final=c['status']['type']['name']=='STATUS_FINAL')
    return ix
IX=_ix()
ALIAS={'LA':'LAR','WAS':'WSH','JAC':'JAX'}
def key(w,A,H):
    A=ALIAS.get(A,A); H=ALIAS.get(H,H); return (w,A,H)
def dk_spread(w,A,H):
    x=IX.get(key(w,A,H))
    if not x: return None
    s=json.load(open(_W+f'/espn_sum/{x["id"]}.json'))
    for p in s.get('pickcenter',[]):
        if 'DraftKings' in p['provider']['name'] and p.get('pointSpread'):
            ps=p['pointSpread']; return x,ps
    return x,None
ROOT=None; _PRE=None
def set_root(r):
    global ROOT,_PRE; ROOT=r; _PRE=None
def _pre():
    global _PRE
    if _PRE is None:
        assert ROOT, 'slight_grade.set_root(R) first'
        _PRE={(p['week'],p['game'],p['side']):p for p in json.load(open(ROOT+'data/pregame_lines.json'))['lines']}
    return _PRE
def pre_line(w,A,H,side):
    p=_pre().get((w,f'{A}@{H}',side)); return p if p and 'line' in p else None
def pre_ml(w,A,H,side):
    p=_pre().get((w,f'{A}@{H}',side)); return p['ml'] if p and 'ml' in p else None
def grade(w,A,H,side):
    """side abbr; returns dict(line, price, res, usd) or None + reason"""
    r=dk_spread(w,A,H)
    if not r: return None,'game not in ESPN index'
    x,ps=r; H2=key(w,A,H)[2]; home=ALIAS.get(side,side)==H2
    if not ps: return None,'no DraftKings spread in ESPN summary'
    c=ps['home' if home else 'away']['close']
    try: line=float(c['line']); price=int(str(c['odds']).replace('+','')) if c['odds'] not in ('EVEN',) else 100
    except Exception: return None,'DraftKings close missing'
    p_=pre_line(w,A,H,side)
    if p_: line,price=float(p_['line']),int(p_['price'])   # last pre-kickoff DraftKings line (TG, Oct 15)
    elif w>=PRE_ONLY: return None,'no DraftKings line recorded before kickoff'
    if not x['final']: return dict(line=line,price=price,res=None,usd=None),None
    a,h=int(x['a']),int(x['h']); mg=(h-a) if home else (a-h); m=mg+line
    res='W' if m>0 else ('L' if m<0 else 'P')
    usd=-100.0 if res=='L' else 0.0 if res=='P' else float(round(price if price>0 else 10000/abs(price)))
    return dict(line=line,price=price,res=res,usd=usd),None
