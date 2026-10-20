#!/usr/bin/env python3
"""Pre-kickoff split snapshots (DraftKings + ScoresAndOdds).

Writes to OUT (default ./snapshots):
  dk_<UTC stamp>.json   parsed DraftKings spread splits (money = % handle, bets = % bets)
  sao_<UTC stamp>.json  parsed ScoresAndOdds spread splits for the NFL week page
  espn_dk_<UTC stamp>.json  DraftKings moneyline + spread (line, price) from ESPN for every game
                        not yet started (the grading numbers recorded before kickoff)
Snapshots are kept (they are the grading record). Exits 1 if any source
returns no games (bot block or layout change), so the run shows as failed.
"""
import json, os, re, sys, time, urllib.request
from datetime import datetime, timezone, timedelta

OUT = sys.argv[1] if len(sys.argv) > 1 else 'snapshots'
KEEP_DAYS = None   # never prune: pre-kickoff pulls are the grading record
ESPN_SB = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard'
ESPN_SUM = 'https://site.api.espn.com/apis/site/v2/sports/football/nfl/summary?event={}'
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
DK = ('https://dknetwork.draftkings.com/draftkings-sportsbook-betting-splits/'
      '?tb_eg=88808&tb_edate=n7days&tb_emt=Spread&tb_page={}')
SAO = 'https://www.scoresandodds.com/nfl/consensus-picks'

def get(url):
    if 'dknetwork' in url:   # the DK splits page is CDN-cached; bust it so every pull is fresh
        url += ('&' if '?' in url else '?') + '_cb=' + str(int(time.time() * 1000))
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9',
                                               'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.status, r.read().decode('utf-8', 'replace')

