# Splits sources round 2 — 2026-10-29 ~9:25 AM CT
Key fact: only DraftKings and Circa publish real per-book handle %. BetMGM = tickets only. FanDuel/Caesars publish nothing (SharpAPI docs: "No other book publishes betting splits").
1. DK Network first-party table dknetwork.draftkings.com/draftkings-sportsbook-betting-splits/ — DK's own Bets%+Handle%, 5-min, all jurisdictions. FREE. Currently "temporarily unavailable" (likely why DK cache died). Poll it; = true primary when back.
2. SharpAPI /api/v1/splits — DK + Circa handle%+bets%, BetMGM bets only, 5-min, 48h history. Pro $229/mo. Same upstreams as VSiN, but gives full Circa board (not 1 free game).
3. Playbook API /v1/splits — free tier = multi-book aggregate (consensus, weak). Starter+: Novig/ProphetX exchange splits w/ real $ volume + trade counts, + history. Genuinely independent money. Price not confirmed.
4. VSiN Pro — DK+Circa full board, both books. Paid subscription.
5. Circa via VSiN free (current).

## Round 2b spot-checks — 9:25 AM CT
| Source | What it has | Cost | Verdict |
|---|---|---|---|
| Sports Insights / Bet Labs | Real bets from 7 contributing (offshore-style) books, bet% + money%, per-book breakdown via "i" icon; Bet Labs history since 2003 | Money% paid; SI Pro $249/mo (their page), 4-day trial | MAYBE — independent, but not DK/Circa; books unnamed |
| Don Best | Odds only, no betting %s | $499/mo ($99 lite) | FAIL |
| BetQL | Ticket % only, from unnamed partner books | paid | FAIL (tickets only) |
| VegasInsider | Consensus = handicapper picks, premium | paid | FAIL |
| OddsJam | Odds API/sharp signals; no per-book handle% found | paid | FAIL (unverified splits) |
| The Odds API | Lines only, no splits | — | FAIL |
| Bookies.com | Page fetch showed no splits data/source | — | FAIL (unverified) |
| Dimers / Unabated / DarkHorse | Not confirmed to publish money%; odds/models | — | FAIL-unverified (no evidence found) |
Prices: VSiN Pro — not published; monthly/annual/season, annual 50% off; promo "Hoops Special $29.99", POD26 17% off annual. Includes DK+Circa splits real-time. Playbook API Starter price — not findable (pricing pages returned nothing).
DK Network splits page: still "temporarily unavailable" at ~9:25 AM CT.
