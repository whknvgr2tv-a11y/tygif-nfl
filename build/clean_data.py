import os as _P_os
_B=_P_os.path.dirname(_P_os.path.abspath(__file__)); _I=_B+'/inputs'; _W=_P_os.environ.get('TYGIF_WORK',_B+'/raw'); _RR=_P_os.path.dirname(_B)+'/'
from decimal import Decimal as _Dec, ROUND_HALF_UP as _RHU
import builtins as _bi
def r0(x): return int(_Dec(str(x)).quantize(_Dec('1'),_RHU))
def round(x,n=None): return r0(x) if n is None else _bi.round(x,n)   # half-up everywhere (TG, Oct 15)
import json, sys, html
sys.path.insert(0,_B)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import regrade_calc as rc, typecards as tc, gamecards as gc
E=html.escape
TY=tc.T
AB=dict(gc.AB); AB.update({'Kansas City':'KC','Carolina':'CAR'})
NAME={v:k for k,v in AB.items()}
NICK=dict(gc.NICK); NICK.update({'KC':'Chiefs','CAR':'Panthers'})
T={(r['week'],r['game']):r for r in json.load(open(_I+'/types_w14.json'))}
CARD={(r['week'],r['game']):r for r in json.load(open(_I+'/card_w14.json'))}
ARCH=rc.ARCH
G=json.load(open(_I+'/week5_refresh.json'))
for _g in G:  # QB factor removed (TG, Oct 15): re-rate without the QB drop
    if _g.get('f'):
        _g['f']=False; _g.pop('qbnote',None)
        if _g['gid']=='tbdal-card':
            _g['rating']='STRONG'; _g['why']='Starts at STRONG · no drops'; _g['wy']='66% of the money is on Dallas (all books).'
M='\u2212'
def ln(v):
    if v==0: return 'PK'
    s=f"{v:+g}"; return s.replace('-',M)
def usd(v):
    v=round(v)
    return '$0' if v==0 else (f"+${v:,}" if v>0 else f"{M}${-v:,}")
def rec(w,l,p):
    return f"{w}-{l}-{p}"
def tally(keys):
    w=sum(T[k]['res']=='W' for k in keys); l=sum(T[k]['res']=='L' for k in keys); p=sum(T[k]['res']=='P' for k in keys)
    return w,l,p,sum(T[k]['usd'] for k in keys),len(keys)
# QB1 didn't start (Weeks 1-4): our side's starter vs QB1
QBD={}  # QB factor removed from the model (TG, Oct 15)
REGRADE={(4,'DAL@HOU'):'Called LEAN at the time; regraded Oct 8 under the current rules.',
 (4,'DET@CAR'):'Called PASS at the time; regraded Oct 8 under the current rules.',
 (4,'ATL@NO'):'Called PASS at kickoff on the DraftKings split; regraded Oct 8 on the all-books split.',
 (3,'PHI@CHI'):'Called STRONG at the time; regraded Oct 8 under the current rules.',
 (1,'ATL@PIT'):'Called LEAN at the time; regraded Oct 8 under the current rules.',
 (2,'MIN@CHI'):'Called LEAN at the time; regraded Oct 8 under the current rules.',
 (3,'SEA@WSH'):'Called LEAN at the time; regraded Oct 8 under the current rules.',
 (3,'TEN@NYG'):'Called LEAN at the time; regraded Oct 8 under the current rules.'}
LV=['PASS','LEAN','STRONG']
def grade(k):
    """returns rating, steps list"""
    r=T[k]; ms=r['money_side']; mp=r['money_pct'] or 0
    steps=[]
    if not ms or mp<55: return 'PASS',steps
    if r['bets_side']!=ms: return 'PASS',steps
    lvl=2 if mp>=65 else 1
    mv=rc.mv_toward_money(k)
    # TG, Oct 25: line move no longer drops a level
    return LV[max(lvl,0)],steps
# --- Monday-line restatement (monday1): TeamRankings books 2-3, last quote before Monday 12:00 AM ET ---
MONDAY={(o['week'],o['game']):o for o in json.load(open(_RR+'data/monday_lines_w1-4.json'))['games']}
OLD_MV={k:rc.mv_toward_money(k) for k in T}
def _mv_monday(k):
    mvf=MONDAY[k]['monday_line_fav']-float(ARCH[k]['Spread'])
    return mvf if T[k]['money_side']==T[k]['fav'] else -mvf
rc.mv_toward_money=_mv_monday
OLD_CARD=dict(CARD)
CARD={}
for k in sorted(T):
    rt=grade(k)[0]
    if rt=='PASS': continue
    base=dict(OLD_CARD.get(k,{'week':k[0],'game':k[1],'type':T[k]['type'],'ourside':T[k]['side']}))
    base['rating']=rt; base['res']=T[k]['res']
    base.setdefault('play',f"{NAME[T[k]['side']]} {ln(T[k]['line'])}")
    CARD[k]=base
RESTATED={k:(OLD_CARD[k]['rating'] if k in OLD_CARD else 'PASS') for k in T if (OLD_CARD[k]['rating'] if k in OLD_CARD else 'PASS')!=(CARD[k]['rating'] if k in CARD else 'PASS')}
S=[k for k in CARD if CARD[k]['rating']=='STRONG']; L=[k for k in CARD if CARD[k]['rating']=='LEAN']

def bets_pct(k):
    a=ARCH[k]; fb=float(a['Fav bet % (spread)'].rstrip('%')); r=T[k]
    return round(fb if r['bets_side']==r['fav'] else 100-fb)
def play_text(k):
    p=CARD[k]['play']; return p.split(' (')[0].replace('-',M)
def short_play(k):
    r=T[k]; return f"{r['side']} {ln(r['line'])}"
def resword(k):
    return {'W':'win','L':'loss','P':'push'}[T[k]['res']]

for k,was in RESTATED.items():
    now=CARD[k]['rating'] if k in CARD else 'PASS'
    add=f"Was {was} before the Monday line was restated Oct 8 (TeamRankings, last quote before Monday); now {now}."
    REGRADE[k]=(REGRADE[k]+' '+add) if k in REGRADE else add
CALLED=[((4,'DAL@HOU'),'LEAN'),((4,'DET@CAR'),'PASS'),((4,'ATL@NO'),'PASS on the DraftKings split'),((3,'PHI@CHI'),'STRONG'),
        ((1,'ATL@PIT'),'LEAN'),((2,'MIN@CHI'),'LEAN'),((3,'SEA@WSH'),'LEAN'),((3,'TEN@NYG'),'LEAN')]
