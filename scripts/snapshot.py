#!/usr/bin/env python3
"""Pre-kickoff split snapshots (DraftKings + ScoresAndOdds).

Writes to OUT (default ./snapshots):
  dk_<UTC stamp>.json   parsed DraftKings spread splits (money = % handle, bets = % bets)
  dkml_/saoml_<UTC stamp>.json  same, moneyline market (TG Oct 25: rating = spread+ML money averaged)
  sao_<UTC stamp>.json  parsed ScoresAndOdds spread splits for the NFL week page
  espn_dk_<UTC stamp>.json  DraftKings moneyline + spread (line, price) from ESPN for every game
                        not yet started (the grading numbers recorded before kickoff)
  an_check_<UTC stamp>.json  Action Network book 15 (all-books) money % vs SAO; warnings only
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
      '?tb_eg=88808&tb_edate=n7days&tb_emt={mkt}&tb_page={p}')
SAO = 'https://www.scoresandodds.com/nfl/consensus-picks'

def _implied(o):
    """Break-even win share for an American price, e.g. -110 -> 0.5238."""
    o = float(str(o).replace('\u2212', '-').replace('+', ''))
    return -o / (100 - o) if o < 0 else 100 / (o + 100)


def get(url):
    if 'dknetwork' in url:   # the DK splits page is CDN-cached; bust it so every pull is fresh
        url += ('&' if '?' in url else '?') + '_cb=' + str(int(time.time() * 1000))
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9',
                                               'Cache-Control': 'no-cache', 'Pragma': 'no-cache'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.status, r.read().decode('utf-8', 'replace')

def txt(s):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', s)).strip()

def dk_parse(h, mkt='Spread'):
    games, blocks = [], h.split('<div class="tb-se ')[1:]
    for b in blocks:
        b = b.split('<div class="tb-se ')[0]
        t = re.search(r'<h5[^>]*>(.*?)</h5>\s*<span[^>]*>(.*?)</span>', b, re.S)
        if not t: continue
        g = {'matchup': txt(t.group(1)), 'kickoff_local': txt(t.group(2)), 'spread': []}
        mk = b.find('>' + mkt + '<')
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

def sao_parse(h, mkt='spread'):
    out = []
    for blk in h.split('<div class="trend-card consensus consensus-table-')[1:]:
        if not blk.startswith(mkt): continue
        tm = re.findall(r'<span class="team-flag" (\w+)""', blk)
        # bar width, not the label: SAO blanks the label (&nbsp;) on lopsided bars (e.g. TB@CAR ML money 7%)
        pa = re.findall(r'class="percentage-a" style="width:(\d+)%', blk); pb = re.findall(r'class="percentage-b" style="width:(\d+)%', blk)
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
    pre = sum(e['competitions'][0]['status']['type']['state'] == 'pre' for e in sb.get('events', []))
    return {'season': sb.get('season', {}).get('year'), 'week': sb.get('week', {}).get('number'),
            'events': len(sb.get('events', [])), 'pre': pre,
            'last': max((e['date'] for e in sb.get('events', [])), default=None)}, out

def espn_status(wkm, ed, now):
    """'ok', 'done' (all kicked off, latest kickoff < 36h ago) or an error string."""
    if ed: return 'ok'
    if wkm['events'] and not wkm['pre'] and wkm.get('last'):
        last = datetime.fromisoformat(wkm['last'].replace('Z', '+00:00'))
        if now - last < timedelta(hours=36): return 'done'
        return f"week {wkm['week']} looks wrong: 0 games left, latest kickoff {wkm['last']} is over 36h ago"
    return 'ESPN returned 0 pre-kickoff games'

AN = 'https://api.actionnetwork.com/web/v2/scoreboard/publicbetting/nfl?bookIds=15,30,68&date={}'
AN_FIX = {'WAS': 'WSH', 'JAC': 'JAX', 'LA': 'LAR'}

def an_check(sao, now):
    """Cross-check SAO money % vs Action Network book 15 (all-books). FLAG only: never blocks or rates."""
    days = sorted({(datetime.fromisoformat(g['kickoff_utc'].replace('Z', '+00:00')) - timedelta(hours=5)).strftime('%Y%m%d')
                   for g in sao if g.get('kickoff_utc')} or {now.strftime('%Y%m%d')})
    an = {}
    for d in days:
        for g in json.loads(get(AN.format(d))[1]).get('games', []):
            ab = {t['id']: AN_FIX.get(t['abbr'].upper(), t['abbr'].upper()) for t in g['teams']}
            sp = {o['side']: o['bet_info']['money']['percent'] for o in g.get('markets', {}).get('15', {}).get('event', {}).get('spread', [])
                  if (o.get('bet_info') or {}).get('money', {}).get('percent') is not None}
            if 'away' in sp and 'home' in sp:
                an[(ab[g['away_team_id']], ab[g['home_team_id']])] = sp
    rows = []
    for g in sao:
        k = (AN_FIX.get(g['away'].upper(), g['away'].upper()), AN_FIX.get(g['home'].upper(), g['home'].upper()))
        a = an.get(k); r = {'game': f'{k[0]}@{k[1]}', 'sao_money_away': g['money_away'], 'sao_money_home': g['money_home']}
        if not a: r['warning'] = 'AN book 15: game not found'
        else:
            r.update(an_money_away=a['away'], an_money_home=a['home'])
            diff = abs(a['away'] - g['money_away']); side = lambda x, y: 'away' if x > y else 'home' if y > x else 'even'
            if side(a['away'], a['home']) != side(g['money_away'], g['money_home']): r['warning'] = f'AN book 15 money side disagrees with SAO ({diff} pts)'
            elif diff > 5: r['warning'] = f'AN book 15 money differs from SAO by {diff} pts'
        rows.append(r)
    return rows

VSIN = 'https://data.vsin.com/betting-splits/?source={}&sport=NFL&view=today'

def vsin_capture(stamp):
    """Raw capture of VSiN free splits (DK + CIRCA, an independent Las Vegas book). Evidence only, no parse/rating yet:
    the free board lists only today's games, so the row format is verified on a game-day pull before any parser ships."""
    out = {}
    for b in ('CIRCA', 'DK'):
        try:
            st, h = get(VSIN.format(b))
            open(f'{OUT}/vsin_{b.lower()}_{stamp}.html', 'w').write(h)
            out[b] = {'http': st, 'bytes': len(h), 'no_data_notice': 'No splits data available' in h,
                      'nfl_team_mentions': len(re.findall(r'Chiefs|Seahawks|Bears|Eagles|Cowboys|Packers|Lions|Ravens', h))}
        except Exception as ex:
            out[b] = {'error': str(ex)[:200]}
    return out

