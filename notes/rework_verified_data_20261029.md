# TYGIF rework — verified data only (2026-10-29)
No paid tools. Stop patchwork. Live site NOT changed by this note.

## 1. What stays
- STRONG/LEAN thresholds as coded now (no retune).
- All-money basis (money %, not tickets) for signals.
- Flat $100 grading; separate records per tier (STRONG / LEAN) and per market.
- Grade on the last pull before kickoff.
- Line-shop (7 books) for price/hold — unchanged.

## 2. What stops
- Treating VSiN-DK as a proven DK twin. It is "VSiN-reported DK", unverified while DK Network is empty.
- Inventing agreement from unverified scrapers (WGT DK, AN/SBD SAO echoes, Covers/OddsShark).
- Wiring any source that lags, freezes its stamp, or contradicts itself (WGT Circa reverted in 036ff6a).
- Adding a source without 2 same-minute pulls within 3 pts vs a live reference.

## 3. Verified-only chain
1. **DK Network splits table** (when live) = the ONLY DK source.
2. Until live: **no DK agreement claim.** Game = Type 4 PASS, note: "DK splits unavailable; no verified book money."
   Exception only if a same-minute pull matches a live DK table.
3. **Circa** only via VSiN free, only for games it actually shows, labeled "Circa" (never "DK").
4. SAO = consensus/fade context only, never agreement.
Every play shows its source label + pull time on the card.

## 4. W8 card now
- CAR +3.5 LEAN stays only if its agreement is labeled honestly ("Circa via VSiN, 1 game; DK unverified"). If it rests on VSiN-DK as "DK" → PASS.
- All other W8 games: PASS with the honest note.
- Site banner: "DK splits feed down. Only games with verified book money are graded. Board is thin this week by design."

## 5. How other tip sheets handle data (from this week's research)
- **VSiN**: publishes 1 free DK/Circa splits game; full board behind VSiN Pro. Labels book by name.
- **Action Network**: publishes bet%/money% free, but it's consensus (SAO-style) not one named book; "sharp" signals paywalled.
- **Covers**: publishes user-pick consensus %; no book handle at all.
Lesson: credible shops name the book and time-stamp; none have a free full-board per-book money feed. Thin-but-honest beats full-but-guessed.

## 6. Checklist
**SA (agent)**
- [ ] Re-label sources in builder: DK / VSiN-DK(unverified) / Circa(VSiN) / SAO; card shows label + pull time.
- [ ] Gate: VSiN-DK cannot produce agreement unless DK Network is live and same-minute check passes.
- [ ] Add PASS note text + site banner (needs TG OK before deploy).
- [ ] Decide CAR per §4; re-run self-check.
- [ ] Poll DK Network each pull; when back, 2 same-minute checks vs VSiN-DK, then restore as sole DK.
- [ ] Log every source check in notes/ with time (CT) and gap.
**TYGIF BETS**
- [ ] Post: W8 board is thin on purpose; only verified plays.
- [ ] Track STRONG and LEAN separately; flag LEAN losing streak (4-7) for review — not a data issue.
