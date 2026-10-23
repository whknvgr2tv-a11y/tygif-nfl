#!/usr/bin/env python3
"""Fail when any game's DraftKings splits line/price differs from ESPN DraftKings in the same pull folder."""
import json, glob, os, re, sys
AL = {'WAS': 'WSH', 'JAC': 'JAX', 'LA Rams': 'LAR', 'LA Chargers': 'LAC', 'NY Jets': 'NYJ', 'NY Giants': 'NYG'}
def ab(name):
    for k, v in AL.items():
        if name.startswith(k + ' ') or name == k: return v
    return name.split()[0]
def norm(s): return s.replace('\u2212', '-').replace('PK', '0').strip()
def num(s):
    s = norm(str(s)); return 0.0 if s in ('0', 'EVEN') else float(s.replace('EVEN', '100'))
def _t(s):
    import datetime as dt; return dt.datetime.fromisoformat(s.replace('Z', '+00:00'))
def check(folder, espn=None):
    dk = sorted(glob.glob(folder + '/dk_*.json')); es = [espn] if espn else sorted(glob.glob(folder + '/espn_dk_*.json'))
    if not dk or not es: return []
    d = json.load(open(dk[-1])); e = json.load(open(es[-1])); pairs = {}
    if not e.get('games'): return [f"{os.path.basename(folder)}: ESPN DK {os.path.basename(es[-1])} has 0 games"]
    # An ESPN capture fetched at/after a game's kickoff is not a pre-kickoff price for that game: skip it.
    for g in e['games']:
        if g.get('kickoff_utc') and _t(e['fetched_utc']) >= _t(g['kickoff_utc']): continue
        pairs[(g['away'], g['home'])] = {g['away']: g['spread']['away'], g['home']: g['spread']['home']}
    bad = []
    for g in d['games']:
        a, h = [ab(x.strip()) for x in g['matchup'].split('@')]
        side = pairs.get((a, h))
        if side is None: continue   # not on ESPN's current week / already started
        for r in g['spread']:
            m = re.match(r'(\S+)\s.*?([+\-\u2212]?\d+(?:\.\d+)?|PK)$', r['side'])
            if not m: continue
            t = ab(r['side'])
            if t not in side: continue   # game already started on ESPN
            el, eo = side[t]['line'], side[t]['odds']
            if num(m.group(2)) != num(el) or num(r['odds']) != num(eo):
                bad.append(f"{os.path.basename(folder)} {t}: DK splits {m.group(2)} ({norm(r['odds'])}) vs ESPN DK {el} ({eo})")
    return bad
if __name__ == '__main__':
    a = sys.argv[1:]; es = None
    if '--espn' in a: i = a.index('--espn'); es = a[i + 1]; del a[i:i + 2]   # ESPN DK file outside the folder (e.g. data/espn_dk)
    fs = a or [max(glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/../build/raw/snap_w*_*'),
                   key=lambda f: os.path.basename(f).split('_', 2)[2])]   # newest by date_time stamp, any week
    bad = [b for f in fs for b in check(f, es)]
    print('\n'.join(bad) or 'dk/espn match ok'); sys.exit(1 if bad else 0)
