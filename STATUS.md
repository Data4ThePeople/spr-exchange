# Status

Project: SPR_explainer
Process: ~/.claude/d4tp-process/PROCESS.md

## Current

Post: none yet
Step: 1
Since: 2026-10-10

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

- 2026-10-10 Step 1 opened. Topic: the 2026 SPR exchange. Who took the barrels, why borrowers paid premiums of about 25%, and where the oil went. Deliverables for Step 1: a searchable award ledger tool (dist/ledger.html) and a "why pay a 25% premium" trade simulator (dist/simulator.html). Plan approved by Eric the same day: verify the brief's facts against primary sources first, then build the ledger, then the simulator. Award PDFs from Eric are in data/raw/doe_awards/. The project brief stays local and is not committed.
- 2026-10-10 Verification pass. Award PDFs from Eric are byte-identical to DOE's archive copies; ledger rebuilt from the PDFs by scripts/build_ledger.py matches the brief line for line (31 contracts, 133,560,000 barrels). All six RFPs, amendments and Q&As downloaded to data/raw/doe_rfps/ with a manifest. The September 29 round is RFP DE-RP96-26PO00006 (FY26 Release No. 4); no award sheet posted as of October 10. EIA series pulled (scripts/fetch_eia.py). Dated WTI and Brent futures pulled from Yahoo (scripts/fetch_futures.py); expired 2026 months are not available. Freight copied from the VLCC project. DATASETS.md written.
