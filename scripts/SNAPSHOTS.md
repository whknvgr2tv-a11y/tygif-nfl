# Split snapshots: how the Tuesday run uses them

The `split-snapshots` workflow saves DraftKings and ScoresAndOdds spread splits every 10 minutes through the 90+ minutes before every kickoff slot (GitHub delays and drops scheduled runs; on Oct 11 nothing ran between 13:10 and 17:58 UTC) to the separate `snapshots` branch
(`snapshots/dk_<UTC>.json`, `snapshots/sao_<UTC>.json` and `snapshots/espn_dk_<UTC>.json`; never pruned, they are the grading record).
`espn_dk_*` holds the ESPN DraftKings moneyline and spread (line, price) with `fetched_utc` for every game not yet started.
Nothing here is on main, so the site never serves it; the branch is still visible in this public repo.

Tuesday run, for each game of the week:
1. `git fetch origin snapshots` and read `snapshots/*.json` from it.
2. DraftKings closing split = the game's entry (match on teams) in the LAST `dk_*.json` whose
   `fetched_utc` is before kickoff. DraftKings removes a game at kickoff, so later files won't have it.
   Money = `handle_pct`, bets = `bets_pct`, from our side's row.
3. All-books closing split = the game's entry in the LAST `sao_*.json` (or our own dated pull) fetched
   before kickoff. Never use a page read after kickoff: the ScoresAndOdds week page keeps changing
   after kickoff (Week 5: DET@ARI read 56% pre-kickoff, 78% after), so it is not a closing source (TG, Oct 13).
4. Write both, with their times and sources, to `data/closing_splits.json`; rate the game under
   Rules v1 with them, then grade at the DraftKings line, price and moneyline at the last saved pull at least 5 minutes before kickoff
   (`dk_*` for line/price, `espn_dk_*` for the moneyline). ESPN's post-game close is used only when nothing was
   recorded before kickoff. Never grade from an ESPN summary fetched after kickoff.
5. Label every closing split with its exact pull time and source, e.g. 'last split at least 5 min before kickoff: Sat Oct 10, 8:49 PM ET'.
6. `scripts/check_coverage.py` runs after each snapshot and fails the run when a game kicked off without a
   DraftKings snapshot in its last 90 minutes. A red run means a gap: fall back to step 7.
7. If a game has no DraftKings snapshot before kickoff, say so in `closing_splits.json`
   (`draftkings: null` plus a note) and keep the last real pull labeled with its time. Never fill
   a closing value from an earlier pull without its label.

## Moneyline plays (TG, Oct 13)
Every weekly run handles ML alongside the spread, using the same card template and records kept separate:
- A STRONG or LEAN spread play gets a moneyline play on our team only when its group (rating + type + favorite/underdog)
  is above $0 over prior weeks (all weeks before the game's week). Never on a Type 3 underdog.
- Card run (any build before kickoff; the card is rebuilt as new pulls arrive): show 'Moneyline: <team>' on qualifying cards
  (team only; never a price). Favorite/underdog comes from the latest ESPN DraftKings moneyline capture (`espn_dk_*`, taken by
  the snapshot workflow and by build/settle.py); the card's one 'As of' line gives the time of the pull it uses.
- Tuesday run: grade each ML play W/L/P from the final score at the DraftKings moneyline at the last saved pull at least 5 minutes before kickoff (`espn_dk_*`;
  ESPN `pickcenter` close only if nothing was recorded), flat $100. Write it to `data/ml_log.json`. If the price is missing, record that and
  grade nothing. STRONG ML and LEAN ML records stay separate and are never added to the spread records.
- Prices live only in the data files. No prices or odds on the site or in the txt files; no dated update or change notes.

## Records (TG, Oct 13)
Every record on the site covers all weeks to date (Week 1 through the last graded week), built from the
look-back games plus every graded row in `data/live_log.csv` and `data/ml_log.json`. No split or label by
period anywhere (no 'Weeks 1–4', 'look back', 'backtest' or 'live'). STRONG, LEAN, STRONG ML and LEAN ML stay
separate, never combined. Card record line: 'Type N · <type name> · <RATING>: W-L-P, +$X' for that type and rating.
After each settle (`python3 build/settle.py`; Monday: `--monday` first writes the Monday lines), the build (build/clean_build.py) rebuilds; its self-check and deep check recompute these from the data.
No explanatory prose on cards or pages beyond plays, records and the checklist; How keeps the brief rules.

## Moneyline groups (TG, Oct 14)
- Every STRONG or LEAN spread play also has our side graded on the DraftKings moneyline recorded before kickoff, favorite or underdog, flat $100, profit rounded per play (ESPN game summary `pickcenter`). Write every row to `data/ml_log.json` with `fd` (Fav/Dog).
- Groups: rating + type + favorite/underdog (e.g. LEAN Type 3 Underdog).
- ML posting rule: post a moneyline play only when its group record over prior weeks (all weeks before the game's week) is > $0. $0 or no history: no play.
- Type 3 underdog: never a moneyline play (pass on the moneyline; the spread is unaffected).
- Re-check after every Tuesday grade. Graded history is never changed by this rule; STRONG and LEAN ML records stay separate from each other and from the spread.
- Home and This Week: one card per game in kickoff order, with the spread call (STRONG/LEAN/PASS + type record + games list), the ML call (play or no play + group record + games list), the checks row and kickoff/final.

## Fixed process (TG, Oct 15)
The weekly process and its sources live in `data/process.json`. clean_build.py reads it; the build fails if any game in any week misses a required field or uses a source not listed there (recorded gaps only: Weeks 1-4 splits, Week 5 DraftKings closing splits).

## Settle (Oct 15)
`python3 build/settle.py` settles finished games (any day, e.g. after Thursday night), builds twice and runs the deep checks.
`python3 build/settle.py --monday` first writes `build/inputs/tr_monday_w<N>.json` for the next week (`build/monday_lines.py`: TeamRankings books 2 and 3, last quote before Sun 11:00 PM CT / Mon 12:00 AM ET).
Signed-off games are frozen in `data/signed_off_games.json`; the build fails if any of their rows change.
