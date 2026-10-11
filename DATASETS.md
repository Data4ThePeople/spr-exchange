# Datasets

One section per dataset, written before any analysis, updated whenever we learn
something new. The point is to know the traps before they show up in a chart.

Retrieval date for everything below: October 10, 2026, unless noted.

## SPR exchange award sheets (U.S. Department of Energy)

**What it is.** One short PDF per round of the 2026 emergency exchange. Each
lists the RFP number, an "as of" date, a stated total, and one line per
contract: a company name and a barrel count. Nothing else.

**Where it comes from.** `https://www.spr.doe.gov/posting/EXCHANGE/archive/<release>/1-Request for Proposal/<release> Award Information.pdf`.
Five files in `data/raw/doe_awards/`, supplied by Eric and confirmed
byte-identical to DOE's archive copies. DOE's folder listing is a JSON feed at
`.../posting/EXCHANGE/archive/` (closed rounds) and `.../posting/EXCHANGE/current/`
(open rounds); snapshots are in `data/raw/doe_rfps/`.

**Version and vintage.** Rounds 1, 1.a, 1.b, 2 and 3, dated March 20, April 10,
April 17, May 11 and June 22, 2026. DOE moves a round from `current/` to
`archive/` after it closes, which changes the URL. Round 4 (RFP issued
September 29, bids due October 6) had no award sheet posted as of October 10.

**Coverage.** Every contract DOE announced: 31 contracts, 13 firms,
133,560,000 barrels. All values are DOE's own figures; nothing is estimated.

**Changes over time.** Company names are not spelled the same way from sheet to
sheet ("Marathon Petroleum Company LP" and "Marathon Petroleum Company";
"Vitol Inc." and "Vitol"; "Phillips 66 Company" and "Phillips 66"; with and
without "LLC"). We merge these in `data/reference/company_map.csv` and keep
DOE's spelling in `company_as_listed`. The sheets do not say whether different
spellings are different legal entities.

**Suppressed, censored or masked values.** The sheets leave out everything
about the deal except the name and volume: site, crude stream, delivery month,
premium bid, and return period are not published per contract.

**Missing data.** None within the sheets. "As of" wording means a sheet could
be reissued; we have seen no reissue.

**Revisions.** Not revised so far. We pin the PDFs in the repo.

**Units and rounding.** Barrels, to the nearest 5,000 in practice. These are
awarded volumes, not delivered volumes. Delivered volumes can differ.

**Known quirks.** Round 3 awarded 500,000 barrels although the RFP set a
3,000,000-barrel minimum offer; the RFP is "negotiated," so DOE can agree other
terms. The firm type is ours, not DOE's (see "Firm types" below).

**Uncertainty.** None stated. The gap between awarded and delivered is unknown
per contract; the weekly SPR level is the only public check (see EIA below).

**License and attribution.** U.S. government work, public domain. Credit: U.S.
Department of Energy, Strategic Petroleum Reserve Project Management Office.

### Firm types (our classification)

| Type | Rule | Firms |
|---|---|---|
| Trading house | Main business is commodity trading; no U.S. refinery in the corporate group | Trafigura, Vitol, Gunvor, Mercuria, Macquarie |
| Major trading arm | Trading company inside an oil major that owns at least one U.S. refinery | Shell Trading (US), Atlantic Trading & Marketing (TotalEnergies) |
| Refiner | The listed entity is a refining company | Marathon, ExxonMobil, BP Products North America, Phillips 66, Alon USA |
| Midstream | Pipeline company's marketing arm | Energy Transfer Crude Marketing |

The brief counted Atlantic Trading & Marketing as a trader and Shell Trading as
a major's trading arm. Both are trading arms of majors with a Gulf Coast
refinery (TotalEnergies at Port Arthur, Shell at Norco), so the same rule puts
them in the same group. The tool lets the reader count that group either way.
Still to confirm from a primary source: the TotalEnergies ownership of Atlantic
Trading & Marketing (so far supported by TotalEnergies' own job postings, which
name ATMI as one of its Houston trading entities), and the current refinery
holdings named in the parent notes.

## SPR exchange requests for proposals (U.S. Department of Energy)

**What it is.** The solicitation for each round: about 150 pages of contract
terms, plus amendments and question-and-answer sheets. This is where the
per-round terms live: sites, crude streams, delivery months, minimum premiums,
return windows, and the title clause.

**Where it comes from.** Same DOE folders as the award sheets. 24 PDFs in
`data/raw/doe_rfps/` with URLs and SHA-256 hashes in `manifest.json`. Spreadsheet
exhibits (offer form, contract template) were not downloaded.

**Version and vintage.** RFPs DE-RP96-26PO00001 through 00006. Round 1 has three
amendments; round 2 has one, which moved 3 million barrels from Bryan Mound
sweet (August) to Bryan Mound sour (July). `data/reference/rfp_terms.csv` uses
the amended round 2 table.

