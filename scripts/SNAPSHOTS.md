# Split snapshots: how the Tuesday run uses them

The `split-snapshots` workflow saves DraftKings and ScoresAndOdds spread splits about 20 and 5 minutes before every kickoff slot to the separate `snapshots` branch
(`snapshots/dk_<UTC>.json` and `snapshots/sao_<UTC>.json`, parsed splits only; files older than 21 days are pruned).
Nothing here is on main, so the site never serves it; the branch is still visible in this public repo.

Tuesday run, for each game of the week:
1. `git fetch origin snapshots` and read `snapshots/*.json` from it.
2. DraftKings closing split = the game's entry (match on teams) in the LAST `dk_*.json` whose
   `fetched_utc` is before kickoff. DraftKings removes a game at kickoff, so later files won't have it.
   Money = `handle_pct`, bets = `bets_pct`, from our side's row.
3. All-books closing split = the ScoresAndOdds week page (`/nfl/consensus-picks?week=2026-reg-N`)
   fetched on Tuesday; it keeps each game's final split. Cross-check with the last `sao_*.json`
   before kickoff; if they differ, use the week page and note it.
4. Write both, with their times and sources, to `data/closing_splits.json`; rate the game under
   Rules v1 with them, then grade at the DraftKings closing line and price (ESPN).
5. If a game has no DraftKings snapshot before kickoff, say so in `closing_splits.json`
   (`draftkings: null` plus a note) and keep the last real pull labeled with its time. Never fill
   a closing value from an earlier pull without its label.
