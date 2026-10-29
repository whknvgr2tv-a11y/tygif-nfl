"""Phase 1 multi-book helpers (evidence only; NOT wired into STRONG/LEAN).
- book_math: shared hold / break-even math from a two-way American price pair.
- circa_from_html: VSiN Circa splits -> games shaped like dk_*.json (source 'vsin_circa').
- books_panel: per game, which books we have (spread% / ML% / all-money% / hold%) and which are missing.
CLI: python3 scripts/books.py <snap_dir> [stamp]   (re-runs Circa parse + panel offline on a saved snap)."""
import glob, json, os, re, sys

NK = {'Cardinals':'ARI','Falcons':'ATL','Ravens':'BAL','Bills':'BUF','Panthers':'CAR','Bears':'CHI','Bengals':'CIN','Browns':'CLE',
      'Cowboys':'DAL','Broncos':'DEN','Lions':'DET','Packers':'GB','Texans':'HOU','Colts':'IND','Jaguars':'JAX','Chiefs':'KC',
      'Raiders':'LV','Chargers':'LAC','Rams':'LAR','Dolphins':'MIA','Vikings':'MIN','Patriots':'NE','Saints':'NO','Giants':'NYG',
      'Jets':'NYJ','Eagles':'PHI','Steelers':'PIT','49ers':'SF','Seahawks':'SEA','Buccaneers':'TB','Titans':'TEN','Commanders':'WSH'}

def implied(o):
    """Break-even win share for one American price (vig included): -110 -> 110/210 = .5238, +150 -> 100/250 = .40."""
    o = float(str(o).replace('\u2212', '-').replace('+', ''))
    return -o / (100 - o) if o < 0 else 100 / (o + 100)

def book_math(a, b):
    """Two-way prices -> hold + break-evens, or None if a price is missing.
    hold_pct = (p_a + p_b - 1) / (p_a + p_b) * 100   (book's theoretical margin; -110/-110 -> 4.55)
    breakeven_pct = implied(price) * 100              (win rate a bettor needs on that side; -110 -> 52.38)
    no_vig_pct = implied / (p_a + p_b) * 100          (fair share with the vig removed)."""
    try:
        pa, pb = implied(a), implied(b)
    except (TypeError, ValueError):
        return None
    s = pa + pb
    return {'hold_pct': round(100 * (s - 1) / s, 2), 'breakeven_pct': [round(100 * pa, 2), round(100 * pb, 2)],
            'no_vig_pct': [round(100 * pa / s, 2), round(100 * pb / s, 2)]}

def circa_from_html(h):
    """Circa table has the same layout as VSiN's DK table, so reuse vsin_dk_parse; join spread + ML per game."""
    from snapshot import vsin_dk_parse
    sp, ml = vsin_dk_parse(h), {g['matchup']: g for g in vsin_dk_parse(h, 'Moneyline')}
    out = []
    for g in sp:
        a, b = g['spread']; m = ml.get(g['matchup'])
        nk = [x['side'].split()[1] for x in (a, b)]
        r = {'matchup': g['matchup'], 'away': NK.get(nk[0]), 'home': NK.get(nk[1]), 'kickoff_local': None, 'source': 'vsin_circa',
             'spread': [dict(x, side=x['side'].replace('VSiN ', 'Circa ', 1)) for x in (a, b)]}
        if m:
            r['moneyline'] = [dict(x, side=x['side'].replace('VSiN ', 'Circa ', 1)) for x in m['spread']]
            r['money_all'] = [round((a['handle_pct'] + r['moneyline'][0]['handle_pct']) / 2, 1),
                              round((b['handle_pct'] + r['moneyline'][1]['handle_pct']) / 2, 1)]
            bm = book_math(*[x['odds'] for x in r['moneyline']])
            if bm: r['ml_hold_pct'] = bm['hold_pct']; r['ml_breakeven_pct'] = bm['breakeven_pct']
        bm = book_math(a['odds'], b['odds'])   # VSiN shows no spread juice today -> usually absent
        if bm: r['hold_pct'] = bm['hold_pct']; r['breakeven_pct'] = bm['breakeven_pct']
        out.append(r)
    return out

def write_circa(d, stamp):
    p = f'{d}/vsin_circa_{stamp}.html'
    if not os.path.exists(p): return None
    games = circa_from_html(open(p).read())
    json.dump({'source': 'vsin_circa', 'html': os.path.basename(p), 'games': games}, open(f'{d}/vsin_circa_{stamp}.json', 'w'), indent=1)
    return games

def _load(d, pre, stamp):
    try: return json.load(open(f'{d}/{pre}_{stamp}.json'))
    except Exception: return None

