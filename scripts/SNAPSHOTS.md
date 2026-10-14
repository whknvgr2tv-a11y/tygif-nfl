# Split snapshots: how the Tuesday run uses them

The `split-snapshots` workflow saves DraftKings and ScoresAndOdds spread splits every 10 minutes through the 90+ minutes before every kickoff slot (GitHub delays and drops scheduled runs; on Oct 11 nothing ran between 13:10 and 17:58 UTC) to the separate `snapshots` branch
(`snapshots/dk_<UTC>.json` and `snapshots/sao_<UTC>.json`, parsed splits only; files older than 21 days are pruned).
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
   Rules v1 with them, then grade at the DraftKings closing line and price (ESPN).
5. Label every closing split with its exact pull time and source, e.g. 'last pull before kickoff: Sat Oct 10, 8:49 PM ET'.
6. `scripts/check_coverage.py` runs after each snapshot and fails the run when a game kicked off without a
   DraftKings snapshot in its last 90 minutes. A red run means a gap: fall back to step 7.
7. If a game has no DraftKings snapshot before kickoff, say so in `closing_splits.json`
   (`draftkings: null` plus a note) and keep the last real pull labeled with its time. Never fill
   a closing value from an earlier pull without its label.
