# Splits deep research — 2026-10-29 ~10:10 AM CT
## A. DK Network
dknetwork.draftkings.com/draftkings-sportsbook-betting-splits/ -> HTTP 200 but page text "temporarily unavailable". STILL DOWN. No sample.
## Key finding
SharpAPI docs (updated Oct 28 2026): only DK + Circa publish handle %; BetMGM bets only; "no other book publishes splits, none planned". Confirms no 3rd retail book exists.
## Paths
1. SharpAPI Pro $229/mo — GET /api/v1/splits?league=nfl&sportsbook=draftkings,circa ; 5-min updates, 48h history. Gets DK even while DK Network page is down IF their DK feed still runs (unverified — ask/trial). Verify: pull same minute as VSiN-DK on CAR@GB, need <=3 pts on 2 pulls.
2. Playbook API — Free plan: consensus money% (booksUsed ~10) = SAO-type, FAIL for agreement. Starter+: include=novig,prophetx -> per-exchange % bets, % money, trades, $ volume; thin flag <25 bets. Truly independent money. Price not confirmed on page.
3. VSiN Pro — same DK/Circa as free, full board. Cheapest if < $229.
## Dead ends
- Kalshi KXNFLGAME / Polymarket: public keyless volume, but volume is total contracts (every trade has both sides) -> no side money %. Price only. FAIL as handle proxy.
- Sportradar betting-splits v3 ("150+ bookmakers" aggregate) — enterprise pricing, aggregated not per-book. FAIL for us.
- Playbook free consensus, AN/SBD/Covers/etc (prior rounds).
## Recommendation
Before CAR lock 7:10 PM CT: sign up SharpAPI (check for trial/monthly cancel) and do 2 same-minute pulls vs VSiN-DK on CAR@GB. If its DK rows are empty too (same upstream as DK Network), drop it and try Playbook Starter exchanges.

# Round 2 follow-up — 10:09 AM CT
## Prices
- VSiN Pro: vsin.com/subscribe gives NO dollar prices in page (fetch+raw HTML). Says monthly, annual (=50% off monthly), season-only offers; cancel via contacting support. Pro "real time betting splits" = DK feed (+Circa compare). Price needs checkout click.
- Playbook pricing: /pricing returns 401; no Starter price found without login.
- SharpAPI (sharpapi.io/pricing): Free $0 (DK+FD odds, 60s delay, no splits), Hobby $79, Pro $229 (splits), Sharp $399. 3-day free trial on Pro, card required, cancel before end = no charge; no long-term contracts. Docs: book_unavailable 503 if no current snapshot; no statement of where DK splits come from when DK Network is offline -> unverified.
## Circa same-minute cross-check (10:09:15-16 CT, CAR@GB)
- WGT wiseguyteam.com/circa-betting-splits (Circa read 10:45 AM ET): ML CAR +170 bets 47% money 4% / GB -195 bets 53% money 96%.
- VSiN data.vsin.com/betting-splits/?source=CIRCA&sport=NFL&view=today: ML CAR 4% money / 47% bets, GB 96% / 53%. Spread CAR+3.5 62% money/53% bets.
- GAP: 0 pts tickets, 0 pts money (ML). WGT Circa page = ML only, but lists ALL ~16 NFL games this week free (vs VSiN free 1 game). Many early-week rows 0/100% (thin).
- Earlier WGT read 6:53 ET 43/57 bets 3/97 money vs VSiN 8:36 CT 47/53, 3/97 — consistent.
- WGT's failure was its DK/consensus board, not its Circa page.
## Field workarounds
- Public search only surfaces VSiN DK page and WGT DK page as stand-ins; Reddit r/sportsbook has nothing current (old threads). DK Network URL with ?tb_edate params shows stale cached May NBA data in search index, not live. No other public workaround found. X search not run.
## Updated recommendation
Free win first: add WGT Circa ML page as a full-board Circa source (passed 0-gap same-minute vs VSiN Circa). Re-verify once more before CAR lock; ignore rows with 0/100 or both sides tiny samples. Paid next: SharpAPI Pro 3-day free trial for DK spread/total + Circa all markets — check DK rows not empty.
