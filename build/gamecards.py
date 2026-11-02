import os as _P_os
_B=_P_os.path.dirname(_P_os.path.abspath(__file__)); _I=_B+'/inputs'; _W=_P_os.environ.get('TYGIF_WORK',_B+'/raw'); _RR=_P_os.path.dirname(_B)+'/'
import re, json
from bs4 import BeautifulSoup
AB={'Houston':'HOU','Tennessee':'TEN','Cleveland':'CLE','NY Jets':'NYJ','Cincinnati':'CIN','Miami':'MIA','NY Giants':'NYG','Washington':'WSH','Tampa Bay':'TB','Dallas':'DAL',
'Philadelphia':'PHI','Jacksonville':'JAX','Chicago':'CHI','Green Bay':'GB','Las Vegas':'LV','New England':'NE','Minnesota':'MIN','New Orleans':'NO','Indianapolis':'IND','Pittsburgh':'PIT',
'Denver':'DEN','LA Chargers':'LAC','Detroit':'DET','Arizona':'ARI','San Francisco':'SF','Seattle':'SEA','Baltimore':'BAL','Atlanta':'ATL','Buffalo':'BUF','LA Rams':'LAR'}
NICK={'HOU':'Texans','TEN':'Titans','CLE':'Browns','NYJ':'Jets','CIN':'Bengals','MIA':'Dolphins','NYG':'Giants','WSH':'Commanders','TB':'Buccaneers','DAL':'Cowboys','PHI':'Eagles','JAX':'Jaguars','CHI':'Bears','GB':'Packers','LV':'Raiders','NE':'Patriots','MIN':'Vikings','NO':'Saints','IND':'Colts','PIT':'Steelers','DEN':'Broncos','LAC':'Chargers','DET':'Lions','ARI':'Cardinals','SF':'49ers','SEA':'Seahawks','BAL':'Ravens','ATL':'Falcons','BUF':'Bills','LAR':'Rams'}
LAD=json.load(open(_I+'/ladders.json'))
SNAP='Tue Oct 6, 5:13 PM ET'
OUR='#d4a017'; CROWD='#6e737c'
def fmt(n): return ('+' if n>0 else ('−' if n<0 else '')) + (f"{abs(n):g}")
def wlp(w,l,p):
    s=f"{w} win{'s' if w!=1 else ''}, {l} loss{'es' if l!=1 else ''}"
    if p: s+=f", {p} push{'es' if p!=1 else ''}"
    return s
def cov(w,l): return f"{round(100*w/(w+l))}%" if w+l else '—'
def cls(w,l):
    if w+l==0: return ''
    r=w/(w+l); return 'g' if r>=0.6 else ('r' if r<0.5 else '')
def bar(label,pct,col_a,col_b):
    return f"<div class='tbdc-bar'><span>{label}</span><div class='tbdc-track'><i style='width:{pct}%;background:{col_a}'></i><i style='width:{100-pct}%;background:{col_b}'></i></div><span class='tbdc-pct'>{pct}%</span></div>"
def money_box(src,stamp,team_ab,money,bets,a_col,b_col):
    return f"<div class='tbdc-box'><div class='tbdc-bh'><span class='tbdc-src'>{src}</span><span class='tbdc-tmz'>{stamp}</span></div>{bar('Money on '+team_ab,money,a_col,b_col)}{bar('Bets on '+team_ab,bets,a_col,b_col)}</div>"
def cover_text(team,line):
    n=abs(line); plural = team.startswith('NY ') or team.endswith('s') and team not in('Dallas',)
    if line>0: return f"{team} {'need' if plural else 'needs'} to lose by {int(n)} or less, or win."
    return f"{team} {'need' if plural else 'needs'} to win by {int(n)+1} or more."
def head(away,home,ab_sp,our_ab,notes):
    a,h=AB[away],AB[home]
    def tm(ab,cls_,side):
        border=OUR if ab==our_ab else CROWD
        st=f"border-{'left' if side=='l' else 'right'}:4px solid {border}"
        return f"<div class='tbdc-tm' style='{st};{'text-align:right' if side=='r' else ''}'><div class='tbdc-ab'>{ab}</div><div class='tbdc-nm'>{NICK[ab]}{' · '+notes[ab] if notes.get(ab) else ''}</div><div class='tbdc-sp'>{ab_sp[ab]}</div></div>"
    return f"<div class='tbdc-match'>{tm(a,'',"l")}<div class='tbdc-at'>@</div>{tm(h,'',"r")}</div>"
