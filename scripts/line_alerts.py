#!/usr/bin/env python3
"""Line-move alerts: compare each posted STRONG/LEAN play's DraftKings spread (newest dk_*.json)
with the posted line (data/current_card.json) or the last alerted line. A move of 0.5+ opens a GitHub
issue (label line-move). State: <snapdir>/alerts_state.json on the snapshots branch. Spreads only."""
import json, glob, os, sys, subprocess
from datetime import datetime, timezone, timedelta
D = sys.argv[1]; CARD = sys.argv[2] if len(sys.argv) > 2 else 'data/current_card.json'
TEST = os.environ.get('ALERT_TEST') == '1'
card = json.load(open(CARD))
files = sorted(glob.glob(f'{D}/dk_*.json'))
if not files: sys.exit('no DraftKings snapshot')
dk = json.load(open(files[-1])); fetched = datetime.fromisoformat(dk['fetched_utc'])
SP = 'state'; sp_path = f'{D}/alerts_state.json'
state = json.load(open(sp_path)) if os.path.exists(sp_path) else {}
def fmt(v): return 'PK' if v == 0 else f'{v:+g}'
cur = {}
for g in dk['games']:
    for s in g['spread']:
        t = s['side'].split(); cur[(g['matchup'], t[1])] = float(t[-1])
def ct(dt):  # US Central; CDT until Nov 1 2026, CST after
    off = 5 if dt < datetime(2026, 11, 1, 7, tzinfo=timezone.utc) else 6
    l = dt - timedelta(hours=off); return f"{l:%a %b} {l.day}, {int(l.strftime("%I"))}:{l:%M %p} {'CDT' if off == 5 else 'CST'}"
now = datetime.now(timezone.utc); opened = 0
for p in card['plays']:
    if datetime.fromisoformat(p['kickoff_utc'].replace('Z', '+00:00')) <= now: continue
    key = f"W{card['week']} {p['game']} {p['team']}"
    new = next((v for (m, n), v in cur.items() if n == p['nick']), None)
    if new is None: continue
    old = state.get(key, {}).get('line', float(p['line']))
    if TEST: new = old + 0.5
    if abs(new - old) < 0.5: continue
    title = f"{'[TEST] ' if TEST else ''}Line move: {p['nick']} {fmt(old)} -> {fmt(new)}"
    body = (f"{p['rating']} play: {p['name']} ({p['game']}, Week {card['week']})\n\n"
            f"- Posted line: {p['name']} {fmt(float(p['line']))} ({card['posted_at_et']})\n- Old line: {fmt(old)}\n- New line: {fmt(new)}\n"
            f"- DraftKings pull: {ct(fetched)}\n\nSpreads only. The play's rating is re-checked at the next card update.")
    r = subprocess.run(['gh', 'issue', 'create', '--label', 'line-move', '--title', title, '--body', body], capture_output=True, text=True)
    print(r.stdout or r.stderr); 
    if r.returncode: sys.exit(1)
    opened += 1
    if TEST: break
    state[key] = {'line': new, 'at': fetched.isoformat()}
json.dump(state, open(sp_path, 'w'), indent=1)
print(f'line alerts: {opened} opened')
