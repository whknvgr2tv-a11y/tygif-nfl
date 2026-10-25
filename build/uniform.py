import os as _P_os
_B=_P_os.path.dirname(_P_os.path.abspath(__file__)); _I=_B+'/inputs'; _W=_P_os.environ.get('TYGIF_WORK',_B+'/raw'); _RR=_P_os.path.dirname(_B)+'/'
import re, json, sys
from bs4 import BeautifulSoup
sys.path.insert(0,_B)
from gamecards import AB, NICK, OUR, CROWD, fmt, wlp, cov, cls, cover_text, parse_line, parse_split
C=_I+'/before-src/'
rep=BeautifulSoup(open(C+'tygif-week-5-report.html').read(),'html.parser')
cards={c.select_one('.match').get_text(strip=True):c for c in rep.select('article.card')}
# published Weeks 1-4 play table
t=BeautifulSoup(open(C+'tygif-tracker.html').read(),'html.parser').find(id='results').select_one('.acard table')
P=[]
for tr in t.select('tbody tr'):
    wk,rg,play,money,res,usd=[td.get_text(' ',strip=True) for td in tr.find_all('td')]
    rating,game=rg.split(' ',1)
    P.append(dict(wk=wk,game=game,play=play,m=float(money.strip('%')),big='Big fav' in play,mv='Line moved against us' in play,res=res))
def rec(x): return dict(w=sum(r['res']=='W' for r in x),l=sum(r['res']=='L' for r in x),p=sum(r['res']=='P' for r in x),n=len(x),games=x)
def ladder_rows(hi,big,mv):
    x=P; L=[rec(x)]
    x=[r for r in x if (r['m']>=65)==hi]; L.append(rec(x))
    x=[r for r in x if r['big']==big]; L.append(rec(x))
    x=[r for r in x if r['mv']==mv]; L.append(rec(x))
    return L
QB={ # team -> (status text) for issues on that team, from the Tuesday card / TB Thursday update
 'TB':'Baker Mayfield out (thumb); Jalon Daniels starts','WSH':'Jayden Daniels questionable','CHI':'Caleb Williams out; Tyson Bagent starts','BAL':'Lamar Jackson questionable'}
TBOVR={'dk':(85,71),'ab':(69,72)}  # money, bets on Dallas (Thu update)
LEVEL=['PASS','LEAN','STRONG']
def opens_avg(s):
    v=[float(x) for x in re.findall(r'[+-]?\d+(?:\.\d+)?',s)]
    return sum(v)/len(v)
def game(gname, rating_pub):
    c=cards[gname]
    away,home=[x.strip() for x in gname.split(' at ')]
    chips=[x.get_text(' ',strip=True) for x in c.find('div',class_='strip',recursive=False).select('.chip')]
    team,line,opened,re_=parse_line(chips[0])
    other=home if team==away else away
    b1,m1=parse_split(chips[1]); b2,m2=parse_split(chips[2])   # team's DK bets/money, team's all-books bets/money
    if gname=='Tampa Bay at Dallas':
        m1,b1=100-TBOVR['dk'][0],100-TBOVR['dk'][1]; m2,b2=100-TBOVR['ab'][0],100-TBOVR['ab'][1]
    # all-books money side
    ab_side = team if m2>50 else other; ab_m = m2 if m2>50 else 100-m2
    ab_bets_on_side = b2 if ab_side==team else 100-b2
    dk_side = team if m1>50 else other; dk_m = m1 if m1>50 else 100-m1
    dk_bets_on_side = b1 if dk_side==team else 100-b1
    fade = other if ab_side==team else team
    a_ab = ab_bets_on_side>50; a_dk = dk_bets_on_side>50
    a = a_ab   # Fade the Crowd is read on the all-books split; DraftKings only has to have the money on the same side
    b = ab_m>=65
    cc = dk_side==ab_side
    # line from the money side's view: positive = money side became more favored
    line_ms = line if ab_side==team else -line
    open_ms = opens_avg(opened) if ab_side==team else -opens_avg(opened)
    toward = open_ms - line_ms   # e.g. money side +1.5 -> -7 : 8.5 toward money side
    d = line_ms<=-6
    e = toward>1
    f = AB[fade] in QB
    # rating from the checks
    if not cc: rt,why='PASS','DraftKings has the money on the other side'
    elif not a: rt,why='PASS','Money and bets on different sides'
    else:
        lvl=2 if b else 1; drops=[n for n,v in (('QB',f),) if v]   # TG, Oct 25: no line-move drop
        lvl-=len(drops); rt=LEVEL[max(lvl,0)]
        base='STRONG' if b else 'LEAN'
        why=f"Starts at {base}" + ("".join(f" · −1 for {x}" for x in drops) if drops else " · no drops")
    assert rt==rating_pub,(gname,rt,rating_pub)
    sp_team=fmt(line).replace('-','−'); sp_other=fmt(-line).replace('-','−')
    fade_line = line if fade==team else -line
    return dict(away=away,home=home,team=team,other=other,line=line,sp={AB[team]:sp_team,AB[other]:sp_other},opened=opened,re_=re_,
        ab_side=ab_side,ab_m=ab_m,ab_b=ab_bets_on_side,dk_side=dk_side,dk_m=dk_m,dk_b=dk_bets_on_side,a=a,a_ab=a_ab,a_dk=a_dk,b=b,c=cc,d=d,e=e,f=f,
        fade=fade,fade_line=fade_line,rating=rt,why=why,disagree=not cc,when=c.select_one('.when').get_text(strip=True),lad=ladder_rows(b,d,e))
