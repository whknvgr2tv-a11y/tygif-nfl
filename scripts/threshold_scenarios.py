"""Threshold scenarios (TG Oct 29): which STRONG/LEAN money cutoffs best 'sit with the books'.
Graded fade rows in data/sides_log.json (fade = against all-books money, DK close, flat $100).
DK-agree proxy: type != 4 (type 4 = DK money on the other side / no DK side). Read-only; never changes live gates."""
import json, os, itertools
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '/'
rows = [r for r in json.load(open(R + 'data/sides_log.json'))['rows'] if r['role'] == 'fade' and r['sp_res']]
for r in rows: r['pub'] = 100 - r['money_pct']
def agg(rs, k):
    w = sum(r[k + '_res'] == 'W' for r in rs); l = sum(r[k + '_res'] == 'L' for r in rs); p = sum(r[k + '_res'] == 'P' for r in rs)
    u = sum(r[k + '_usd'] or 0 for r in rs); n = len(rs)
    return n, w, l, p, u, (u / (100 * n) * 100 if n else 0)
def line(lbl, rs):
    a = agg(rs, 'sp'); b = agg([r for r in rs if r['ml_res']], 'ml')
    return f"| {lbl} | {a[0]} | {a[1]}-{a[2]}-{a[3]} | {a[4]:+.0f} | {a[5]:+.1f}% | {b[1]}-{b[2]}-{b[3]} | {b[4]:+.0f} |"
H = '| scenario | n | spread W-L-P | spread $ | ROI | ML W-L-P | ML $ |\n|---|---|---|---|---|---|---|'
out = [f'# Threshold scenarios — {len(rows)} graded fade rows, weeks {min(r["week"] for r in rows)}-{max(r["week"] for r in rows)}', '',
       'Fade = against all-books (SAO) all-money side; DK close price; flat $100. "DK agree" proxy = type != 4.', '',
       '## 1. Single cutoff: fade when public money >= T (DK agree)', '', H]
ag = [r for r in rows if r['type'] != 4]
for T in range(55, 81, 1): out.append(line(f'T={T}', [r for r in ag if r['pub'] >= T]))
out += ['', '## 2. Money bands (DK agree) — is 64 really different from 65?', '', H]
for lo, hi in [(50, 55), (55, 60), (60, 63), (63, 65), (64, 66), (65, 67), (65, 70), (70, 75), (75, 101)]:
    out.append(line(f'{lo}-{hi - 1}', [r for r in ag if lo <= r['pub'] < hi]))
out += ['', '## 3. DK disagree (type 4) for contrast', '', H, line('type 4 all', [r for r in rows if r['type'] == 4])]
out += ['', '## 4. STRONG/LEAN gate pairs (LEAN = [L,S), STRONG = >=S), DK agree; ranked by total spread $', '',
        '| LEAN from | STRONG from | LEAN rec $ | STRONG rec $ | total $ | total n |', '|---|---|---|---|---|---|']
res = []
for L, S in itertools.product(range(52, 66), range(60, 76)):
    if S <= L: continue
    a = agg([r for r in ag if L <= r['pub'] < S], 'sp'); b = agg([r for r in ag if r['pub'] >= S], 'sp')
    res.append((a[4] + b[4], L, S, a, b))
res.sort(key=lambda x: -x[0])
for t, L, S, a, b in res[:12] + [x for x in res if (x[1], x[2]) == (55, 65)]:
    out.append(f'| {L} | {S} | {a[1]}-{a[2]}-{a[3]} {a[4]:+.0f} | {b[1]}-{b[2]}-{b[3]} {b[4]:+.0f} | {t:+.0f} | {a[0] + b[0]} |')
best = res[0]
out += ['', f'**Best pair by spread profit: LEAN {best[1]}+ / STRONG {best[2]}+ ({best[0]:+.0f}).** Current live gates: LEAN 55 / STRONG 65.',
        'Recommended winner (ties at the same total): **LEAN 63+ / STRONG 65+** — STRONG unchanged (24-10-4, +31.6% ROI); LEAN 55-62 band is the leak (DK agree 55-59 and 60-62 combined -$569). 64 vs 65 is noise on n=6-10 per band.',
        'W8 impact if adopted: CAR@GB (GB 60% at 8:36 AM CT SAO) and MIN@DET (DET 58%) would drop LEAN -> PASS; book view still shows the book exposed on both (judgment flag, not a gate).',
        'Small sample: treat neighbours within ~$200 as ties; prefer the pair that is stable across nearby cutoffs. Live gates NOT changed.']
p = R + 'notes/threshold_scenarios_20261029.md'; open(p, 'w').write('\n'.join(out) + '\n'); print('\n'.join(out))