**Coverage.** All six rounds. The premium tables are images of spreadsheets in
the PDFs; we keyed them by hand into `data/reference/rfp_terms.csv` with the
page each came from. They need a second read against the PDFs in the tie-out.

**Changes over time.** The premium design changed. Round 1 set a minimum
premium per site and one return window. From round 1.a on, DOE added a schedule
of extra premium for choosing a later return period. Minimum premiums ran 17%
to 24% in rounds 1 through 2, then 8% to 9% in round 3 and 7% to 9.5% in
round 4. Minimum offer size rose from 1 million to 3 million barrels at round 2.

**Suppressed, censored or masked values.** The premium each winner actually
bid (minimum plus the bidder's "additional premium" plus the return-period
add-on) is not published. Only DOE's press-release averages are public: about
28% for round 2 (15.1 million premium barrels on 53.3 million), 26% across the
first three rounds (June 10 release), 25% across four (September 29 release).

**Missing data.** Per-contract site, stream, delivery month, return period.

**Revisions.** Amendments are separate PDFs. We hold all that were posted.

**Units and rounding.** Barrels; premiums in percent of net barrels delivered.

**Known quirks.** Title passes to the borrower "at the custody transfer
measurement locations" (Section H.1, identical wording in all six RFPs). The
RFPs contain no clause limiting resale or export. DOE's round 1 Q&A (question
24) says the government generally may not restrict crude exports under 42
U.S.C. 6212a, apart from sanctions and limits on certain Chinese entities.
Domestic vessel moves must meet the Jones Act unless waived. Borrowers pay all
transport costs and must post a letter of credit for 100% of the oil's value.

**Uncertainty.** None stated.

**License and attribution.** U.S. government work, public domain.

## Weekly and monthly petroleum series (U.S. Energy Information Administration)

**What it is.** SPR crude stocks, commercial crude stocks, crude exports and
imports, production, refinery inputs and utilization, distillate stocks, and
WTI and Brent spot prices. Series IDs and descriptions are in
`scripts/fetch_eia.py`.

**Where it comes from.** EIA Open Data API v2, series-id route. Raw JSON per
series in `data/raw/eia/`; tidy table in `data/processed/eia_series.csv`.

**Version and vintage.** Weekly data through the week ending October 2, 2026.
Monthly data through July 2026. Daily spot prices through October 6, 2026.

**Coverage.** Weekly SPR stocks start August 20, 1982, so "lowest since" claims
from the weekly series can reach back only that far; the monthly series starts
October 1977. To do before the tie-out: read the Weekly Petroleum Status Report
methodology and record which weekly series are surveyed and which are
estimated. Weekly exports in particular are an estimate, and the monthly
figure is the one to quote for a finished month.

**Changes over time.** To document from EIA's notes during the coverage check.

**Suppressed, censored or masked values.** None known in these series.

**Missing data.** Null values are dropped by the fetch script; none fall in 2026.

**Revisions.** Weekly values are not revised week to week, but the monthly
series replaces them as the record and is itself revised. We refresh the whole
series on each pull and record the pull date in `data/raw/eia/_retrieved.json`.

**Units and rounding.** Stocks in thousand barrels. Flows in thousand barrels
per day; a weekly flow times 7 gives barrels for the week. Prices in dollars
per barrel.

**Known quirks.** EIA's own NYMEX futures series (RCLC1 to RCLC4) stop on
April 5, 2024, so they cannot supply a 2026 curve. The weekly SPR level fell
132.5 million barrels from March 20 to October 2, 2026, against 133.56 million
awarded; the two are different measures (awarded versus physically moved, and
the level also reflects any returns or other movements).

**Uncertainty.** To record from EIA's methodology during the coverage check.

**License and attribution.** Public domain. https://www.eia.gov/about/copyrights_reuse.php

## WTI and Brent futures by contract month (CME and ICE closes, relayed by Yahoo Finance)

**What it is.** Daily closing price for each dated futures contract: November
2026 through December 2029 for WTI, and the Brent months Yahoo carries.

**Where it comes from.** Yahoo Finance chart endpoint, one request per contract
symbol (for example CLZ26.NYM). Raw JSON in `data/raw/futures/`; tidy table in
`data/processed/futures_closes.csv`.

**Version and vintage.** January 2, 2026 through October 9, 2026.

**Coverage.** Every value is an exchange close as relayed by Yahoo. Nothing is
interpolated by us. Yahoo no longer serves contracts that have expired, so the
April through October 2026 WTI contracts are missing. For those months the
front of the curve has to come from EIA's WTI spot price instead. Several
far-dated Brent months are also not served. Missing symbols are listed in
`data/raw/futures/_retrieved.json`.

**Changes over time.** None in the period.

**Suppressed, censored or masked values.** None.

**Missing data.** See coverage. A missing contract is left missing.

