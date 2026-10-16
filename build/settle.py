#!/usr/bin/env python3
"""Weekly settle: one command from a fresh checkout.

  python3 build/settle.py            # fetch, pull, settle, build twice, deep checks
  python3 build/settle.py --offline  # skip network (rebuild from what is in build/raw + origin/snapshots)
  python3 build/settle.py --monday   # Monday run: first build/monday_lines.py for the next week (TeamRankings books 2-3,
                                     # last quote before Sun 11 PM CT -> build/inputs/tr_monday_w<N>.json), then the settle

1. git fetch origin snapshots (pre-kickoff DraftKings/ScoresAndOdds/ESPN-DraftKings pulls).
2. ESPN scoreboard for every live week (6 on, each with build/inputs/tr_monday_w<N>.json) into
   build/raw/pulls/<UTC stamp>/sb_w<N>.json, then copied to build/raw/espn_sum/sb_w<N>.json,
   the one scoreboard copy the build reads scores and status from.
   Game summaries go to the same dated folder, kept apart:
     prekick/<event>.json   fetched while the game was still scheduled -> also written as an ESPN DraftKings
                            capture data/espn_dk/espn_dk_<stamp>.json (the grading moneyline source)
     postgame/<event>.json  fetched after kickoff -> kept for the record, never used for grading
3. build/pregame.py rebuilds data/pregame_lines.json (last numbers recorded before kickoff).
4. build/clean_build.py with TYGIF_SETTLE=1 adds live_log rows for final STRONG/LEAN games, builds, runs the deep checks.
5. Builds again and requires byte-identical output.
"""
import json, os, sys, glob, hashlib, subprocess, time, urllib.request, importlib.util
from datetime import datetime, timezone
B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(B); RAW = os.environ.get('TYGIF_WORK', B + '/raw')
SB = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?seasontype=2&week={w}&dates={y}'
SUM = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={}'
_sp = importlib.util.spec_from_file_location('snapmod', R + '/scripts/snapshot.py'); snap = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(snap)

def run(*a, env=None):
    print('$', ' '.join(a)); subprocess.run(a, cwd=R, check=True, env=dict(os.environ, **(env or {})))

def trim(s):   # keep only what the build reads: the DraftKings pickcenter entries
    return {'pickcenter': [p for p in s.get('pickcenter', []) if 'DraftKings' in p['provider']['name']]}

def pull():
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%MZ'); out = f'{RAW}/pulls/{stamp}'
    os.makedirs(out + '/prekick', exist_ok=True); os.makedirs(out + '/postgame', exist_ok=True)
    w = 6; caps = []
    while os.path.exists(f'{B}/inputs/tr_monday_w{w}.json'):
        y = json.load(open(f'{RAW}/espn_sum/sb_w{w - 1}.json'))['season']['year']
        st, h = snap.get(SB.format(w=w, y=y)); sb = json.loads(h)
        for p in (f'{out}/sb_w{w}.json', f'{RAW}/espn_sum/sb_w{w}.json'):
            json.dump(sb, open(p, 'w'))
        for e in sb['events']:
            state = e['competitions'][0]['status']['type']['state']
            st, h = snap.get(SUM.format(e['id'])); s = json.loads(h); now = datetime.now(timezone.utc)
            pre = state == 'pre' and now < datetime.fromisoformat(e['date'].replace('Z', '+00:00'))
            json.dump(dict(trim(s), fetched_utc=now.isoformat(timespec='seconds'), state=state), open(f'{out}/{"prekick" if pre else "postgame"}/{e["id"]}.json', 'w'))
            if pre:
                g = snap.espn_dk_game(e, s)
                if g: caps.append(g)
            if not os.path.exists(f'{RAW}/espn_sum/{e["id"]}.json'):   # index file only; weeks 6 on never grade from it
                json.dump(trim(s), open(f'{RAW}/espn_sum/{e["id"]}.json', 'w'), separators=(',', ':'))
            time.sleep(0.3)
        print(f'week {w}: {len(sb["events"])} games,', sum(e["competitions"][0]["status"]["type"]["name"] == "STATUS_FINAL" for e in sb["events"]), 'final')
        w += 1
    if caps:
        os.makedirs(R + '/data/espn_dk', exist_ok=True)
        json.dump({'fetched_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'source': 'build/settle.py (ESPN game summaries, games not yet started)',
                   'games': caps}, open(f'{R}/data/espn_dk/espn_dk_{stamp}.json', 'w'), indent=1)
    print('pulled into', out)

def site_hash():
    h = hashlib.sha256()
    for f in sorted(glob.glob(R + '/*.html') + glob.glob(R + '/*.txt') + glob.glob(R + '/data/*.json') + glob.glob(R + '/data/*.csv')):
        h.update(f.encode()); h.update(open(f, 'rb').read())
    return h.hexdigest()

def main():
    if '--monday' in sys.argv:
        w = 6
        while os.path.exists(f'{B}/inputs/tr_monday_w{w}.json'): w += 1
        run(sys.executable, 'build/monday_lines.py', '--week', str(w))
    if '--offline' not in sys.argv:
        run('git', 'fetch', 'origin', 'snapshots:refs/remotes/origin/snapshots')
        pull()
    run(sys.executable, 'build/pregame.py')
    run(sys.executable, 'build/clean_build.py', env={'TYGIF_SETTLE': '1'})
    h1 = site_hash()
    run(sys.executable, 'build/clean_build.py'); h2 = site_hash()
    if h1 != h2: sys.exit('second build differs from the first')
    print('settle ok: two identical builds, deep checks passed. Review git diff, then commit.')

if __name__ == '__main__':
    main()
