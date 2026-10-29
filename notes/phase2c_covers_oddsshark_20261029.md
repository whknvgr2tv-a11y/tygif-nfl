# Phase 2c — Covers / OddsShark money% check (Thu Oct 29 2026, ~8:45 AM CT)

Verdict: NEITHER is a usable independent money/handle source. No parser/wiring added.

- Covers consensus (f13dcf.html, contests.covers.com/Consensus/TopConsensus/NFL) and
  Covers matchups (0742ee.html): % = Covers *contest players' picks* (pick counts shown,
  e.g. CAR@GB 544 CAR / 381 GB = 59%/41%). Not bets or handle at any sportsbook. ~14/14 W8
  games covered, but it's a picks poll, so ineligible for the money agreement chain.
- OddsShark: /nfl/consensus-picks fetch returned Covers HTML (redirect into Covers) — no
  separate OddsShark data; nothing saved in discovery dir either.
- Pregame (62a8e3.html): game-center shell, consensus tab loaded via JS; no % in HTML.

Sample CAR@GB vs SAO (snap_w8_20261029_0840): SAO money CAR 52 / GB 48 (bets 46/54);
Covers contest picks CAR 59 / GB 41. Different, but because it measures picks, not money.
Not an echo of SAO — just a different (non-money) metric.