def yn(v,good,neutral_no=False):
    if neutral_no and not v: return "<span class='uc-yn nu'><i>–</i>No</span>"
    ok = (v==good)
    return f"<span class='uc-yn {'ok' if ok else 'no'}'><i>{'✓' if ok else '✕'}</i>{'Yes' if v else 'No'}</span>"
def body(g):
    A,H=AB[g['away']],AB[g['home']]
    def tm(ab,side):
        border=OUR if (g['rating']!='PASS' and ab==AB[g['fade']]) else CROWD
        return f"<div class='tbdc-tm' style='border-{'left' if side=='l' else 'right'}:4px solid {border};{'text-align:right' if side=='r' else ''}'><div class='tbdc-ab'>{ab}</div><div class='tbdc-nm'>{NICK[ab]}</div><div class='tbdc-sp'>{g['sp'][ab]}</div></div>"
    head=f"<div class='tbdc-match'>{tm(A,'l')}<div class='tbdc-at'>@</div>{tm(H,'r')}</div><div class='tbdc-meta'>{g['when']}</div>"
    if g['rating']=='PASS':
        call=f"<div class='tbdc-call'><div><div class='tbdc-k'>The call</div><div class='tbdc-pick'>No bet</div></div><div class='tbdc-badge PASS'>PASS</div></div>"
    else:
        fl=fmt(g['fade_line']).replace('-','−')
        call=f"<div class='tbdc-call'><div><div class='tbdc-k'>The call</div><div class='tbdc-pick'>{g['fade']} {fl}</div><div class='tbdc-small'>{cover_text(g['fade'],g['fade_line'])}</div></div><div class='tbdc-badge {g['rating']}'>{g['rating']}</div></div>"
    ms=AB[g['ab_side']]
    opn=g['opened'].replace('-','−')
    now=g['sp'][AB[g['team']]]
    qbt=QB.get(AB[g['fade']],'no injury tag')
    rows=[('a','Money and bets on the same side',yn(g['a'],True),f"All books: {ms} {g['ab_m']}% money, {g['ab_b']}% bets"),
          ('b','65%+ of the money (all sportsbooks)',yn(g['b'],True),f"{g['ab_m']}% on {ms}"),
          ('c','DraftKings has the money on the same side',yn(g['c'],True),f"DraftKings: {AB[g['dk_side']]} {g['dk_m']}% of the money"),
          ('d','6+ point favorite holds the money',yn(g['d'],True,True),f"{ms} {g['sp'][ms]}"),
          ('e','Line moved over 1 pt toward the money',yn(g['e'],False),f"{'Reopened' if g['re_'] else 'Opened'} {AB[g['team']]} {opn}, now {now}"),
          ('f','Our QB1 isn’t playing (out, doubtful, questionable or IR)',yn(g['f'],False),f"{AB[g['fade']]}: {qbt}")]
    cl="<div class='tbdc-h'>Rating checklist</div><div class='uc'>"+''.join(f"<div class='uc-r'><span class='uc-l'>{k}</span><div class='uc-t'>{lab}<span class='uc-n'>{num}</span></div>{y}</div>" for k,lab,y,num in rows)+f"</div><div class='uc-res'><span>{g['why']}</span><b class='rb {g['rating']}'>{g['rating']}</b></div>"
    L=g['lad']
    lbl=['All plays','65%+ money' if g['b'] else 'Under 65% money','vs 6+ fav' if g['d'] else 'Not vs 6+ fav','Line moved' if g['e'] else 'Line steady']
    if g['rating']=='PASS':
        side=f"{AB[g['fade']]} {fmt(g['fade_line']).replace('-','−')}"
        hd=f"If we had played it <span>{side}{' · fading the all-books money side' if g['disagree'] else ''}</span>"
    else:
        hd="How plays like this have done <span>Weeks 1–4</span>"
    def rc(r): return f"{r['w']} W, {r['l']} L, {r['p']} P" if r['n'] else '—'
    def wp(r): return f"{round(100*r['w']/(r['w']+r['l']))}%" if r['w']+r['l'] else '—'
    trs=''.join(f"<tr class='{'fin' if i==3 else ''}'><th scope='row'>{lb}</th><td class='{cls(r['w'],r['l'])}'>{rc(r)}</td><td>{r['n']}</td><td class='{cls(r['w'],r['l'])}'>{wp(r)}</td></tr>" for i,(lb,r) in enumerate(zip(lbl,L)))
    lad=[f"<div class='tbdc-h'>{hd}</div><table class='lt'><thead><tr><th>Check</th><th>Record</th><th>Plays</th><th>Win %</th></tr></thead><tbody>{trs}</tbody></table>"]
    last=L[3]
    if last['n']:
        items=''.join(f"<li><span>Week {r['wk'][1:]} · {r['game'].replace('@',' at ')}</span><b class='{dict(W='g',L='r',P='').get(r['res'])}'>{re.sub(r' \(.*\)$','',r['play'])} · {dict(W='win',L='loss',P='push')[r['res']]}</b></li>" for r in last['games'])
        lad.append(f"<details class='tbdc-games'><summary>See the {last['n']} matching play{'s' if last['n']!=1 else ''}</summary><ul>{items}</ul></details>")
    return f"<div class='tbdc'>{head}{call}{cl}{''.join(lad)}</div>"
