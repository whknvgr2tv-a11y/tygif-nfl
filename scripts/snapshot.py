#!/usr/bin/env python3
"""Pre-kickoff split snapshots (DraftKings + ScoresAndOdds).

Writes to OUT (default ./snapshots):
  dk_<UTC stamp>.json   parsed DraftKings spread splits (money = % handle, bets = % bets)
  sao_<UTC stamp>.json  parsed ScoresAndOdds spread splits for the NFL week page
Prunes snapshot files older than KEEP_DAYS (21). Exits 1 if either source
returns no games (bot block or layout change), so the run shows as failed.
"""
import json, os, re, sys, time, urllib.request
from datetime import datetime, timezone, timedelta

OUT = sys.argv[1] if len(sys.argv) > 1 else 'snapshots'
KEEP_DAYS = 21
UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
DK = ('https://dknetwork.draftkings.com/draftkings-sportsbook-betting-splits/'
      '?tb_eg=88808&tb_edate=n7days&tb_emt=Spread&tb_page={}')
SAO = 'https://www.scoresandodds.com/nfl/consensus-picks'

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
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
    # prune
    cut = now - timedelta(days=KEEP_DAYS)
    for fn in os.listdir(OUT):
        m = re.search(r'_(\d{8}T\d{4})Z', fn)
        if m and datetime.strptime(m.group(1), '%Y%m%dT%H%M').replace(tzinfo=timezone.utc) < cut:
            os.remove(os.path.join(OUT, fn))
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
