# Status

Project: SPR_explainer
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: spr-exchange
Step: 2d
Since: 2026-10-11

## Steps

| Step | What | Confirmed | Notes |
|---|---|---|---|
| 1  | Exploration and analysis | 2026-10-11 | Own tie-out 32/32; independent tie-out found no difference in any published number; three wording edits accepted by Eric |
| 2a | Draft with brackets resolved | 2026-10-11 | Title: Meet the Speculative Petroleum Reserve |
| 2b | Eric's edit, Claude's look-over | 2026-10-11 | Three look-overs; 23 edits accepted; open source checks listed in the log |
| 2c | Slice markup | 2026-10-11 | Defaults only; 30 slices |
| 2d | Hero 1680x1080 + alt text | | |
| 2e | SEO | | |
| 2f | Pushed to Prismic (draft) | | |
| 2g | Mailchimp teaser | | |

## Stale

None.

## Log

- 2026-10-10 Step 1 opened. Topic: the 2026 SPR exchange. Who took the barrels, why borrowers paid premiums of about 25%, and where the oil went. Deliverables for Step 1: a searchable award ledger tool (dist/ledger.html) and a "why pay a 25% premium" trade simulator (dist/simulator.html). Plan approved by Eric the same day: verify the brief's facts against primary sources first, then build the ledger, then the simulator. Award PDFs from Eric are in data/raw/doe_awards/. The project brief stays local and is not committed.
- 2026-10-10 Verification pass. Award PDFs from Eric are byte-identical to DOE's archive copies; ledger rebuilt from the PDFs by scripts/build_ledger.py matches the brief line for line (31 contracts, 133,560,000 barrels). All six RFPs, amendments and Q&As downloaded to data/raw/doe_rfps/ with a manifest. The September 29 round is RFP DE-RP96-26PO00006 (FY26 Release No. 4); no award sheet posted as of October 10. EIA series pulled (scripts/fetch_eia.py). Dated WTI and Brent futures pulled from Yahoo (scripts/fetch_futures.py); expired 2026 months are not available. Freight copied from the VLCC project. DATASETS.md written.
- 2026-10-10 Ledger tool built: dist/ledger.html from scripts/build_ledger_page.py and scripts/ledger_template.html. Filters, four headline cards, stacked bars by round, company leaderboard, weekly SPR level with award dates, sortable table with DOE source links, CSV download. Checked at 879px and 390px inside an iframe; all filters tested by script. Full height at 879px is about 1,400px. Waiting on Eric's review before the simulator. GitHub Pages not yet enabled.
- 2026-10-11: worked trade example for round 1.b (scripts/trade_math.py). Eric dropped the live-curve simulator in favor of a math explainer. Waiting on his read of the estimate.
- 2026-10-11: trade math extended to rounds 3 and 4 (per-lot output in data/processed/trade_example_round_*.csv). Waiting on Eric's read.
- 2026-10-11: round 4 priced on bid date and latest close; RFP B-1 terms re-read against the PDF and match rfp_terms.csv. DOE has posted no award as of today.
- 2026-10-11: trade explainer built (dist/trade.html) with rounds 1.b, 3 and a pending card for round 4. Waiting on Eric's review and edits. Hero idea from Eric saved to memory.
- 2026-10-11: modeled profit for trading houses added to dist/trade.html (per-barrel best case x trader barrels, before costs). All six RFPs put transport costs on the borrower (B.6(b)); not priced.
- 2026-10-11: trade explainer relabeled 'Maximum profit before transportation costs' with Eric's fine print; Nederland pipeline tariffs saved. Terminal fees not public.
- 2026-10-11: pulled the FY22 Winter Exchange RFP set for comparison; 2021-22 premiums were fixed by DOE (2.3% to 9.1%), not bid, and unchanged by amendments. Angles from Eric saved to memory.
- 2026-10-11: read two Argus reports on delayed returns of 2021-22 exchange oil; contract modifications exist only as FOIA releases, not held. Eric is considering two posts: (1) how the exchange works, (2) 2021-22 vs 2026 handling.
- 2026-10-11: Eric reframed post 1 around two government risks (return risk; the gap years through 2027). Checked return windows, letter of credit and force majeure terms, and the 2027 futures move against the data.
- 2026-10-11: return schedule bounds built (dist/returns.html): 8.48M certain back by end of 2027, 87.06M by end of 2028, last due July 31, 2029. Waiting on Eric's review.
- 2026-10-11: own tie-out script written (scripts/tie_out.py), 32 of 32 checks pass. Independent tie-out by a fresh agent launched. Eric says the post publishes 2026-10-12; no records request.
- 2026-10-11: GitHub Pages enabled (main, root), pages live under https://data4thepeople.github.io/spr-exchange/dist/. Eric: move to 2a after the independent tie-out finishes and its edits are worked through.
- 2026-10-11: independent tie-out back. No difference in any published number; ledger 31/31, rfp_terms 25/25, rounds 6/6, EIA and futures row for row. Fixed: cent rounding ties in two trade CSVs, DATASETS.md statements, 'three of the six rounds', 'agreed to lend', receipt-rate sources. Open for Eric: 'Maximum profit' and 'ideal time' wording.
- 2026-10-11: EIA coverage check done from WPSR Appendix A (footnote on what SPR stocks include; weekly vs monthly gap 0.9M for June 2026).
- 2026-10-11: Eric accepted tie-out edits 1 to 3 (estimated profit wording, lower-or-higher fine print, closer-to-pickup line on the June card) and confirmed step 1. Step 2a open; waiting on the slug and Eric's draft.
- 2026-10-11: slug set to spr-exchange; posts/spr-exchange/POST.md created from the template. Waiting on Eric's draft.
- 2026-10-11: Eric's draft placed in POST.md verbatim; brackets resolved (SPR chart image from the inventory tool, history, three-viz walk-through, two risks, teaser, limits). Proposed edits to his prose sent as a numbered list; none applied.
- 2026-10-11: Eric accepted opening edits 1-4, the closing with changes 1 and 2, tie-back items 3-5 and the refiner paragraph; all applied to POST.md.
- 2026-10-11: Eric's own edits to POST.md reviewed; nine rewordings proposed and all accepted, applied.
- 2026-10-11: title set to 'Meet the Speculative Petroleum Reserve'; renaming callouts added to the intro and the closing at Eric's instruction.
- 2026-10-11: Eric confirmed step 2a. Step 2b open.
- 2026-10-11: 2b look-over done; items 2-7 applied and a sourced sentence on the conflict and the IEA release added to the history section.
- 2026-10-11: Eric's second round of edits reviewed; 16 proposed edits all accepted and applied, plus the bank guarantee sentence. Tanker figure confirmed against the VLCC project (Baltic TD3C, Oct 9).
- 2026-10-11: links added to the inventory tool and the supertanker post (both checked, both load).
- 2026-10-11: Eric confirmed step 2b. Step 2c open. Carried forward for Eric to check before publishing: IEA release and Bloomberg link not opened by Claude; 1975 founding and four sites, the 180-million-barrel 2022 sale, DOE's 'about 25%' average and the 'stabilize GLOBAL oil supply' wording come from sources not saved; Alon USA as a small refiner is Claude's labeling.
- 2026-10-11: 2c markup checked with the importer, convert-only: 30 slices, 3 full-width embeds, 1 image, 1 divider. No fences added; no embed is followed directly by a heading.
- 2026-10-11: Eric confirmed step 2c. Step 2d open.
- 2026-10-11: hero-prompt.md written, three variants from Eric's auction-barrel idea. Waiting on the generated image.
