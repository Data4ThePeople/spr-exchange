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
- 2026-10-12 Eric: the design finding "is the spine of the post"; tie it all out and validate the reading. Done so far: scripts/design_evidence.py (all evidence figures in one file), price terms quoted from the 2022 notices and 2026 RFPs in DATASETS.md, DOE's January 25, 2022 loan release saved and keyed (Trafigura 3.0M and Macquarie 2.0M of 13.4M), own tie-out extended and passing. Running: an independent tie-out of the evidence figures and a separate adversarial review of the reading.
- 2026-10-12 Comparison page extended at Eric's instruction: price terms side by side, the 2022 bid table, the January 2022 loans. Own tie-out passes. Independent tie-out and adversarial review still running.
- 2026-10-12 Independent tie-out of design_evidence.json (fresh agent, own downloads, EIA pulled again from the API): every figure matched. It found the price comparison was done at the wrong level (line item, not delivery line); redone delivery line by delivery line: trading houses $5.12 below the lowest winner, refiners 26 cents below (was 52 cents above). Also fixed in DATASETS.md: a quotation cut short, a page range, and an overstated line about money terms in the 2026 RFPs.
- 2026-10-12 Adversarial review of the design reading. Verdicts: (1) no rule favored refiners in 2022, supported; (2) "refiners did not need the oil less in 2026", unsupported, because about half the 2026 oil went unclaimed, so refiners took less than was on offer; (3) design as the cause, partly supported, cannot be separated from the pull of higher prices abroad in 2026; (4) the January 2022 round overstates the case: the whole 2021-22 loan program was about 23% trading houses by its reconstruction, and the contracts are public in DOE's FOIA reading room (DATASETS.md corrected). "Lock in the day it bids" is too strong: the award comes days later and round 1.b's margin fell from $15.57 to $2.49 between bid and award. Page wording softened accordingly. Still to do: read the FOIA contract file, Gulf Coast refinery and export data, break-even against uptake by lot.
- 2026-10-12 Side research for Eric, not in the repo: Trafigura's chief executive, its federal lobbying filings (Senate LDA database) and FEC contributions by people listing Trafigura as employer. Raw pulls are in scratch/ (not committed). The 2026 election cycle pull failed on a rate limit.
- 2026-10-12 2021-22 loan contracts read (Eric: "yes start with the contracts"). scripts/fetch_doe_foia_2022.py (31 files, 451 pages), scripts/ocr_pdf.swift (macOS text recognition for the scans), data/reference/exchange_2021_22.csv keyed by hand and checked against the text by scripts/build_exchange_2021_22.py. Result: 13 agreements, 24.42 million barrels, trading houses 20.5% (23.0% of the sour program), refiners 57.1%. The comparison page now shows the whole program in place of the single January 2022 round. Modifications not yet keyed; a first read shows returns moved into 2026, including Trafigura's.
