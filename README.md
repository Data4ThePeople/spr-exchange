# The Strategic Petroleum Reserve: the 2026 exchange and the 2022 sales

Data and code behind two Data 4 The People posts on the U.S. Strategic Petroleum Reserve (SPR). The first shows how the 2026 emergency exchange works: who borrowed the oil, how a borrower could lock in a margin with futures, and when the oil is due back. The second compares the 2022 emergency sales with the 2026 loans: who got the oil each time, and where the money from the 2022 sales went.

## Live links

- Posts:
  - [Meet the Speculative Petroleum Reserve](https://www.data4thepeople.com/p/spr-exchange)
  - [Sell It or Lend It? With Our Emergency Oil, the Devil Is in the Details](https://www.data4thepeople.com/p/spr-sale-vs-loan)
- GitHub Pages: https://data4thepeople.github.io/spr-exchange/
  - [Who took the barrels](https://data4thepeople.github.io/spr-exchange/dist/ledger.html) (`dist/ledger.html`)
  - [How borrowing oil can make money](https://data4thepeople.github.io/spr-exchange/dist/trade.html) (`dist/trade.html`)
  - [When the oil is due back](https://data4thepeople.github.io/spr-exchange/dist/returns.html) (`dist/returns.html`)
  - [2022 sales vs. 2026 loans](https://data4thepeople.github.io/spr-exchange/dist/compare.html) (`dist/compare.html`, embeddable one part at a time with `?part=who`, `terms` or `bids`)
  - [Where the 2022 sale money went](https://data4thepeople.github.io/spr-exchange/dist/proceeds.html) (`dist/proceeds.html`)

## What's here

- `posts/<slug>/POST.md`: the text of each post, with its images in `images/`.
- `dist/`: the built charts. Each page is self-contained, with its data inlined and no outside scripts.
- `scripts/`: fetch, build and check scripts (listed below), plus the HTML templates for each page.
- `data/raw/`: source files as downloaded, with `manifest.json` files (URL, size, SHA-256) where the script writes them.
- `data/reference/`: tables keyed by hand from source documents, such as RFP terms, round dates, company name merges and firm types.
- `data/processed/`: tidy tables and JSON built by the scripts.
- `DATASETS.md`: one section per dataset (source, vintage, coverage, quirks and limits), and a table tracing each number in the second post to its source.
- `requirements.txt`: Python packages.

## Data sources

| Agency or source | Dataset | Where it lives |
|---|---|---|
| U.S. Department of Energy, SPR office | 2026 emergency exchange award sheets (rounds 1, 1.a, 1.b, 2, 3) | `data/raw/doe_awards/` |
| U.S. Department of Energy | 2026 exchange requests for proposals, amendments and Q&A | `data/raw/doe_rfps/` |
| U.S. Department of Energy | FY22 Winter Exchange RFP set (the 2021-22 loans) | `data/raw/doe_rfps_2022/` |
| U.S. Department of Energy, FOIA reading room | 2021-22 exchange agreements and their modifications | `data/raw/doe_foia_2022/` |
| U.S. Department of Energy | 2022 emergency sales: notices of sale, offer abstracts and award reports | `data/raw/doe_sales_2022/` |
| U.S. Department of Energy | Crude oil purchase award sheets, 2023 to 2025 | `data/raw/doe_purchases/` |
| U.S. Department of Energy | SPR annual reports (2022, 2023) and budget volumes | `data/raw/doe_reports/` |
| U.S. Department of Energy | January 25, 2022 exchange press release | `data/raw/doe_press/` |
| U.S. Energy Information Administration | Weekly and monthly petroleum series (Open Data API v2): SPR and commercial stocks, exports, imports, refinery runs, spot prices | `data/raw/eia/` |
| CME and ICE, as relayed by Yahoo Finance | Daily closes for dated WTI and Brent futures contracts | `data/raw/futures/` |
| Congress and the Office of Management and Budget | Public Law 117-328 passages and Budget Appendix entries for the SPR petroleum account | `data/raw/law/` |
| ETP Crude LLC | Published pipeline tariffs (Texas and FERC) | `data/raw/tariffs/` |
| Fearnleys and the Baltic Exchange | Tanker freight series, copied from the D4TP VLCC project | `data/raw/freight/` |

All U.S. government files are public domain. Futures closes come from a third party and are not the official exchange settlement file. See `DATASETS.md` for retrieval dates and limits.

## How to rebuild

Requirements: Python 3 with the packages in `requirements.txt`. The OCR step (`scripts/ocr_pdf.swift`) needs macOS. Raw files are committed, so the build steps run without fetching.

```sh
pip install -r requirements.txt

# 1. Fetch (optional; refreshes data/raw/)
python3 scripts/fetch_eia.py              # needs EIA_API_KEY
python3 scripts/fetch_futures.py
python3 scripts/fetch_doe_sales.py
python3 scripts/fetch_doe_purchases.py
python3 scripts/fetch_doe_foia_2022.py
python3 scripts/check_awards.py           # downloads any new 2026 award sheet

# 2. Build the ledgers and analysis tables
python3 scripts/build_ledger.py
python3 scripts/trade_math.py 1.b
python3 scripts/trade_math.py 3
python3 scripts/trade_math.py 4
python3 scripts/return_schedule.py
python3 scripts/lot_uptake.py
python3 scripts/build_sales_2022.py
python3 scripts/build_bids_2022.py
python3 scripts/build_exchange_2021_22.py
python3 scripts/build_exchange_mods.py
python3 scripts/build_purchases.py
python3 scripts/sale_proceeds.py
python3 scripts/design_evidence.py

# 3. Build the pages in dist/
python3 scripts/build_ledger_page.py
python3 scripts/build_trade_page.py
python3 scripts/build_returns_page.py
python3 scripts/build_compare_page.py
python3 scripts/build_proceeds_page.py

# 4. Check the published figures by a second path
python3 scripts/tie_out.py
```

API keys and a contact email for the request header (`EIA_API_KEY`, `D4TP_CONTACT_EMAIL`) are read at run time from a private env file outside this repo, through a small loader module (`d4tp_env.py`) that is also not in the repo. Only the fetch scripts and `check_awards.py` need them. The EIA fetch needs a free EIA API key.

To add a new 2026 round: put the award PDF in `data/raw/doe_awards/`, add any new company spelling to `data/reference/company_map.csv`, add the round to `data/reference/rounds.csv`, and rerun the build. `scripts/check_awards_weekly.sh` runs `check_awards.py` on a schedule; it does not rebuild the ledger or pages.

## Method notes

- Firm types (trading house, major trading arm, refiner, midstream, and others added for 2022) are our classification, not DOE's. The rules are in `DATASETS.md`, and company name spellings are merged in `data/reference/company_map.csv`.
- DOE does not publish the premium each 2026 winner bid. The trade math uses the RFP minimum premium plus the return-window add-on, so it shows the most a bidder could have made, not what any firm made. It leaves out crude grade differences, pipeline and shipping costs, the letter of credit and interest.
- Award sheets give barrels per firm per round, not the lot or return window chosen, so the return schedule is shown only as earliest and latest bounds.
- 2022 sale figures are awarded volumes at offered prices. Contract prices were later adjusted by a price index up to delivery, so the money actually received comes from DOE's annual report, not from the award reports.
- Text from scanned 2021-22 contracts was read with macOS text recognition. Terms were keyed by hand, and the build scripts stop if a keyed value is not found in the recognized text.

Data 4 The People
