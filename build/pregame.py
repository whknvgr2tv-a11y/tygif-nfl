"""Rebuild the last pre-kickoff DraftKings line/price/moneyline for every game from the raw pulls.
Spread (all weeks): DraftKings splits page pulls (snapshots branch dk_* + scripts/snapshot.py pulls in build/raw/snap_w<N>_*).
Moneyline, Week 5: ESPN DraftKings odds saved Fri Oct 9 (data/odds_w5, times in data/odds_fetch_times.json).
Moneyline, Week 6 on: ESPN DraftKings captures (scripts/snapshot.py espn_dk_*: snapshots branch, data/espn_dk, build/raw/snap_w<N>_*).
Only numbers fetched before the game's kickoff are used; nothing fetched after kickoff is ever read."""
import os as _P_os
_B=_P_os.path.dirname(_P_os.path.abspath(__file__)); _I=_B+'/inputs'; _W=_P_os.environ.get('TYGIF_WORK',_B+'/raw'); _RR=_P_os.path.dirname(_B)+'/'

import json,glob,subprocess,os,datetime as dt
NK={'Cardinals':'ARI','Falcons':'ATL','Ravens':'BAL','Bills':'BUF','Panthers':'CAR','Bears':'CHI','Bengals':'CIN','Browns':'CLE','Cowboys':'DAL','Broncos':'DEN','Lions':'DET','Packers':'GB','Texans':'HOU','Colts':'IND','Jaguars':'JAX','Chiefs':'KC','Raiders':'LV','Chargers':'LAC','Rams':'LAR','Dolphins':'MIA','Vikings':'MIN','Patriots':'NE','Saints':'NO','Giants':'NYG','Jets':'NYJ','Eagles':'PHI','Steelers':'PIT','49ers':'SF','Seahawks':'SEA','Buccaneers':'TB','Titans':'TEN','Commanders':'WSH'}
RULE=('Grading line, price and moneyline = DraftKings at the last pull at least 5 min before kickoff: spreads from the DraftKings splits page pulls, '
      'moneylines from the ESPN DraftKings odds saved Fri Oct 9, 10:04 PM CT (Week 5) and from the ESPN DraftKings captures (Week 6 on). '
      'Games with nothing recorded before kickoff (Weeks 1-4, and Week 5 TB@DAL) use the DraftKings close from the ESPN game summary.')
FIRST_LIVE=5
def weeks():
    out=[]; w=FIRST_LIVE
    while os.path.exists(_W+f'/espn_sum/sb_w{w}.json'): out.append(w); w+=1
    return out
def _num(s): return float(str(s).replace('\u2212','-').replace('PK','0'))
# Narrow, documented exceptions: a DraftKings splits row that is a kickoff-transition placeholder, not a price.
# W7 NE@CHI dk_20261023T0014Z (7:14:55 PM CT, 5 s before kickoff): the splits page flipped kickoff to 8:20 PM ET and showed
# -110/-110 on both sides, while every pull from 5:58 PM on (dk_* and ESPN DK, incl. ESPN at 7:15:09 PM CT) had -108/-112.
# The line (-3) is unchanged; the price is taken from the previous DK splits pull (dk_20261023T0004Z, 7:04 PM CT). Site Auditor, Oct 22.
CUTOFF=dt.timedelta(minutes=5)   # TG, Oct 22: grade at the last saved pull at least 5 minutes before kickoff
def _iso(ts): return dt.datetime.fromisoformat(ts.replace('Z','+00:00'))
def build(R):
    git=lambda *a: subprocess.run(['git','-C',R]+list(a),capture_output=True,text=True).stdout
    br={'dk':[],'espn_dk':[]}
    for f in git('ls-tree','--name-only','-r','origin/snapshots','snapshots/').split():
        n=f.split('/')[-1]
        for k in ('dk','espn_dk'):
            if n.startswith(k+'_'): d=json.loads(git('show','origin/snapshots:'+f)); br[k].append((d['fetched_utc'],'snapshots branch '+n,d))
    out=[]
    for w in weeks():
        snaps=list(br['dk']); caps=list(br['espn_dk'])
        for f in glob.glob(_W+f'/snap_w{w}_*/dk_*.json'): d=json.load(open(f)); snaps.append((d['fetched_utc'],'scripts/snapshot.py pull '+f.split('/')[-1],d))
        for f in glob.glob(_W+f'/snap_w{w}_*/espn_dk_*.json'): d=json.load(open(f)); caps.append((d['fetched_utc'],'scripts/snapshot.py pull '+f.split('/')[-1],d))
        for f in glob.glob(R+'data/espn_dk/espn_dk_*.json'): d=json.load(open(f)); caps.append((d['fetched_utc'],'data/espn_dk/'+f.split('/')[-1],d))
        snaps.sort(key=lambda x:x[0]); caps.sort(key=lambda x:x[0])
        for e in json.load(open(_W+f'/espn_sum/sb_w{w}.json'))['events']:
            c=e['competitions'][0]; t={x['homeAway']:x['team']['abbreviation'] for x in c['competitors']}; A,H=t['away'],t['home']
            ko=_iso(e['date'])-CUTOFF; lo=ko-dt.timedelta(days=8)
            last=None
            for ts,src,d in snaps:
                if not (lo<_iso(ts)<=ko): continue
                for g in d['games']:
                    sp={NK[s['side'].split()[1]]:(_num(s['side'].split()[-1]),int(_num(s['odds']))) for s in g['spread']}
                    if set(sp)=={A,H}: last=(ts,src,sp)
            ml=None
            if w==5:
                f=R+f'data/odds_w5/{e["id"]}.json'; FT=json.load(open(R+'data/odds_fetch_times.json'))['fetched_utc']
                if e['id'] in FT and os.path.exists(f):
                    at=dt.datetime.fromisoformat(FT[e['id']])
                    if at<ko:
                        it=[i for i in json.load(open(f))['items'] if i['provider']['name']=='DraftKings'][0]
                        ml=(at.isoformat(timespec='seconds'),{A:int(it['awayTeamOdds']['moneyLine']),H:int(it['homeTeamOdds']['moneyLine'])},f'ESPN DraftKings odds data/odds_w5/{e["id"]}.json (saved Fri Oct 9)')
            else:
                for ts,src,d in caps:
                    if not (lo<_iso(ts)<=ko): continue
                    for g in d['games']:
                        if {g['away'],g['home']}=={A,H} and g['ml']['away'] and g['ml']['home'] and 'OFF' not in (g['ml']['away'],g['ml']['home']):
                            v=lambda o:100 if o=='EVEN' else int(o.replace('+',''))
                            ml=(ts,{g['away']:v(g['ml']['away']),g['home']:v(g['ml']['home'])},'ESPN DraftKings capture '+src)
            for side in (A,H):
                p=dict(week=w,game=f'{A}@{H}',side=side)
                if last: p.update(line=last[2][side][0],price=last[2][side][1],at_utc=last[0],source=last[1])
                if ml: p.update(ml=ml[1][side],ml_at_utc=ml[0],ml_source=ml[2])
                if len(p)>3: out.append(p)
    return {'rule':RULE,'lines':out}
if __name__=='__main__':
    R=_RR; json.dump(build(R),open(R+'data/pregame_lines.json','w'),indent=1); print('written')