def ladder(key, rows_lbl, qb_now):
    L=LAD[key]
    out=[f"<div class='tbdc-h'>How plays like this have done <span>Weeks 1–4 rated plays · same 4 checks for every play</span></div>",
         "<div class='tbdc-row hd'><div class='tbdc-lbl'>Matching plays</div><div class='tbdc-rec'>Result</div><div class='tbdc-cv'>Covered</div></div>"]
    for i,(lbl,r) in enumerate(zip(rows_lbl,L)):
        last=i==len(L)-1
        out.append(f"<div class='tbdc-row{' ind' if i else ''}{' ex' if last else ''}'><div class='tbdc-lbl'>{lbl}<span class='tbdc-gm'>{r['n']} plays</span></div><div class='tbdc-rec {cls(r['w'],r['l'])}'>{wlp(r['w'],r['l'],r['p'])}</div><div class='tbdc-cv {cls(r['w'],r['l'])}'>{cov(r['w'],r['l'])}</div></div>")
    last=L[-1]
    def gi(g):
        m=re.match(r'^W(\d) (\S+) (.+?)(?: \(.*\))? ([WLP])$',g)
        return f"<li><span>Week {m.group(1)} · {m.group(2).replace('@',' at ')}</span><b class='{dict(W='g',L='r',P='').get(m.group(4))}'>{m.group(3)} · {dict(W='win',L='loss',P='push')[m.group(4)]}</b></li>"
    items=''.join(gi(g) for g in last['games'])
    out.append(f"<details class='tbdc-games'><summary>See the {last['n']} matching plays</summary><ul>{items}</ul></details>")
    out.append(f"<p class='tbdc-qb'>QB status is not one of the 4 checks: Weeks 1–4 plays weren't scored for it. This week: {qb_now}</p>")
    return ''.join(out)
LADDER_LBL={True:['All STRONG and LEAN plays','…with 65%+ of the money on the other side','…against a 6+ point favorite holding the money','…line not moved more than 1 pt toward the money'],
            False:['All STRONG and LEAN plays','…with 65%+ of the money on the other side','…not against a 6+ point favorite holding the money','…line not moved more than 1 pt toward the money']}
FOOT="<div class='tbdc-foot'>Covered % leaves out pushes · small samples · not financial advice</div>"

def parse_line(chip):
    m=re.match(r'Line (.+?) ([+-]?\d+(?:\.\d+)?) · (re)?opened (.+)',chip)
    return m.group(1), float(m.group(2)), m.group(4), bool(m.group(3))
def parse_split(chip):
    m=re.search(r'(\d+)% bets · (\d+)% money',chip); return int(m.group(1)),int(m.group(2))

def play_card(c, rating, team_call, why_extra, qb_now, qb_box, key, stamp_dk=SNAP, stamp_ab='ScoresAndOdds · '+SNAP, line_sub=None, meta_extra='', dk=None, ab=None, line_big=None):
    away,home=[x.strip() for x in c.select_one('.match').get_text().split(' at ')]
    when=c.select_one('.when').get_text(strip=True)
    chips=[x.get_text(' ',strip=True) for x in c.select('.strip .chip')]
    team,line,opened,re_=parse_line(chips[0])
    our=AB[team]; opp_name= home if team==away else away; opp=AB[opp_name]
    sp={our:fmt(line).replace('-','−'), opp:fmt(-line).replace('-','−')}
    if dk is None:
        b,mn=parse_split(chips[1]); dk=(100-mn,100-b)
        b,mn=parse_split(chips[2]); ab=(100-mn,100-b)
    big = '✓' == [r.select_one('.clist-mark').text for r in c.select('.clist-row')][2]
    notes={our: qb_box[2]} if qb_box[2] else {}
    h=head(away,home,sp,our,notes)
    meta=f"<div class='tbdc-meta'>{when} · Line: DraftKings{meta_extra}</div>"
    call=f"<div class='tbdc-call'><div><div class='tbdc-k'>The call</div><div class='tbdc-pick'>{team} {sp[our]}</div><div class='tbdc-small'>{cover_text(team,line)}</div></div><div class='tbdc-badge {rating}'>{rating}</div></div>"
    why=[f"Most of the money and most of the bets are on {opp_name}. We bet the other side."]
    if big: why.append(f"{opp_name} is a big favorite ({abs(line):g} points) holding the money, and big favorites the crowd loves have struggled to cover.")
    why.append(f"DraftKings has {dk[0]}% of the money on {opp_name} (all books {ab[0]}%), above the 65% needed for STRONG.")
    why+=why_extra
    whyh="<div class='tbdc-h'>Why</div><ul class='tbdc-why'>"+''.join(f'<li>{w}</li>' for w in why)+"</ul>"
    money=(f"<div class='tbdc-h'>Where the money is <span>{opp} = the crowd side</span></div><div class='tbdc-2'>"
           f"{money_box('DraftKings',stamp_dk,opp,dk[0],dk[1],CROWD,OUR)}{money_box('All books',stamp_ab,opp,ab[0],ab[1],CROWD,OUR)}</div>"
           f"<div class='tbdc-leg'><b style='background:{CROWD}'></b>{opp_name} &nbsp; <b style='background:{OUR}'></b>{team} &nbsp;·&nbsp; Both sources agree: the money is on {opp_name}.</div>")
    lb=line_big or (f"{'Reopened' if re_ else 'Opened'} {our} {opened.replace('-','−')} → Now {sp[our]}")
    ls=line_sub or "Not more than 1 point toward the money, so the rating holds. Source: DraftKings now; opening line(s) as listed on the Tuesday card."
    boxes=(f"<div class='tbdc-2' style='margin-top:12px'><div class='tbdc-box'><div class='tbdc-h' style='margin-top:0'>Line movement</div><div class='tbdc-big'>{lb}</div><div class='tbdc-sub'>{ls}</div></div>"
           f"<div class='tbdc-box'><div class='tbdc-h' style='margin-top:0'>QB situation</div><div class='tbdc-big'>{qb_box[0]}</div><div class='tbdc-sub'>{qb_box[1]}</div></div></div>")
    lad=ladder(key, LADDER_LBL[big], qb_now)
    return f"<div class='tbdc'>{h}{meta}{call}{whyh}{money}{boxes}{lad}{FOOT}</div>"

