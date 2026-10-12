# Status

Project: SPR_explainer
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: (slug not set) post 2, the 2021-22 exchange compared with 2026
Step: 1
Since: 2026-10-12

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

- 2026-10-12 Post 2 opened. Topic: how the 2021 and 2022 SPR loans worked and how they compare with the 2026 exchange, promised at the end of the first post ("Tomorrow we will look at how the 2021 and 2022 loans worked, and how they compare with this year's"). The first post's record is in STATUS-spr-exchange.md. DATASETS.md carries over; it already holds the FY22 Winter Exchange RFP set and notes on later contract changes from secondary sources.
- 2026-10-12 Carried in from post 1: (a) Eric wants the dollar-fixed bank guarantee looked at as a possible difference between 2022 and 2026, not yet compared; (b) the 2021-22 premium was fixed, 2.3% to 9.1%, not bid; (c) return dates on the 2021-22 loans were pushed back, known only from Argus reporting; (d) the weekly award-sheet check writes its log line to this file.
- 2026-10-12 Step 1 research: the 2022 release was seven emergency sales, not loans (Eric's recollection was right). DOE posts every award. Plan approved by Eric: compare the 2022 sales with the 2026 loans; the December 2021 loan becomes a short section.
- 2026-10-12 Step 1 build: scripts/fetch_doe_sales.py (28 DOE files), scripts/build_sales_2022.py (300 contracts, 16 buyers, 180,660,000 barrels, ties to every stated total), 11 names added to company_map.csv with a new type for Equinor and Unipec, data/reference/sales_2022.csv and program_comparison.csv, dist/compare.html. Own tie-out extended: all checks pass. Bank guarantee is the same rule in the 2021 loan and 2026, so it is not a difference between them.
- 2026-10-12 Independent tie-out (fresh agent, own downloads and code): every number on dist/compare.html matched DOE's documents. Its findings on wording and display were applied: barrels shown to three decimals; "starting point" rows rewritten because the 2022 reference price is not a floor (winning offers came in below it); export row made parallel for both years; June no longer called the lowest minimum; return date given as a month; the two rows that are our own reading are labeled; group renamed "oil companies with no U.S. refinery"; sweet reference price added for the first sale. Open for Eric: the firm-type rule moves the headline shares, see the log of sensitivities in DATASETS.md.
- 2026-10-12 Eric: "this is the big story", asked why refiners got the oil in 2022 and not in 2026, whether the government steered it, or whether refiners did not need it. Findings so far: no rule in the 2022 notices favors refiners ("the sale will be by price competition"); DOE's Offeror Abstract Reports show every 2022 bid (scripts/build_bids_2022.py): trading houses did bid but were priced below the winners; Trafigura did not bid in 2022; refineries ran harder in 2026 than in 2022 by EIA data. DOE has posted no bids for 2026. These new figures still need my tie-out checks and an independent tie-out.