def vsin_dk_parse(h, mkt='Spread'):
    """Backup only: VSiN's DraftKings splits table -> same rows as dk_parse (used when the DK page is empty/unavailable).
    side text 'VSiN <Nickname> <line>' (spread) / 'VSiN <Nickname>' (ML) so build's _dk_rows/_dkml_rows read it unchanged."""
    out = []
    for tb in re.findall(r'<tbody>(.*?)</tbody>', h, re.S):
        rows = re.findall(r'<tr class="sp-row">(.*?)</tr>', tb, re.S)
        if len(rows) != 2: continue
        sides = []
        for r in rows:
            nm = re.search(r'sp-team-link[^>]*>([^<]+)<', r)
            b = [txt(x) for x in re.findall(r'<span class="sp-badge[^"]*">(.*?)</span>\s*</td>', r, re.S)]
            if not nm or len(b) < 9: break
            nk = nm.group(1).split()[-1]; i = 0 if mkt == 'Spread' else 6
            pc = lambda x: int(re.match(r'(\d+)', x).group(1))
            sides.append({'side': f'VSiN {nk} {b[i]}' if mkt == 'Spread' else f'VSiN {nk}',
                          'odds': None if mkt == 'Spread' else b[i], 'handle_pct': pc(b[i+1]), 'bets_pct': pc(b[i+2])})
        if len(sides) == 2:
            out.append({'matchup': sides[0]['side'].split()[1] + ' @ ' + sides[1]['side'].split()[1],
                        'kickoff_local': None, 'source': 'vsin_dk_backup', 'spread': sides})
    return out

