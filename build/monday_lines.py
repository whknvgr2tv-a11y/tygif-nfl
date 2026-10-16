#!/usr/bin/env python3
"""Monday line per game: TeamRankings spread history, books 2 and 3, each book's last quote posted before
Monday 12:00 AM ET of game week (= Sunday 11:00 PM CT, the Sunday-night reopen). The 'Open' row is never used
(it can be a summer look-ahead). A quote older than 7 days is stale and not used. Monday line = average of the two.

  python3 build/monday_lines.py --week 7                 # fetch; writes build/inputs/tr_monday_w7.json
  python3 build/monday_lines.py --week 6 --html DIR      # re-parse saved spread-movement pages (no network)
Raw pages are saved to build/raw/tr_w<N>/<slug>.html. Refuses to run before the cutoff has passed.
"""
import re, sys, json, os, datetime as dt, urllib.request, argparse
from zoneinfo import ZoneInfo
B = os.path.dirname(os.path.abspath(__file__)); RAW = os.environ.get('TYGIF_WORK', B + '/raw')
ET = ZoneInfo('America/New_York')
TRAB = {'JAC': 'JAX', 'WAS': 'WSH', 'LA': 'LAR'}
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
SB = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard?seasontype=2&week={w}&dates={y}'

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=40) as r:
        return r.read().decode('utf-8', 'replace')
def text(h):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S); t = re.sub(r'<[^>]+>', ' | ', t)
    return re.sub(r'(\s*\|\s*)+', ' | ', t)
def num(v):
    v = v.strip(); return None if v in ('--', '') else (0.0 if v.upper() in ('PK', 'EVEN') else float(v))

def parse(h, mon):
    """mon = naive Monday 00:00 ET (TeamRankings times are ET)"""
    t = text(h)
    tm, other = [TRAB.get(x, x) for x in re.search(r'\| (\w+) Spread \| (\w+) Spread \|', t).groups()]
    seg = t[t.find('Spread History'):]
    quotes = []
    for mo, dy, hh, mm, ap, b1, b2, b3 in re.findall(r'(\d\d)/(\d\d) (\d\d):(\d\d) ([AP]M) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|', seg):
        hh = int(hh) % 12 + (12 if ap == 'PM' else 0)
        yr = mon.year - (1 if int(mo) == 12 and mon.month == 1 else 0)
        quotes.append((dt.datetime(yr, int(mo), int(dy), hh, int(mm)), [num(b1), num(b2), num(b3)]))
    pick = {}
    for b in (1, 2):   # books 2 and 3
        prior = sorted((ts, v[b]) for ts, v in quotes if ts < mon and v[b] is not None)
        if prior and prior[-1][0] >= mon - dt.timedelta(days=7): pick[b + 1] = prior[-1]
    vals = [v for _, v in pick.values()]
    return {'team': tm, 'other': other, 'books': {k: {'line': v, 'at': ts.strftime('%m/%d %I:%M %p')} for k, (ts, v) in pick.items()},
            'avg': (sum(vals) / len(vals)) if vals else None}

def week_monday(week):
    """Monday 00:00 ET before the week's first kickoff, from the ESPN scoreboard"""
    p = f'{RAW}/espn_sum/sb_w{week}.json'
    sb = json.load(open(p)) if os.path.exists(p) else json.loads(get(SB.format(w=week, y=dt.date.today().year)))
    first = min(dt.datetime.fromisoformat(e['date'].replace('Z', '+00:00')) for e in sb['events']).astimezone(ET)
    d = first.date() - dt.timedelta(days=(first.weekday() - 0) % 7)   # back to Monday
    return dt.datetime(d.year, d.month, d.day), len(sb['events'])

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--week', type=int, required=True); ap.add_argument('--html'); ap.add_argument('--out')
    a = ap.parse_args()
    mon, n = week_monday(a.week)
    if not a.html and dt.datetime.now(ET).replace(tzinfo=None) < mon:
        sys.exit(f'too early: the Monday line cutoff is {mon:%a %b %d} 12:00 AM ET (Sun 11:00 PM CT)')
    out = {}
    if a.html:
        for f in sorted(os.listdir(a.html)):
            if f.endswith('.html'): out[f[:-5]] = parse(open(os.path.join(a.html, f)).read(), mon)
    else:
        rd = f'{RAW}/tr_w{a.week}'; os.makedirs(rd, exist_ok=True)
        idx = get('https://www.teamrankings.com/nfl/odds/')
        slugs = sorted(set(re.findall(rf'/nfl/matchup/([a-z0-9-]+-week-{a.week}-{mon.year})"', idx)))
        for s in slugs:
            h = get(f'https://www.teamrankings.com/nfl/matchup/{s}/spread-movement'); open(f'{rd}/{s}.html', 'w').write(h)
            out[s] = parse(h, mon)
    miss = [k for k, v in out.items() if v['avg'] is None]
    if len(out) != n: sys.exit(f'TeamRankings has {len(out)} week {a.week} games, ESPN has {n}: not written')
    if miss: sys.exit(f'no book 2/3 quote in the 7 days before the cutoff: {miss}: not written')
    p = a.out or f'{B}/inputs/tr_monday_w{a.week}.json'
    json.dump(out, open(p, 'w'), indent=1); print(f'wrote {p}: {len(out)} games, cutoff {mon:%a %b %d} 12:00 AM ET')

if __name__ == '__main__':
    main()
