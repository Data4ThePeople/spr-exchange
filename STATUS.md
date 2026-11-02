# Status

Project: SPR_explainer
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: none yet
Step: 1
Since: 2026-11-02

## Steps

| Step | What | Confirmed | Notes |
|---|---|---|---|
| 1  | Exploration and analysis | | |
| 2a | Draft with brackets resolved | | |
| 2b | Eric's edit, Claude's look-over | | |
| 2c | Slice markup | | |
| 2d | Hero 1680x1080 + alt text | | |
| 2e | SEO | | |
| 2f | Pushed to Prismic (draft) | | |
| 2g | Mailchimp teaser | | |

## Stale

None.

## Log

- 2026-11-02 Step 1 opened for post 3, a short update for publication on November 3, 2026. Topic: the award sheets for round 4 (FY26 Release No. 4) and FY27 Release No. 1, both posted by DOE on October 29, 2026 and saved by the weekly check. Round 4: 23,800,000 of 40,000,000 barrels awarded to six firms, as of October 13. FY27-1: 16,750,000 of 17,000,000 barrels to five firms, as of October 28. Combined 40,550,000 barrels, to be picked up November 2026 to January 2027 and returned with a premium by the end of 2029. Post 2's record moved to STATUS-spr-sale-vs-loan.md (complete); post 1's is in STATUS-spr-exchange.md.
- 2026-11-02 Carried in: (a) the weekly check flagged both rounds as new because DOE's listing now prefixes the names with "1-" and "2-"; the name match needs fixing; (b) Trafigura (300,000) and Energy Transfer (550,000) in round 4 were awarded less than the RFP's 3,000,000-barrel minimum offer, as in round 3; (c) awards are not deliveries; the EIA weekly SPR level is the only public check; (d) the weekly award check still writes its log line to this file.
- 2026-11-02 Plan approved. Done: weekly check matches DOE's prefixed names ("nothing new"); build_ledger.py takes the round from rounds.csv (FY27-1 had read as round 1); Gunvor USA spelling mapped; rounds.csv award dates and award_sheet_url; ledger 42 contracts, 174,110,000 barrels, every sheet ties; weekly SPR stocks pulled again through October 23 (no revisions); round 4 uptake 59.5% and margins unchanged; return schedule now all seven rounds. Published pages frozen (posts 1 and 2 embed them); post 3 page is dist/ledger-2026-11.html (embed 1,560px). Own tie-out: 178 checks pass. Correction to what I told Eric in chat: four round 4 awards (not two) are below the 3M minimum offer, plus two in FY27-1.
- 2026-11-02 Found: Yahoo has revised its futures history since October 12. A re-pull dropped 1,899 saved closes and changed most WTI closes from March on (up to $4.72). Re-pull discarded; saved copy kept. Repriced with the re-pull, every round's margin moves (1.b $17.03 to $9.63; 3 $2.47 to -$0.54). The saved front month sits closer to EIA spot. Open for Eric: post 1's published margins rest on the saved copy; no official settlement file to settle it.
- 2026-11-02 Eric asked for repayment terms, the settled premium and the borrower's margin. Noted in DATASETS.md (post 3 section): both rounds are still loans; return windows and premiums per lot; agreed premiums are not published (minimums only); round 4 margin $9.18 to $11.21 at the minimum premium; FY27-1 not computed because bid-day futures are not in the saved copy.
- 2026-11-02 Eric: "static charts. quick update", drop "emergency", report the latest round's economics only if they can be calculated, point readers back to the earlier posts. The interactive page dist/ledger-2026-11.html was removed, with its template and --out changes. Built scripts/build_update_chart.py -> charts/01-newest-rounds.png (company bars for round 4 and FY27-1, dark palette, validated colors) and its CSV; tie_out.py checks the chart against the sheets. FY27-1 economics cannot be calculated from verified prices, so the post carries none for it. Own tie-out passes. Independent tie-out launched.

