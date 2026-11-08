"""Settled closes whose raw snapshot is not in the archive.

live_log, pregame_lines, sides_log and ml_log are the grading record when the
snapshot files they cite are absent from origin/snapshots and the local raw
archive. The documented line, price, moneyline, rating, type and combined
money percentages are kept. The spread-versus-moneyline pieces that were
averaged into those combined percentages are not in the logs, so they stay
unknown. This module does not write a snapshot and does not invent those pieces.
"""
import csv, glob, json, os, re, subprocess
from decimal import Decimal, ROUND_HALF_UP

_CITE = re.compile(r'(?:espn_dk|saoml|dkml|sao|dk)_\d{8}T\d{4}Z\.json')
_PCT = re.compile(r'^([A-Z]{2,3}) (\d+)\b')
_PROV = re.compile(r'(scripts/snapshot\.py pull|snapshots branch) ((?:espn_dk|saoml|dkml|sao|dk)_\d{8}T\d{4}Z\.json)')

def _r0(x):
    return int(Decimal(str(x)).quantize(Decimal('1'), ROUND_HALF_UP))

def _pay(price, res):
    if res == 'L': return -100.0
    if res == 'P': return 0.0
    if res == 'W': return float(_r0(price if price > 0 else 10000 / abs(price)))
    return None

def _num(s):
    return float(str(s).replace('\u2212', '-').replace('+', ''))

