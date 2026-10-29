"""DraftKings sportsbook per-game "% of bets placed" (bets % only, NO handle) -> dk_sb_bets_<stamp>.json.

Used by build/clean_build.py as the DraftKings-own agreement fallback when the DK Network splits board
(dknetwork.draftkings.com) is empty/"temporarily unavailable". TG, Oct 29 2026: no VSiN.

Source: https://sportsbook.draftkings.com/event/<slug>/<eventId>   e.g. car-panthers-%40-gb-packers/34118182
  Game lines -> expand chevron -> "% of bets placed" bars for Moneyline / Spread / Total.
  The percentages are rendered client-side; a plain HTTP GET (no browser) does not return them reliably,
  so this module is INGEST-ONLY for now.
  TODO(browser): automate the expand+read per event (subagent browser pass), write the file shape below.

File shape (one per pull; never invent a number - omit a game rather than guess):
  {"fetched_utc": ISO, "source": "...", "market": "bets_pct_only_no_handle",
   "games": [{"game":"CAR@GB","away":"CAR","home":"GB","spread_line_away":3.5,
              "spread_bets_away":36,"spread_bets_home":64,"ml_bets_away":26,"ml_bets_home":74,"slug":"..."}]}

CLI: python3 scripts/dk_sb_bets.py ingest <file.json> [week]
     -> validates and copies into build/raw/snap_w<week>_<YYYYMMDD_HHMM CT>/dk_sb_bets_<stamp>.json
"""
import json, os, sys
from datetime import datetime
from zoneinfo import ZoneInfo
RAW = os.environ.get('TYGIF_WORK', os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'build', 'raw'))
NEED = ('away', 'home', 'spread_bets_away', 'spread_bets_home')

def validate(d):
    ok = []
    for g in d.get('games', []):
        if not all(isinstance(g.get(k), (int, float)) or k in ('away', 'home') and g.get(k) for k in NEED): continue
        if not 95 <= g['spread_bets_away'] + g['spread_bets_home'] <= 105: continue
        ok.append(g)
    return ok

def ingest(path, week):
    d = json.load(open(path)); games = validate(d)
    if not games: sys.exit('no valid games in ' + path)
    t = datetime.fromisoformat(d['fetched_utc'].replace('Z', '+00:00'))
    ct = t.astimezone(ZoneInfo('America/Chicago')); stamp = t.astimezone(ZoneInfo('UTC')).strftime('%Y%m%dT%H%MZ')
    out = os.path.join(RAW, f'snap_w{week}_{ct:%Y%m%d_%H%M}'); os.makedirs(out, exist_ok=True)
    d = dict(d, games=games, market='bets_pct_only_no_handle',
             note='DraftKings sportsbook per-game % of bets placed (bets only, no handle); DK-own agreement fallback when DK Network board is down')
    p = os.path.join(out, f'dk_sb_bets_{stamp}.json'); json.dump(d, open(p, 'w'), indent=1)
    print(f'{len(games)} games -> {p}'); return p

if __name__ == '__main__':
    if len(sys.argv) >= 3 and sys.argv[1] == 'ingest': ingest(sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else os.environ.get('TYGIF_WEEK', '8'))
    else: print(__doc__)
