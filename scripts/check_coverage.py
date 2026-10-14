#!/usr/bin/env python3
"""Fail loudly (exit 1 + ::error::) when pre-kickoff coverage is missing.
1) Gap check: every game that kicked off in the last 36 h must have a DraftKings snapshot
   (dk_*.json containing it) fetched in the 90 minutes before its kickoff.
2) Now check: every game kicking off in the next 100 minutes must be in this run's DraftKings file.
Kickoff times come from the ScoresAndOdds snapshots (kickoff_utc)."""
import json, glob, sys, os
from datetime import datetime, timezone, timedelta
D = sys.argv[1] if len(sys.argv) > 1 else 'snapshots'
P = lambda s: datetime.fromisoformat(s.replace('Z', '+00:00'))
NICK = {'Cardinals':'ARI','Falcons':'ATL','Ravens':'BAL','Bills':'BUF','Panthers':'CAR','Bears':'CHI','Bengals':'CIN','Browns':'CLE',
        'Cowboys':'DAL','Broncos':'DEN','Lions':'DET','Packers':'GB','Texans':'HOU','Colts':'IND','Jaguars':'JAC','Chiefs':'KC',
        'Raiders':'LV','Chargers':'LAC','Rams':'LA','Dolphins':'MIA','Vikings':'MIN','Patriots':'NE','Saints':'NO','Giants':'NYG',
        'Jets':'NYJ','Eagles':'PHI','Steelers':'PIT','49ers':'SF','Seahawks':'SEA','Buccaneers':'TB','Titans':'TEN','Commanders':'WAS'}
def dk_games(d):
    out = set()
    for g in d['games']:
        a, h = [x.strip().split()[-1] for x in g['matchup'].split('@')]
        out.add(frozenset((NICK.get(a, a), NICK.get(h, h))))
    return out
now = datetime.now(timezone.utc)
dks = sorted((P(d['fetched_utc']), dk_games(d)) for d in (json.load(open(f)) for f in glob.glob(f'{D}/dk_*.json')))
ko = {}
for f in glob.glob(f'{D}/sao_*.json'):
    for g in json.load(open(f))['games']:
        if g.get('kickoff_utc'): ko[frozenset((g['away'], g['home']))] = (P(g['kickoff_utc']), f"{g['away']}@{g['home']}")
errs = []
for k, (t, name) in ko.items():
    if now - timedelta(hours=36) < t <= now:
        if not any(t - timedelta(minutes=90) <= ft < t and k in gs for ft, gs in dks):
            errs.append(f'{name} kicked off {t:%Y-%m-%d %H:%MZ} with no DraftKings snapshot in the 90 min before kickoff')
    if now < t <= now + timedelta(minutes=100) and dks and k not in dks[-1][1]:
        errs.append(f'{name} kicks off {t:%H:%MZ} but is missing from this run\'s DraftKings file')
for e in errs: print(f'::error::{e}')
print(f'coverage check: {len(ko)} games known, {len(errs)} problems')
sys.exit(1 if errs else 0)