def main():
    os.makedirs(OUT, exist_ok=True)
    now = datetime.now(timezone.utc); stamp = now.strftime('%Y%m%dT%H%MZ')
    ok = True
    # DraftKings: walk pages until one adds nothing new
    dk, raw, seen = [], [], set()
    def dk_pages(mkt):
        rows, seen_ = [], set()
        for p in range(1, 7):
            st, h = get(DK.format(mkt=mkt, p=p))
            got = [g for g, b in dk_parse(h, mkt) if g['matchup'] + g['kickoff_local'] not in seen_]
            if not got: break
            for g in got: seen_.add(g['matchup'] + g['kickoff_local']); rows.append(g)
            time.sleep(2)
        return rows
    for p in range(1, 7):
        st, h = get(DK.format(mkt='Spread', p=p))
        got = [(g, b) for g, b in dk_parse(h) if g['matchup'] + g['kickoff_local'] not in seen]
        if not got: break
        for g, b in got:
            seen.add(g['matchup'] + g['kickoff_local']); dk.append(g); raw.append(b)
        time.sleep(2)
    meta = {'fetched_utc': now.isoformat(timespec='seconds'), 'source': DK.format(mkt='Spread', p='N')}
    vh = None
    if not dk:   # DK splits page empty/'temporarily unavailable' -> VSiN's DraftKings table (backup only)
        try:
            vh = get(VSIN.format('DK'))[1]; dk = vsin_dk_parse(vh)
            if dk: meta['source'] = VSIN.format('DK') + ' (backup: DK page empty)'
            print(f'DK page empty -> VSiN DK backup: {len(dk)} games')
        except Exception as ex: print('VSiN DK backup failed:', ex)
    for g in dk:  # book math from prices already pulled (no new scrape); fail-open
        try:
            sp = g['spread']; ip = [_implied(x['odds']) for x in sp]
            g['hold_pct'] = round(100 * (sum(ip) - 1) / sum(ip), 2)
            for i, x in enumerate(sp):
                # book wins on both outcomes while this side's money share sits in [lock_lo, breakeven]
                x['breakeven_money_pct'] = round(100 * ip[i], 1)
                x['lock_lo_money_pct'] = round(100 * (1 - ip[1 - i]), 1)
                x['book_exposed'] = x['handle_pct'] > 100 * ip[i]
        except Exception as e:
            g['hold_error'] = str(e)
    json.dump(dict(meta, games=dk), open(f'{OUT}/dk_{stamp}.json', 'w'), indent=1)
    print(f'DraftKings: {len(dk)} games with spread splits')
    if not dk: ok = False
    # TG, Oct 25: ratings use ALL money (spread + moneyline). DK moneyline splits -> dkml_<stamp>.json
    # (rows keep key 'spread' = the market rows, same shape as dk_; fail open: build falls back to spread-only + warns)
    try:
        dkml = dk_pages('Moneyline')
        if not dkml and vh: dkml = vsin_dk_parse(vh, 'Moneyline')
        json.dump({'fetched_utc': now.isoformat(timespec='seconds'), 'source': DK.format(mkt='Moneyline', p='N'), 'market': 'moneyline',
                   'games': dkml}, open(f'{OUT}/dkml_{stamp}.json', 'w'), indent=1)
        print(f'DraftKings: {len(dkml)} games with moneyline splits')
    except Exception as ex:
        print('DraftKings moneyline pull failed (fail open, spread-only):', ex)
    # ScoresAndOdds: current NFL week page
    st, h = get(SAO)
    wk = re.search(r'consensus-picks\?week=([\w-]+)', h)
    sao = sao_parse(h)
    json.dump({'fetched_utc': now.isoformat(timespec='seconds'), 'source': SAO, 'week': wk.group(1) if wk else None,
               'games': [g for g, _ in sao]}, open(f'{OUT}/sao_{stamp}.json', 'w'), indent=1)
    print(f'ScoresAndOdds: {len(sao)} games with spread splits (week {wk.group(1) if wk else "?"})')
    if not sao: ok = False
    saoml = sao_parse(h, 'moneyline')
    json.dump({'fetched_utc': now.isoformat(timespec='seconds'), 'source': SAO, 'market': 'moneyline', 'week': wk.group(1) if wk else None,
               'games': [g for g, _ in saoml]}, open(f'{OUT}/saoml_{stamp}.json', 'w'), indent=1)
    print(f'ScoresAndOdds: {len(saoml)} games with moneyline splits')
    # Action Network book 15 cross-check: FLAG only (SAO stays the all-books source); fails open
    try:
        rows = an_check([g for g, _ in sao], now)
        json.dump({'fetched_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'source': AN.format('YYYYMMDD'),
                   'rule': 'warn if AN book 15 money differs from SAO by >5 pts or picks the other side; never blocks or re-rates',
                   'warnings': [r for r in rows if 'warning' in r], 'games': rows}, open(f'{OUT}/an_check_{stamp}.json', 'w'), indent=1)
        print(f'Action Network cross-check: {len(rows)} games, {sum("warning" in r for r in rows)} warnings')
        for r in rows:
            if 'warning' in r: print('  WARN', r['game'], r['warning'])
    except Exception as ex:
        print('Action Network cross-check skipped (fail open):', ex)
    # Multi-source status: one file per pull listing what each source returned (fail open)
    src = {'fetched_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'),
           'draftkings_splits': len(dk), 'scoresandodds': len(sao)}
    try:
        src['vsin'] = vsin_capture(stamp)
        print('VSiN capture:', {k: v.get('bytes', v.get('error')) for k, v in src['vsin'].items()})
    except Exception as ex:
        src['vsin'] = {'error': str(ex)[:200]}
    src['note'] = ('independent money sources: DraftKings (own book), VSiN Circa (raw capture, '
                   'unparsed, not rated). SAO and AN share data.')
    try:
        json.dump(src, open(f'{OUT}/sources_{stamp}.json', 'w'), indent=1)
    except Exception as ex:
        print('sources json write failed (fail open):', ex)
    # ESPN DraftKings moneyline + spread for games not yet started
    try:
        cw = os.environ.get('TYGIF_WEEK') or (re.search(r'(\d+)$', wk.group(1)).group(1) if wk else None)
        if not cw: raise ValueError('card week unknown (no ScoresAndOdds week, TYGIF_WEEK unset)')
        wkm, ed = espn_dk(int(cw))
        json.dump(dict({'fetched_utc': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'source': f'{ESPN_SB}?week={cw}&seasontype=2'}, **wkm, games=ed),
                  open(f'{OUT}/espn_dk_{stamp}.json', 'w'), indent=1)
        print(f'ESPN DraftKings: {len(ed)} games not yet started (week {wkm["week"]})')
        if dk and dk[0].get('source') == 'vsin_dk_backup':   # VSiN has no spread prices -> same-pull ESPN DraftKings price
            NK = {'Cardinals':'ARI','Falcons':'ATL','Ravens':'BAL','Bills':'BUF','Panthers':'CAR','Bears':'CHI','Bengals':'CIN','Browns':'CLE','Cowboys':'DAL','Broncos':'DEN','Lions':'DET','Packers':'GB','Texans':'HOU','Colts':'IND','Jaguars':'JAX','Chiefs':'KC','Raiders':'LV','Chargers':'LAC','Rams':'LAR','Dolphins':'MIA','Vikings':'MIN','Patriots':'NE','Saints':'NO','Giants':'NYG','Jets':'NYJ','Eagles':'PHI','Steelers':'PIT','49ers':'SF','Seahawks':'SEA','Buccaneers':'TB','Titans':'TEN','Commanders':'WSH'}
            for g in dk:
                for e in ed:
                    for s_, k in zip(g['spread'], ('away', 'home')):
                        if NK.get(s_['side'].split()[1]) == e[k]: s_['odds'] = e['spread'][k]['odds']
            json.dump(dict(meta, games=dk), open(f'{OUT}/dk_{stamp}.json', 'w'), indent=1)
        es = espn_status(wkm, ed, datetime.now(timezone.utc))
        if es == 'done': print('Every game of the week has kicked off (latest kickoff < 36h ago); ESPN not failed.')
        elif es != 'ok': print('ESPN DraftKings:', es); ok = False
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