def _origin_names(root):
    p = subprocess.run(['git', '-C', root, 'ls-tree', '--name-only', '-r', 'origin/snapshots', 'snapshots/'],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(p.stderr.strip() or 'origin/snapshots is not available')
    return set(p.stdout.split())

def present(fn, origin, work, root):
    """True when the builder can read this snapshot (branch, local snap, or data/espn_dk)."""
    if f'snapshots/{fn}' in origin: return True
    if glob.glob(os.path.join(work, 'snap_w*', fn)): return True
    if os.path.exists(os.path.join(root, 'data', 'espn_dk', fn)): return True
    return False

def breakeven(away, home, price_away, price_home):
    """DK break-even from the documented closing prices (same book_math the pulls use). None if a price is missing."""
    import sys
    scripts = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts')
    if scripts not in sys.path: sys.path.insert(0, scripts)
    from books import book_math
    bm = book_math(price_away, price_home)
    if not bm: return None
    return {away: bm['breakeven_pct'][0], home: bm['breakeven_pct'][1]}

def _prov(text, kind):
    for how, fn in _PROV.findall(text):
        if fn.startswith(kind + '_'): return f'{how} {fn}'
    return None

def missing_closes(root, work=None):
    """{(week, game): documented close} for settled games whose cited raw close is absent.

    A game is included only when live_log, pregame_lines, sides_log and ml_log
    agree. Disagreement raises: the build must not fall back to an earlier pull
    and must not guess which record wins.
    """
    root = os.path.abspath(root)
    work = work or os.environ.get('TYGIF_WORK') or os.path.join(root, 'build', 'raw')
    origin = _origin_names(root)
    live = list(csv.DictReader(open(os.path.join(root, 'data', 'live_log.csv'))))
    pre = {}
    for row in json.load(open(os.path.join(root, 'data', 'pregame_lines.json')))['lines']:
        pre[(row['week'], row['game'], row['side'])] = row
    sides = {}
    for row in json.load(open(os.path.join(root, 'data', 'sides_log.json')))['rows']:
        sides.setdefault((row['week'], row['game']), {})[row['role']] = row
    ml = {(r['week'], r['game']): r for r in json.load(open(os.path.join(root, 'data', 'ml_log.json')))['plays']}
    out = {}
    for r in live:
        if not (r.get('result') or '').strip(): continue
        text = r['close_split_source'] + ' ' + r['card_source']
        cited = sorted(set(_CITE.findall(text)))
        if not cited: continue
        absent = [fn for fn in cited if not present(fn, origin, work, root)]
        if not absent: continue
        w, game = int(r['week']), r['game'].replace('LA@', 'LAR@')
        A, H = game.split('@')
        our = r['our_side']
        rating, ty = r['rating'], int(r['type'])
        line, price = _num(r['closing_line']), int(_num(r['closing_price']))
        money, bets, dk = _PCT.match(r['close_all_money'].strip()), _PCT.match(r['close_all_bets'].strip()), _PCT.match(r['close_dk_money'].strip())
        rows = {side: pre.get((w, game, side)) for side in (A, H)}
        sd, play = sides.get((w, game), {}), ml.get((w, game))
        err = []
        if not money or not bets or not dk: err.append('combined money/bets/DK not a documented side and percent')
        if any(rows[s] is None or 'line' not in rows[s] or 'price' not in rows[s] or 'ml' not in rows[s] for s in (A, H)):
            err.append('pregame_lines missing a side, line, price or moneyline')
        if set(sd) != {'fade', 'money'}: err.append('sides_log missing fade or money')
        if play is None: err.append('ml_log missing')
        if err: raise SystemExit(f'W{w} {game}: raw close {absent} is missing and the saved records cannot be kept ({"; ".join(err)})')
        prow, frow, mrow = rows[our], sd['fade'], sd['money']
        if (prow['line'], int(prow['price'])) != (line, price): err.append('pregame line/price != live_log close')
        if rows[A]['at_utc'] != rows[H]['at_utc'] or rows[A]['source'] != rows[H]['source']: err.append('pregame sides disagree on time or source')
        if rows[A]['ml_at_utc'] != rows[H]['ml_at_utc'] or rows[A]['ml_source'] != rows[H]['ml_source']: err.append('pregame moneylines disagree on time or source')
        if frow['team'] != our or frow['rating'] != rating or int(frow['type']) != ty or float(frow['spread_line']) != line:
            err.append('sides fade != live_log')
        if mrow['rating'] != rating or int(mrow['type']) != ty: err.append('sides money rating != live_log')
        if money.group(1) != mrow['team'] or int(mrow['money_pct']) != int(money.group(2)):
            err.append('sides money % != live_log all-books money')
        if bets.group(1) != money.group(1): err.append('all-books bets side != all-books money side')
        if int(frow['money_pct']) + int(mrow['money_pct']) != 100: err.append('sides money percentages do not add to 100')
        if play['side'] != our or play['rating'] != rating or float(play['spread_line']) != line or int(play['price']) != int(rows[our]['ml']):
            err.append('ml_log != live_log / pregame moneyline')
        dk_src, sao_src = rows[our]['source'], _prov(r['close_split_source'], 'sao')
        if not sao_src or not dk_src: err.append('provenance string missing')
        if os.path.basename(dk_src) not in text or os.path.basename(rows[our]['ml_source']) not in text or os.path.basename(sao_src) not in text:
            err.append('pregame provenance is not the live_log provenance')
        for side, row in (('fade', frow), ('money', mrow)):
            team = row['team']
            for kind, px, res, usd in (('spread', rows[team]['price'], row['sp_res'], row['sp_usd']),
                                       ('moneyline', rows[team]['ml'], row['ml_res'], row['ml_usd'])):
                got = _pay(px, res)
                if got is None or usd is None or float(usd) != got: err.append(f'{team} {kind} result does not match the documented price')
        if err: raise SystemExit(f'W{w} {game}: raw close {absent} is missing and the saved records disagree ({"; ".join(err)})')
        out[(w, game)] = dict(
            week=w, game=game, A=A, H=H, rating=rating, type=ty, our_side=our,
            ab_side=money.group(1), ab_m=int(money.group(2)), ab_b=int(bets.group(2)),
            dk_side=dk.group(1), dk_m=int(dk.group(2)), dk_b=None, components=None,
            at_utc=rows[our]['at_utc'], ml_at_utc=rows[our]['ml_at_utc'],
            source=dk_src, ml_source=rows[our]['ml_source'], split_src=sao_src, dk_src=dk_src,
            line={s: rows[s]['line'] for s in (A, H)}, price={s: int(rows[s]['price']) for s in (A, H)},
            ml={s: int(rows[s]['ml']) for s in (A, H)},
            rows={s: dict(rows[s]) for s in (A, H)}, cited=cited, absent=absent)
    return out
