import os as _P_os
_B=_P_os.path.dirname(_P_os.path.abspath(__file__)); _I=_B+'/inputs'; _W=_P_os.environ.get('TYGIF_WORK',_B+'/raw'); _RR=_P_os.path.dirname(_B)+'/'
import json,csv,copy
T={(r['week'],r['game']):r for r in json.load(open(_I+'/types_w14.json'))}
ARCH={}
for i,wk in [(4,1),(3,2),(2,3),(1,4)]:
    for r in csv.DictReader(open(_W+f'/audit_src/arch_t{i}.csv')):
        g=f"{r['Away team']}@{r['Home team']}"; ARCH[(wk,g)]=r
def card(new):
    c=json.load(open(_I+'/card_w14.json'))
    c={(x['week'],x['game']):x for x in c}
    if new:
        if (3,'PHI@CHI') in c: c[(3,'PHI@CHI')]['rating']='LEAN'
        c[(4,'DAL@HOU')]['rating']='STRONG'
        c[(4,'DET@CAR')]=dict(week=4,rating='LEAN',game='DET@CAR',play='Carolina +3.5',money='56%',res='W',type=3,ourside='CAR')
    return c
def rec(keys):
    w=l=p=0; usd=0.0
    for k in keys:
        r=T[k]
        if r['res']=='W': w+=1
        elif r['res']=='L': l+=1
        elif r['res']=='P': p+=1
        usd+=r['usd'] or 0
    return w,l,p,round(usd,2),len(keys)
def mv_toward_money(k):
    r=ARCH[k]; mv=float(r['Move from weekly reopen (toward fav +)'] or 0)
    return mv if T[k]['money_side']==T[k]['fav'] else -mv
for new in (False,True):
    C=card(new); print('NEW' if new else 'OLD')
    for rt in ('STRONG','LEAN'): print(' ',rt,rec([k for k,v in C.items() if v['rating']==rt]))
    print('  All',rec(list(C)))
    for w in (3,4): print('  week',w,rec([k for k in C if k[0]==w]))
    ftc=[k for k,r in T.items() if r['bets_side']==r['money_side'] and r['money_pct'] and r['money_pct']>=55 and r['side']]
    # base strong
    base_s=[k for k in ftc if T[k]['money_pct']>=65]
    print('  heavy/base strong(theory)',rec(base_s))
    pub_base_s=[k for k in base_s if not (not new and k==(4,'DAL@HOU'))]
    print('  base STRONG (published def)',rec(pub_base_s))
    down=[k for k in ftc if mv_toward_money(k)>1]
    print('  downgraded by move (FTC>=55)',rec(down), sorted(down))
    passes=[k for k in ftc if k not in C]
    print('  FTC not on card',rec(passes),passes)

def bd(new):
    C=card(new); out={}
    def add(key,k): out.setdefault(key,[]).append(k)
    for k in C:
        r=T[k]; a=ARCH[k]; m=r['money_pct']
        add('m65+' if m>=65 else 'm55-64',k)
        s=abs(r['fav_line']); add('<3' if s<3 else '3-5.5' if s<6 else '6-9.5' if s<10 else '10+',k)
        add('loc_'+a['Favorite home/road/neutral'],k)
        add('prime' if a['Primetime (Y/N)']=='Y' else 'day',k)
        add('div' if a['Divisional (Y/N)']=='Y' else 'nondiv',k)
        mv=float(a['Move from weekly reopen (toward fav +)'] or 0); add('tfav' if mv>0 else 'tdog' if mv<0 else 'nomove',k)
        if k[0]>=2: add('rest_'+a['Rest advantage'],k)
    return {x:rec(v) for x,v in out.items()}
if __name__=='__main__':
    o=bd(False); n=bd(True)
    for x in sorted(o): print(x,o[x],'->',n[x])

def other(keys):
    w=l=p=0; usd=0.0
    for k in keys:
        r=T[k]; a=ARCH[k]
        od=[o for o in json.load(open(_W+'/audit_src/odds/'+a['ESPN event id']+'.json'))['items'] if o['provider']['name']=='DraftKings'][0]
        ours_home = (r['side']==a['Home team'])
        oth = od['awayTeamOdds'] if ours_home else od['homeTeamOdds']
        pr=float(oth['close']['spread']['american'])
        res={'W':'L','L':'W','P':'P'}[r['res']]
        if res=='W': w+=1; usd+= (100/abs(pr)*100 if pr<0 else pr)
        elif res=='L': l+=1; usd-=100
        else: p+=1
    return w,l,p,round(usd,2)