**Revisions.** Not expected. Pinned in the repo.

**Units and rounding.** Dollars per barrel, two decimals.

**Known quirks.** These are not the official CME settlement file, which is not
free. Closes for thinly traded far months can be stale or differ by a few cents
from the official settlement. Any figure built from them should say "closing
prices as relayed by Yahoo Finance." Spot and futures are different things: the
spot price is a physical assessment at Cushing; a futures close is for a
contract month.

**Uncertainty.** Not stated by the source. Treat far-month values as accurate to
roughly the nearest dollar until checked against a CME source.

**License and attribution.** Exchange data relayed by a third party. We publish
derived figures and a few cited values, not the bulk series.

## Tanker freight (Fearnleys and the Baltic Exchange, from the VLCC project)

**What it is.** Two series already assembled for the supertanker-rates post:
Fearnleys' daily assessment for a VLCC from the U.S. Gulf to Thailand, as a lump
sum in millions of dollars per cargo; and the Baltic Exchange weekly TD3C rate
(Middle East Gulf to China) in Worldscale points and dollars per day.

**Where it comes from.** Copied from `../VLCC/data/` into `data/raw/freight/`.
Fetch scripts and notes live in the VLCC project (`scripts/fetch_fearnleys.py`,
`research/NOTES.md`).

**Version and vintage.** Fearnleys through October 9, 2026. Baltic through the
week 41 report (October 9, 2026).

**Coverage.** Fearnleys U.S. Gulf series: daily from August 2019. Baltic TD3C:
weekly from December 2020.

**Known quirks.** Only the Fearnleys series is a U.S. Gulf export route, and it
is to Asia on a 2-million-barrel ship. The Baltic series we hold is a Middle
East route; it shows the freight market's direction but is not the cost of
moving SPR crude. We hold no U.S. Gulf to Europe rate (Baltic TD25), and most
reported SPR exports went to Europe on smaller ships. A lump sum divided by
about 1.98 million barrels gives dollars per barrel before war-risk insurance.

**Uncertainty.** Broker assessments, not transaction records.

**License and attribution.** Credit Fearnleys and the Baltic Exchange. Publish
derived per-barrel figures and cited values, not the series.

## SPR export counts (Kpler, as reported by news outlets)

**What it is.** Ship-tracking estimates of how much SPR crude left the country.
We do not hold the data, only published figures.

**Coverage.** Scattered points in time: about 13 million barrels by mid-May
(Bloomberg, May 14), about one third of 58 million by end of May. A later
secondary report says "roughly half" of released barrels were exported; we have
not found the primary Kpler source for it. Argus (April 23) reported about 26
million barrels to four trading firms being offered into Europe. No full-period
public count exists.

**Known quirks.** Crude is fungible. A tracker can follow a cargo loaded at an
SPR-connected dock, but a barrel refined at home can free another barrel for
export. Any full-period figure in the post is ours and labeled as ours.

**License and attribution.** Cite the outlet and Kpler. Each figure needs its
original article located and read before it is used.

## Worked trade example (`scripts/trade_math.py`)

- **What it is:** a per-barrel estimate of the borrow, sell and hedge trade for one round. Run as `scripts/trade_math.py <round>` for rounds 1.a, 1.b, 2, 3 or 4. Output: `data/processed/trade_example_round_<round>.csv`, one row per pricing date, lot and return window.
- **Method:** barrels owed are 1 plus the RFP minimum premium plus the return window's add-on (`data/reference/rfp_terms.csv`). Return price is the mean WTI futures close for the contract months in the window. Gross margin per barrel borrowed = sale price - barrels owed x return price. The break-even premium is sale price / return price - 1. Computed on the bid due date and on the award date.
- **Two sale prices:** (1) the front-month WTI futures close (`data/raw/futures/CL=F.json`, Yahoo continuous contract), which is the highest price on the curve when near prices sit above later ones; (2) the contract for the month after the lot's delivery month, which is closer to what oil lifted that month sells for. Yahoo does not serve the April to October 2026 contracts, so (2) is blank for rounds 1 to 3.
- **Limits:** the premium each firm bid is not public, so the minimum is used and the result is a ceiling. Not included: the grade's gap to WTI (most lots are sour crude), pipeline and shipping, the letter of credit, interest on the sale proceeds. When or whether any firm hedged is not known. Where a far contract month is missing (September and October 2029), the window uses the months that are served.

## Trade explainer page (`scripts/build_trade_page.py` -> `dist/trade.html`)

- One example per round (1.b, 3, 4): the lot and return window with the largest gross margin on the bid due date in `trade_example_round_<round>.csv`, at the minimum premium. Sale price is the contract for the month after pickup where held (round 4), else the front-month close (rounds 1.b and 3).
- "Barrels taken" comes from the award ledger; a round with no award sheet shows as pending. Set `SHOW_PENDING_MATH = False` in the build script to leave that card empty.
