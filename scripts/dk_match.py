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
def check(folder):
    dk = sorted(glob.glob(folder + '/dk_*.json')); es = sorted(glob.glob(folder + '/espn_dk_*.json'))
    if not dk or not es: return []
    d = json.load(open(dk[-1])); e = json.load(open(es[-1])); pairs = {}
    for g in e['games']: pairs[(g['away'], g['home'])] = {g['away']: g['spread']['away'], g['home']: g['spread']['home']}
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
    fs = sys.argv[1:] or [sorted(glob.glob(os.path.dirname(os.path.abspath(__file__)) + '/../build/raw/snap_w6_*'))[-1]]
    bad = [b for f in fs for b in check(f)]
    print('\n'.join(bad) or 'dk/espn match ok'); sys.exit(1 if bad else 0)