def _ab(side):   # 'VSiN Panthers +3.5' / 'DK ...' -> abbr from nickname, else first all-caps token
    for t in side.split():
        if t in NK: return NK[t]
        if t in NK.values(): return t
    return None

def books_panel(d, stamp):
    """Per SAO game: books present with spread/ML/all-money % (away, home) + hold. Missing books listed explicitly."""
    sao, saoml = _load(d, 'sao', stamp), _load(d, 'saoml', stamp)
    dk, dkml = _load(d, 'dk', stamp), _load(d, 'dkml', stamp)
    espn, circa = _load(d, 'espn_dk', stamp), _load(d, 'vsin_circa', stamp)
    games = {(g['away'], g['home']): {'away': g['away'], 'home': g['home'], 'kickoff_utc': g.get('kickoff_utc'), 'books': {}}
             for g in (sao or {}).get('games', [])}
    def put(k, book, v):
        if k in games: games[k]['books'][book] = v
    for g in (sao or {}).get('games', []):
        m = next((x for x in (saoml or {}).get('games', []) if (x['away'], x['home']) == (g['away'], g['home'])), None)
        v = {'spread_money': [g['money_away'], g['money_home']], 'spread_bets': [g['bets_away'], g['bets_home']]}
        if m: v.update(ml_money=[m['money_away'], m['money_home']],
                       all_money=[round((g['money_away'] + m['money_away']) / 2, 1), round((g['money_home'] + m['money_home']) / 2, 1)])
        put((g['away'], g['home']), 'sao_all_books', v)
    dkm = {tuple(_ab(x['side']) for x in g['spread']): g for g in (dkml or {}).get('games', [])}
    for g in (dk or {}).get('games', []):
        k = tuple(_ab(x['side']) for x in g['spread']); m = dkm.get(k)
        v = {'source': g.get('source', 'dk'), 'spread_money': [x['handle_pct'] for x in g['spread']], 'spread_bets': [x['bets_pct'] for x in g['spread']]}
        if m: v['ml_money'] = [x['handle_pct'] for x in m['spread']]; v['all_money'] = [round((p + q) / 2, 1) for p, q in zip(v['spread_money'], v['ml_money'])]
        bm = book_math(*[x.get('odds') for x in g['spread']])
        if bm: v['hold_pct'] = bm['hold_pct']; v['breakeven_pct'] = bm['breakeven_pct']
        if m and (bm := book_math(*[x.get('odds') for x in m['spread']])): v['ml_hold_pct'] = bm['hold_pct']
        put(k, 'draftkings', v)
    for g in (circa or {}).get('games', []):
        v = {k: g[k] for k in ('hold_pct', 'breakeven_pct', 'ml_hold_pct', 'ml_breakeven_pct') if k in g}
        v['spread_money'] = [x['handle_pct'] for x in g['spread']]; v['spread_bets'] = [x['bets_pct'] for x in g['spread']]
        if 'moneyline' in g: v['ml_money'] = [x['handle_pct'] for x in g['moneyline']]; v['all_money'] = g['money_all']
        put((g['away'], g['home']), 'circa', v)
    for g in (espn or {}).get('games', []):
        sp, ml = book_math(g['spread']['away']['odds'], g['spread']['home']['odds']), book_math(g['ml']['away'], g['ml']['home'])
        v = {'prices_only': True, 'spread_line': [g['spread']['away']['line'], g['spread']['home']['line']]}
        if sp: v['hold_pct'] = sp['hold_pct']; v['breakeven_pct'] = sp['breakeven_pct']
        if ml: v['ml_hold_pct'] = ml['hold_pct']; v['ml_breakeven_pct'] = ml['breakeven_pct']
        put((g['away'], g['home']), 'espn_dk_prices', v)
    allb = ('sao_all_books', 'draftkings', 'circa', 'espn_dk_prices')
    for g in games.values(): g['missing'] = [b for b in allb if b not in g['books']]
    out = {'stamp': stamp, 'note': 'evidence only; ratings still SAO all-money + DK agreement. Pairs are [away, home].',
           'coverage': {b: sum(b in g['books'] for g in games.values()) for b in allb}, 'games': list(games.values())}
    json.dump(out, open(f'{d}/books_panel_{stamp}.json', 'w'), indent=1)
    return out

def run(d, stamp):
    c = write_circa(d, stamp)
    p = books_panel(d, stamp)
    print(f'Circa: {len(c) if c is not None else "no html"} games parsed; books panel coverage {p["coverage"]} of {len(p["games"])}')
    return p

if __name__ == '__main__':
    d = sys.argv[1]
    st = sys.argv[2] if len(sys.argv) > 2 else sorted(re.search(r'sao_(.+)\.json', f).group(1) for f in glob.glob(f'{d}/sao_*.json'))[-1]
    run(d, st)
