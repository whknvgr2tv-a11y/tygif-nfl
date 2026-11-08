"""Regression: a missing raw close keeps the documented settled grade, and a fresh pull still grades from the file.

Does not disable a check, change a threshold, or leave a snapshot behind.
"""
import glob, json, os, shutil, subprocess, sys, tempfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'build'))
os.chdir(ROOT)
import settled_close as sc
import pregame

WORK = os.path.join(ROOT, 'build', 'raw')
M = '\u2212'

def fail(msg):
    print('FAIL', msg); sys.exit(1)

def rate_fns():
    src = open(os.path.join(ROOT, 'build', 'clean_build.py')).read()
    ns = {'M': M}
    exec(src[src.index('def rate_unified'):src.index('def _rate_ml')], ns)
    return ns['rate_v1'], ns['rate_unified']

def line_of(lines, week, game, side):
    return next(p for p in lines if (p['week'], p['game'], p['side']) == (week, game, side))

def main():
    held = sc.missing_closes(ROOT, WORK)
    if set(held) != {(8, 'CHI@SEA'), (9, 'JAX@BAL')}: fail(f'missing closes {sorted(held)}')
    jax, chi = held[(9, 'JAX@BAL')], held[(8, 'CHI@SEA')]
    if (jax['rating'], jax['type'], jax['our_side'], jax['line']['BAL'], jax['price']['BAL'], jax['ml']['BAL']) != ('LEAN', 3, 'BAL', 8.5, 102, 350):
        fail(f'JAX documented close {jax["rating"]} {jax["our_side"]} {jax["line"]} {jax["price"]} {jax["ml"]}')
    if (jax['ab_side'], jax['ab_m'], jax['ab_b'], jax['dk_side'], jax['dk_m'], jax['components'], jax['dk_b']) != ('JAX', 61, 78, 'JAX', 74, None, None):
        fail('JAX combined money changed or a component was filled in')
    if '20261106T0104Z' not in jax['split_src'] or '20261106T0104Z' not in jax['dk_src'] or '20261106T0104Z' not in jax['ml_source']:
        fail('JAX provenance dropped')
    if (chi['rating'], chi['type'], chi['our_side'], chi['price']['CHI'], chi['ml']['CHI'], chi['ab_m'], chi['dk_m']) != ('LEAN', 3, 'CHI', 100, 140, 56, 55):
        fail('CHI documented close changed')
    # same rating functions, two inputs: the missing-close fallback (Thu 3:07 PM CT) is a different grade
    rate_v1, rate_unified = rate_fns()
    mon = {'team': 'JAX', 'avg': -8.75}
    sp = {'JAX': f'{M}8.5', 'BAL': '+8.5'}
    rt, ty, *_ = rate_v1('JAX', 'BAL', ('JAX', 61, 78), 'JAX', mon, sp, False, no_bets=True)
    be = sc.breakeven('JAX', 'BAL', -122, 102)
    rt, gap = rate_unified(rt, ty, 61, 78, 'JAX', be)
    if (rt, ty, f'{gap:+g}') != ('LEAN', 3, '+6'): fail(f'documented JAX grades {rt} T{ty} {gap}')
    raw = json.loads(subprocess.check_output(['git', 'show', 'origin/snapshots:snapshots/dk_20261105T2107Z.json'], text=True))
    sao = json.loads(subprocess.check_output(['git', 'show', 'origin/snapshots:snapshots/sao_20261105T2107Z.json'], text=True))
    saoml = json.loads(subprocess.check_output(['git', 'show', 'origin/snapshots:snapshots/saoml_20261105T2107Z.json'], text=True))
    g = next(x for x in raw['games'] if 'Jaguars' in x['matchup'])
    side = {s['side'].split()[1]: s for s in g['spread']}
    if side['Ravens']['side'].split()[-1] not in ('+10',) or side['Ravens']['odds'].replace('\u2212', '-') != '-115':
        fail('2107Z fallback is no longer BAL +10 -115; the regression fixture moved')
    sm = next(x for x in sao['games'] if x['home'] == 'BAL' and x['away'] in ('JAC', 'JAX'))
    ml = next(x for x in saoml['games'] if x['home'] == 'BAL' and x['away'] in ('JAC', 'JAX'))
    abm = int((sm['money_away'] + ml['money_away']) / 2 + 0.5)
    rt, ty, *_ = rate_v1('JAX', 'BAL', ('JAX', abm, 70), 'JAX', mon, {'JAX': f'{M}10', 'BAL': '+10'}, False, no_bets=True)
    if (rt, ty) == ('LEAN', 3): fail('Thu 3:07 PM CT pull no longer regrades JAX; test is not watching the bug')
    if (rt, ty) != ('STRONG', 1): fail(f'fallback grade {rt} T{ty} abm {abm}')
    # saved lines for every game whose raw close is on file, plus the two preserved closes
    built = {(p['week'], p['game'], p['side']): p for p in pregame.build(ROOT + '/')['lines']}
    saved = {(p['week'], p['game'], p['side']): p for p in json.load(open('data/pregame_lines.json'))['lines']}
    for k, row in saved.items():
        if k[0] > 8 and k[1] != 'JAX@BAL': continue
        if built.get(k) != row: fail(f'pregame changed a settled line {k}: {built.get(k)} != {row}')
    bal = built[(9, 'JAX@BAL', 'BAL')]
    if (bal['line'], bal['price'], bal['ml']) != (8.5, 102, 350): fail(f'JAX pregame fell back: {bal}')
    # fresh board: a real file at the cited stamp is graded from that file, not frozen
    # and a later pre-kickoff pull moves a game that has not settled
    fix = os.path.join(WORK, 'snap_w9_test_fixture')
    try:
        os.makedirs(fix, exist_ok=True)
        json.dump({'fetched_utc': '2026-11-06T01:04:53+00:00', 'games': [{'matchup': 'JAX Jaguars @ BAL Ravens', 'spread': [
            {'side': 'JAX Jaguars -8.5', 'odds': '-122'}, {'side': 'BAL Ravens +8.5', 'odds': '+103'}]}]},
                  open(os.path.join(fix, 'dk_20261106T0104Z.json'), 'w'))
        json.dump({'fetched_utc': '2026-11-06T01:05:13+00:00', 'games': [{'away': 'JAX', 'home': 'BAL', 'ml': {'away': '-455', 'home': '+350'}}]},
                  open(os.path.join(fix, 'espn_dk_20261106T0104Z.json'), 'w'))
        json.dump({'fetched_utc': '2026-11-06T01:04:53+00:00', 'games': []}, open(os.path.join(fix, 'sao_20261106T0104Z.json'), 'w'))
        if (9, 'JAX@BAL') in sc.missing_closes(ROOT, WORK): fail('present raw close was still treated as missing')
        got = line_of(pregame.build(ROOT + '/')['lines'], 9, 'JAX@BAL', 'BAL')
        if got['price'] != 103 or 'dk_20261106T0104Z.json' not in got['source']: fail(f'fresh close file ignored: {got}')
        shutil.rmtree(fix)
        if (9, 'JAX@BAL') not in sc.missing_closes(ROOT, WORK): fail('deleting the fixture still left the close present')
        os.makedirs(fix, exist_ok=True)
        json.dump({'fetched_utc': '2026-11-08T13:00:00+00:00', 'games': [{'matchup': 'CIN Bengals @ ATL Falcons', 'spread': [
            {'side': 'CIN Bengals -2.5', 'odds': '-110'}, {'side': 'ATL Falcons +2.5', 'odds': '-110'}]}]},
                  open(os.path.join(fix, 'dk_20261108T1300Z.json'), 'w'))
        json.dump({'fetched_utc': '2026-11-08T13:00:30+00:00', 'games': [{'away': 'CIN', 'home': 'ATL', 'ml': {'away': '-155', 'home': '+130'}}]},
                  open(os.path.join(fix, 'espn_dk_20261108T1300Z.json'), 'w'))
        got = line_of(pregame.build(ROOT + '/')['lines'], 9, 'CIN@ATL', 'ATL')
        jax = line_of(pregame.build(ROOT + '/')['lines'], 9, 'JAX@BAL', 'BAL')
        if (got['line'], got['price']) != (2.5, -110) or 'dk_20261108T1300Z.json' not in got['source']: fail(f'fresh board did not move CIN@ATL: {got}')
        if (jax['line'], jax['price'], jax['ml']) != (8.5, 102, 350): fail(f'fresh board regraded settled JAX: {jax}')
    finally:
        shutil.rmtree(fix, ignore_errors=True)
    if glob.glob(os.path.join(WORK, 'snap_w9_test_fixture', '*')): fail('test fixture snapshot was left behind')
    if (9, 'JAX@BAL') not in sc.missing_closes(ROOT, WORK): fail('close still looks present after cleanup')
    print('settled-close regression ok: missing JAX/CHI kept, fresh board moves only the open game')

if __name__ == '__main__':
    main()
