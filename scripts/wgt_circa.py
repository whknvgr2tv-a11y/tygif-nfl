"""Wise Guy Team Circa MONEYLINE board (wiseguyteam.com/circa-betting-splits) -> wgt_circa_<stamp>.json.
# UNUSED: reverted Oct 29 2026 (lag + borderline 3-pt gap vs VSiN Circa). See notes/splits_deep_research_20261029.md
TG, Oct 29: free fill for Circa money when free VSiN Circa only shows ~1 game. Adopted after same-minute checks vs VSiN Circa
(CAR@GB money 0 pts @10:09 CT, 3 pts @10:52 CT). Rules: ML ONLY (no spread/total Circa invented from it); rows with 0/100 money
(thin/no handle) are skipped; WGT's DraftKings board is NOT used (failed same-minute check vs VSiN-DK, 11-18 pt gaps).
CLI: python3 scripts/wgt_circa.py <wgt_circa.html> <out_dir> [stamp]"""
import re, json, sys, os
def parse(h):
    t = re.sub(r'<script.*?</script>|<style.*?</style>', '', h, flags=re.S); t = re.sub(r'<[^>]+>', ' ', t); t = re.sub(r'\s+', ' ', t)
    a = t.find('NFL: Circa moneyline'); b = t.find('Full NFL betting splits', a)
    if a < 0 or b < 0: return None, []
    sec = t[a:b]; m = re.search(r'read ([A-Z][a-z]{2} \d+, \d{4}, [\d:]+ [AP]M ET)', sec); read = m.group(1) if m else None
    row = r'([A-Z][A-Za-z. ]+?) ([+-]\d+|--) [+-]\d+ \S+ (\d+)% (\d+)%'
    games = []; seen = set()
    for g in re.finditer(r'[A-Z][a-z]{2} \d+:\d+ [AP]M ET \S+ (.+?) @ (.+?) Circa ML Best ML Bets% Money% ' + row + ' ' + row, sec):
        aw, hm, n1, ml1, b1, m1, n2, ml2, b2, m2 = g.groups()
        if ml1 == '--' or ml2 == '--': continue          # next week's game with no Circa price
        k = (aw.split()[-1], hm.split()[-1])
        if k in seen: continue
        seen.add(k)
        games.append({'matchup': f'{aw} @ {hm}', 'away_nick': k[0], 'home_nick': k[1], 'source': 'wgt_circa_ml',
                      'thin': int(m1) in (0, 100), 'moneyline': [
                          {'side': f'Circa {k[0]}', 'odds': ml1, 'handle_pct': int(m1), 'bets_pct': int(b1)},
                          {'side': f'Circa {k[1]}', 'odds': ml2, 'handle_pct': int(m2), 'bets_pct': int(b2)}]})
    return read, games
if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]; st = sys.argv[3] if len(sys.argv) > 3 else 'x'
    read, g = parse(open(src, encoding='latin-1').read()); os.makedirs(out, exist_ok=True)
    json.dump({'source': 'wiseguyteam.com/circa-betting-splits (Circa ML only)', 'read': read, 'html': os.path.basename(src), 'games': g},
              open(f'{out}/wgt_circa_{st}.json', 'w'), indent=1)
    print(read, len(g), 'games;', sum(x['thin'] for x in g), 'thin')