def txt(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()

def dk_parse(h):
    games, blocks = [], h.split('<div class="tb-se ')[1:]
    for b in blocks:
        b = b.split('<div class="tb-se ')[0]
        t = re.search(r'<h5[^>]*>(.*?)</h5>\s*<span[^>]*>(.*?)</span>', b, re.S)
        if not t: continue
        g = {'matchup': txt(t.group(1)), 'kickoff_local': txt(t.group(2)), 'spread': []}
        mk = b.find('>Spread<')
        if mk < 0: continue
        seg = b[mk:]; nxt = re.search(r'tb-se-head', seg[20:])
        if nxt: seg = seg[:nxt.start() + 20]
        for row in seg.split('tb-sodd')[1:]:
            side = re.search(r'tb-slipline[^>]*>([^<]+)<', row)
            odds = re.search(r'tb-odd-s[^>]*>\s*([^<\s]+)', row)
            pct = re.findall(r'<div class="flex-1">\s*(\d+)%', row)
            if side and len(pct) >= 2:
                g['spread'].append({'side': side.group(1).strip(), 'odds': odds.group(1) if odds else None,
                                    'handle_pct': int(pct[0]), 'bets_pct': int(pct[1])})
        if g['spread']: games.append((g, b))
    return games

def sao_parse(h):
    out = []
    for blk in h.split('<div class="trend-card consensus consensus-table-')[1:]:
        if not blk.startswith('spread'): continue
        tm = re.findall(r'<span class="team-flag" (\w+)""', blk)
        pa = re.findall(r'class="percentage-a"[^>]*>(\d+)%', blk); pb = re.findall(r'class="percentage-b"[^>]*>(\d+)%', blk)
        t = re.search(r'data-value="([^"]+)"', blk)
        if len(tm) >= 2 and len(pa) >= 2 and len(pb) >= 2:
            out.append(({'away': tm[0], 'home': tm[1], 'kickoff_utc': t.group(1) if t else None,
                         'bets_away': int(pa[0]), 'bets_home': int(pb[0]),
                         'money_away': int(pa[1]), 'money_home': int(pb[1])}, blk[:6000]))
    return out

def espn_dk_game(e, s):
    """one scheduled ESPN scoreboard event + its game summary -> DraftKings ML and spread (current = pre-kickoff numbers)"""
    c = e['competitions'][0]
    t = {x['homeAway']: x['team']['abbreviation'] for x in c['competitors']}
    pc = [p for p in s.get('pickcenter', []) if 'DraftKings' in p['provider']['name']]
    if not pc: return None
    pc = pc[0]; ml = pc.get('moneyline') or {}; ps = pc.get('pointSpread') or {}
    cur = lambda d, k: ((d.get(k) or {}).get('close') or {})   # ESPN 'close' = current number while the game is still scheduled
    return {'id': e['id'], 'away': t['away'], 'home': t['home'], 'kickoff_utc': e['date'],
            'ml': {'away': cur(ml, 'away').get('odds'), 'home': cur(ml, 'home').get('odds')},
            'spread': {k: {'line': cur(ps, k).get('line'), 'odds': cur(ps, k).get('odds')} for k in ('away', 'home')}}

def espn_dk(week):
    """DraftKings ML + spread from ESPN for games still scheduled (pre-kickoff numbers only), for the card week explicitly
    (ESPN's default scoreboard can still be on the previous week)."""
    st, h = get(f'{ESPN_SB}?week={week}&seasontype=2'); sb = json.loads(h); out = []
    for e in sb.get('events', []):
        if e['competitions'][0]['status']['type']['state'] != 'pre': continue
        st, h = get(ESPN_SUM.format(e['id'])); g = espn_dk_game(e, json.loads(h))
        if g: out.append(g)
        time.sleep(0.5)
    return {'season': sb.get('season', {}).get('year'), 'week': sb.get('week', {}).get('number')}, out

def main():
    os.makedirs(OUT, exist_ok=True)
    now = datetime.now(timezone.utc); stamp = now.strftime('%Y%m%dT%H%MZ')
    ok = True
    # DraftKings: walk pages until one adds nothing new
    dk, raw, seen = [], [], set()
    for p in range(1, 7):
        st, h = get(DK.format(p))
        got = [(g, b) for g, b in dk_parse(h) if g['matchup'] + g['kickoff_local'] not in seen]
        if not got: break
        for g, b in got:
            seen.add(g['matchup'] + g['kickoff_local']); dk.append(g); raw.append(b)
        time.sleep(2)
    meta = {'fetched_utc': now.isoformat(timespec='seconds'), 'source': DK.format('N')}
    json.dump(dict(meta, games=dk), open(f'{OUT}/dk_{stamp}.json', 'w'), indent=1)
    print(f'DraftKings: {len(dk)} games with spread splits')
    if not dk: ok = False
    # ScoresAndOdds: current NFL week page
    st, h = get(SAO)
    wk = re.search(r'consensus-picks\?week=([\w-]+)', h)
    sao = sao_parse(h)
    json.dump({'fetched_utc': now.isoformat(timespec='seconds'), 'source': SAO, 'week': wk.group(1) if wk else None,
               'games': [g for g, _ in sao]}, open(f'{OUT}/sao_{stamp}.json', 'w'), indent=1)
    print(f'ScoresAndOdds: {len(sao)} games with spread splits (week {wk.group(1) if wk else "?"})')
    if not sao: ok = False
    # ESPN DraftKings moneyline + spread for games not yet started
    try:
        cw = os.environ.get('TYGIF_WEEK') or (re.search(r'(\d+)$', wk.group(1)).group(1) if wk else None)
        if not cw: raise ValueError('card week unknown (no ScoresAndOdds week, TYGIF_WEEK unset)')
        wkm, ed = espn_dk(int(cw))
        json.dump(dict({'fetched_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'source': f'{ESPN_SB}?week={cw}&seasontype=2'}, **wkm, games=ed),
                  open(f'{OUT}/espn_dk_{stamp}.json', 'w'), indent=1)
        print(f'ESPN DraftKings: {len(ed)} games not yet started (week {wkm["week"]})')
        if not ed: ok = False
    except Exception as ex:
        print('ESPN DraftKings capture failed:', ex); ok = False
    # prune (disabled when KEEP_DAYS is None)
    cut = now - timedelta(days=KEEP_DAYS) if KEEP_DAYS else None
    for fn in (os.listdir(OUT) if cut else []):
        m = re.search(r'_(\d{8}T\d{4})Z', fn)
        if m and datetime.strptime(m.group(1), '%Y%m%dT%H%M').replace(tzinfo=timezone.utc) < cut:
            os.remove(os.path.join(OUT, fn))
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
