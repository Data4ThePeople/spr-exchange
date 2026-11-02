# Status

Project: SPR_explainer
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: spr-below-the-floor
Step: 2d
Since: 2026-11-02

## Steps

| Step | What | Confirmed | Notes |
|---|---|---|---|
| 1  | Exploration and analysis | 2026-11-02 | Round 4 and FY27-1 keyed; two static charts; own tie-out passes; two independent tie-outs, fixes applied |
| 2a | Draft with brackets resolved | 2026-11-02 | Claude drafted at Eric's instruction; independent fact-check, fixes applied; closing still a bracket for Eric |
| 2b | Eric's edit, Claude's look-over | 2026-11-02 | Eric's edits and closing; six look-over items accepted; floor sources linked |
| 2c | Slice markup | 2026-11-02 | No changes needed; 41 blocks, 2 images with captions, divider once, no embeds |
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
- 2026-11-02 Eric: include the round 4 margin, "do the math to get the profit potential", separate chart if needed. Built charts/02-round-4-profit.png: all 16 lot-window margins on bid day, sale at the contract for the month after pickup (post 1's basis, best lot $9.87 matches post 1), arithmetic written out for the best one; footnote says Aug-Oct 2029 uses August alone. Ceiling for the whole round: $178.7M to $234.9M. tie_out.py recomputes every bar from the raw futures files; passes.
- 2026-11-02 Independent tie-out (fresh agent) of chart 01 and the loan terms: hashes match; every bar, label and date matches; awards below the minimum offer match. Errors found in my DATASETS summary, fixed: round 4 premium range is 7% to 17.5% (not 19.5%); FY27-1 is 14% to 19.5% (not 13% to 20%); "Gunvor USA" also appears in round 4. Footnote "not the same as barrels delivered" was partly supported; reworded to "DOE publishes barrels awarded, not barrels delivered." It confirmed DOE leaves the premium out on purpose (RFP Section M: offer data "excluding exchange ratio") and found no free source for October 21 futures settlements. Could not check: the FY27-1 premium table as an image, the round 4 Q&A, the firm types from primary sources.
- 2026-11-02 Second independent check (chart 02, 16 lot-window margins): no differences; every premium, price and margin matched to the cent from the saved raw futures; the ceiling $178.7M to $234.9M matched. Word flags: "locks in ... by buying futures" stated an assumption as fact; "the most a borrower could make" holds only on our assumptions.
- 2026-11-02 Eric: chart 02 "too busy"; asked for post 1's round 4 card instead. Rebuilt as a static card (best lot, $88.43 - $78.56 = $9.87; 32.3%; 17.5%; estimated profit $47 million = 4.8M trading-house barrels x $9.87, post 1's method), worded as a condition ("if prices were locked in"). All its inputs were in the independent checks; the $47 million is their product. tie_out.py recomputes the card from raw files; passes.
- 2026-11-02 Eric wants to say FY27-1's economics were very likely good (98.5% taken, mostly trading houses). EIA daily spot pulled again (no revisions): $96.24 on round 4's bid day, $103.95 on FY27-1's (8.0% higher). Return-side 2028-29 prices for October 21 are still not verifiable. Wording proposed to Eric in chat.
- 2026-11-02 Eric confirmed Step 1. Next: 2a, which needs a slug and Eric's draft.
- 2026-11-02 Step 2a opened. Eric: "i want you to draft this. this is a quick update": barrels just lent, how much to traders, when paybacks are due, and what experts consider the reserve's minimum operating level; lead: if companies take it all, the reserve drops below the bottom of the range, "we will find out if the experts are right." Claude drafted the whole post at his instruction, as with post 2. Working slug spr-below-the-floor (Claude's, for Eric to change); date November 3, 2026, 6:30 a.m. EST (DST ended November 1). New sources for the floor section are in DATASETS.md: CNBC August 15 (DOE 70M, Misra, Hochstein, Rapidan), Dallas Fed Q3 survey, 42 U.S.C. 6241(h) (252.4M, limited drawdowns only). Left out: the "1981 GAO 250 million" claim (report not found) and the unsourced "DOE projects 243 million". Closing left as a bracket for Eric.
- 2026-11-02 Eric asked to add to the due-back section: the last loans "didnt come back on time", "we are still waiting for much of it", no penalties when pushed back, link the earlier post. Written to match post 2 and the records: dates moved on 10 of 13, two years or more on seven; companies did not miss deadlines (government agreed); Trafigura's remaining oil moved to July-October 2026, return not shown in the records; ExxonMobil 22PO0013 now due October 1 to November 30, 2026; "no adjustment to the premium" quoted from the modifications (several say so, others are silent). "Still waiting for much of it" not stated: not known from the records. Link to post 2.
- 2026-11-02 Independent fact-check of the 2a draft (fresh agent, own downloads): every number matched (282.6M, 242M, lowest since February 1982, $96.24/$103.95, 67.2%, 20.2%, 91.9%, 49.8%, pickups, return windows, "excluding exchange ratio", June 500,000, round 1 returns from September 1, 2026). Hochstein, DOE 70M, Rapidan, Dallas Fed and the statute supported. Fixed: two Misra phrases were CNBC paraphrase, not quotes; "share taken fell when the trade paid less" rested on two rounds (now just the June comparison); the 8% spot rise now says it helps only if 2028-29 prices rose less, which we cannot check. Flagged to Eric, not changed: "we are about to find out whether those experts are right" (his lead) may be more certain than the data allow; October 29 is the files' last-modified date.
- 2026-11-02 Eric confirmed 2a. Next: 2b, Eric edits POST.md (closing bracket still open); Claude looks it over.
- 2026-11-02 Step 2b opened. Waiting for Eric's edits to POST.md.
- 2026-11-02 Step 2b: Eric edited POST.md (grain-of-salt line, floor intro, low-point sentence, his closing with a link bracket). Six look-over items accepted: link bracket resolved; comes/withdrawals; "we have no idea" -> "the true bottom is not known" (the stricter option, since "nobody" is a universal claim); heading "What to watch"; hyphens; delivery caveat added to the limits.
- 2026-11-02 Eric asked for links on the floor sources. Added: CNBC August 15 (DOE 70M, Misra, Hochstein, Rapidan), Dallas Fed Q3 survey page, 42 U.S.C. 6241 (Cornell LII), EIA weekly SPR stocks page. All four URLs return 200.
- 2026-11-02 Eric confirmed 2b. Next: 2c, slice markup.
- 2026-11-02 Step 2c opened. Convert-only: 41 blocks (drop cap, 6 headings, 2 images with captions, 14 list items, 17 paragraphs), divider once before the limits; no embeds, so no iframe spacers. Hero warnings expected until 2d.
- 2026-11-02 Eric confirmed 2c. Next: 2d, hero 1680x1080 and alt text.
- 2026-11-02 Step 2d opened. No hero idea from Eric, so Claude wrote two prompts in posts/spr-below-the-floor/hero-prompt.md: a salt cavern cutaway with low oil under a painted FLOOR? line (recommended), and the navy SPR barrel with a measuring stick. Waiting for Eric's image or his own idea.
- 2026-11-02 Step 2d: Eric generated the cavern image from the revised Prompt 1 (several FLOOR? lines). Source kept as images/spr-below-the-floor-hero-source.jpg (2752x1536); cropped from the center to images/spr-below-the-floor-hero-1680x1080.png; the barrel is partly cut off at the right, as Eric expected. Lettering: four FLOOR? signs spelled correctly, plus a mirror-image reflection of one on the oil surface; barrel text partly cropped. Alt 479 characters; hero check ok. Waiting for Eric to confirm.