PASS_REC={'disagree':("Sportsbooks disagree","Tracked starting Week 5. No results yet."),
 'sharps':("Big bettors vs the public · Weeks 1–4 · 20 games","Betting against the money: 8 wins, 12 losses (−$483). Following it: 12 wins, 8 losses (+$268). That is why we pass."),
 'noplay':("Rated PASS (no edge) · Weeks 1–4 · 6 games","Had we bet against the money: 2 wins, 4 losses (−$203).")}
def pass_card(c, kind):
    away,home=[x.strip() for x in c.select_one('.match').get_text().split(' at ')]
    when=c.select_one('.when').get_text(strip=True)
    chips=[x.get_text(' ',strip=True) for x in c.find('div',class_='strip',recursive=False).select('.chip')]
    team,line,opened,re_=parse_line(chips[0])
    t=AB[team]; other_name= home if team==away else away; o=AB[other_name]
    sp={t:fmt(line).replace('-','−'), o:fmt(-line).replace('-','−')}
    h=head(away,home,sp,None,{})
    reason={'disagree':'Sportsbooks disagree on where the money is.','sharps':'Big bettors and the public are on opposite sides.','noplay':'Mixed signals and the line moved against us.'}[kind]
    call=f"<div class='tbdc-call'><div><div class='tbdc-k'>The call</div><div class='tbdc-pick'>No bet</div><div class='tbdc-small'>{reason}</div></div><div class='tbdc-badge PASS'>PASS</div></div>"
    lis=[li.get_text(' ',strip=True) for li in c.find('ul',recursive=False).find_all('li')]
    lis=[re.sub(r'^Sharps split at DraftKings','Split at DraftKings',x).replace('fading the sharps lost money','betting against big bettors lost money').replace('Reverse line move against us','Line moved against the bets') for x in lis]
    whyh="<div class='tbdc-h'>Why</div><ul class='tbdc-why'>"+''.join(f'<li>{w}</li>' for w in lis)+"</ul>"
    b1,m1=parse_split(chips[1]); b2,m2=parse_split(chips[2])
    money=(f"<div class='tbdc-h'>Where the money is <span>shown for {team}</span></div><div class='tbdc-2'>"
           f"{money_box('DraftKings',SNAP,t,m1,b1,'#9a9da4',CROWD)}{money_box('All books','ScoresAndOdds · '+SNAP,t,m2,b2,'#9a9da4',CROWD)}</div>")
    lb=f"{'Reopened' if re_ else 'Opened'} {t} {opened.replace('-','−')} → Now {sp[t]}"
    line=f"<div class='tbdc-2' style='margin-top:12px'><div class='tbdc-box'><div class='tbdc-h' style='margin-top:0'>Line movement</div><div class='tbdc-big'>{lb}</div><div class='tbdc-sub'>Source: DraftKings now; opening line(s) as listed on the Tuesday card.</div></div>"
    ou=c.find('div',class_='ou',recursive=False)
    if ou:
        best=ou.select_one('.best').get_text(' ',strip=True)
        m=re.search(r'\(would be (\w+)\)',best)
        first=ou.select('ul li')[0].get_text(' ',strip=True)
        line+=f"<div class='tbdc-box'><div class='tbdc-h' style='margin-top:0'>Total · tracked only</div><div class='tbdc-big'>{ou.select_one('.ocall').get_text(strip=True)}</div><div class='tbdc-sub'>Would be {m.group(1) if m else 'rated'}, but totals are never played. {first}</div></div>"
    line+="</div>"
    lbl,txt=PASS_REC[kind]
    rec=f"<div class='tbdc-h'>How this kind of pass has done</div><div class='tbdc-row'><div class='tbdc-lbl'>{lbl}<span class='tbdc-gm'>{txt}</span></div></div>"
    return f"<div class='tbdc'>{h}<div class='tbdc-meta'>{when} · Line: DraftKings</div>{call}{whyh}{money}{line}{rec}<div class='tbdc-foot'>Pass games are graded both ways once final · not financial advice</div></div>"
