# Datasets

One section per dataset, written before any analysis, updated whenever we learn
something new. The point is to know the traps before they show up in a chart.

Retrieval date for everything below: October 10, 2026, unless noted. Futures were pulled again on October 11, 2026 (`data/raw/futures/_retrieved.json`).

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
September 29, bids due October 6) had no award sheet posted as of October 12.

**Weekly check.** `scripts/check_awards.py` reads both DOE folder listings and
downloads any award sheet not yet in `data/raw/doe_awards/`; it also reports a
release that is not in `rounds.csv`. `scripts/check_awards_weekly.sh` runs it
every Monday at 10:30 through a launchd job on Eric's Mac
(`org.data4thepeople.spr-awards-weekly`), commits a new sheet, and shows an
alert. It does not rebuild the ledger or the charts.

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
`data/raw/doe_rfps/`. `manifest.json` there lists 29 files with URLs and SHA-256
hashes: these 24 plus the five award sheets held in `data/raw/doe_awards/`. Spreadsheet
exhibits (offer form, contract template) were not downloaded.

**Version and vintage.** RFPs DE-RP96-26PO00001 through 00006. Round 1 has three
amendments; round 2 has one, which moved 3 million barrels from Bryan Mound
sweet (August) to Bryan Mound sour (July). `data/reference/rfp_terms.csv` uses
the amended round 2 table.

**Coverage.** All six rounds. The premium tables sit in the PDFs as pasted spreadsheets
(they do have a text layer); we keyed them by hand into
`data/reference/rfp_terms.csv` with the page each came from. The independent
tie-out of October 11, 2026 re-read all 25 rows and all 6 rows of `rounds.csv`
against the PDFs and found no difference.

**Inconsistencies inside DOE's documents.** Round 3 (RFP 00005): the B.5 table
on page B-6 lists Big Hill at 14,000,000 (August) and 15,000,000 (September);
the B.1 table and two later copies say 11,000,000 and 14,000,000, which add to
the stated 40,000,000 and agree with Q&A question 3. We use 11 and 14 million.
Round 1 (RFP 00001): the Bryan Mound receipt rate carries a footnote of 2
million barrels a month for "Nov-Feb 2027" on pages B-1 and C-1 and "Jan-Feb
2027" on B-5 and B-6.

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

**Missing data.** The fetch script drops null values; the raw files contain none.

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
April through October 2026 WTI contracts are missing. For the near end of the
curve the trade math uses Yahoo's front-month continuous contract (`CL=F`), not
EIA's spot price. The two differ: on April 13, 2026 EIA spot was $100.72 and
`CL=F` closed at $99.08; on June 15, $84.65 and $80.75. Several
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

- **What it is:** a per-barrel estimate of the borrow, sell and hedge trade for one round. Run as `scripts/trade_math.py <round>`. Outputs are built and checked for rounds 1.b, 3 and 4 only. Output: `data/processed/trade_example_round_<round>.csv`, one row per pricing date, lot and return window.
- **Method:** barrels owed are 1 plus the RFP minimum premium plus the return window's add-on (`data/reference/rfp_terms.csv`). Return price is the mean WTI futures close for the contract months in the window. Gross margin per barrel borrowed = sale price - barrels owed x return price. The break-even premium is sale price / return price - 1. Computed on the bid due date and on the award date; a round with no award yet (round 4) is priced on the bid due date and on the latest close held, labeled "latest". Each contract month in a window is the contract whose delivery month is that month. Prices are rounded to the cent with halves rounded up.
- **Two sale prices:** (1) the front-month WTI futures close (`data/raw/futures/CL=F.json`, Yahoo continuous contract), which is the highest price on the curve when near prices sit above later ones; (2) the contract for the month after the lot's delivery month, which is closer to what oil lifted that month sells for. Yahoo does not serve the April to October 2026 contracts, so (2) is blank for rounds 1 to 3.
- **Limits:** the premium each firm bid is not public, so the minimum is used and the result is a ceiling. Not included: the grade's gap to WTI (most lots are sour crude), pipeline and shipping, the letter of credit, interest on the sale proceeds. When or whether any firm hedged is not known. Where a far contract month is missing (September and October 2029), the window uses the months that are served.

## Trade explainer page (`scripts/build_trade_page.py` -> `dist/trade.html`)

- One example per round (1.b, 3, 4): the lot and return window with the largest gross margin on the bid due date in `trade_example_round_<round>.csv`, at the minimum premium. Sale price is the contract for the month after pickup where held (round 4), else the front-month close (rounds 1.b and 3).
- For a front-month example, the card adds a second figure priced with the first dated contract after the pickup month, when we hold one within two months of pickup (round 3 only: November 2026 for a September pickup).
- The profit line is the per-barrel amount times trading-house barrels in the round, priced on the bid due date. It is not a maximum: the same math on other dates gives higher and lower values (the independent tie-out found $25.64 a barrel for round 1.b on April 29, 2026).
- "Barrels taken" comes from the award ledger; a round with no award sheet shows as pending. Set `SHOW_PENDING_MATH = False` in the build script to leave that card empty.

## Transportation costs (`data/reference/transport_costs.csv`, `data/raw/tariffs/`)

- **What we hold:** ETP Crude LLC's published pipeline rates from the Energy Transfer Nederland terminal (custody transfer point for West Hackberry and Big Hill oil) to the Motiva and Total refineries and the Zydeco Pipeline: 20.57 to 31.77 cents a barrel, effective July 1, 2026 (TX No. 14.5.0 and F.E.R.C. No. 12.8.0, PDFs saved). The rate in force in April 2026 was the prior issue; the F.E.R.C. Zydeco rate was 31.32 cents then, as reported in a search summary and not yet read from the PDF.
- **What we do not hold:** terminal, dock and storage fees at Nederland, Freeport or Texas City (private contracts; not found in any public filing), and pipeline rates out of Bryan Mound and Bayou Choctaw. The Texas coastal protection fee is 1.333 cents a barrel when in force; the Comptroller's site says it was suspended as of May 1, 2026 (from a search summary, not yet checked on the page).
- **Use:** quoted in the notes of `dist/trade.html` only. No transportation cost is subtracted from any figure.

## 2021-22 exchange, for comparison (`data/raw/doe_rfps_2022/`)

- **What it is:** DOE's "FY22 Winter Exchange," RFP DE-RP96-22PO00001, up to 32,000,000 barrels of sour crude, proposals due December 6, 2021, deliveries December 16, 2021 to April 2022. RFP, four amendments, Q&A and exhibits from the same DOE archive, with `manifest.json`.
- **Premium terms (RFP pages B-5 and C-1):** fixed by DOE per site and return period, not bid. 2.3% for return July to September 2022; 3.9% for January to February 2023; 5.3% to 6.1% for mid to late 2023; 8.6% to 9.1% for June to September 2024. Awards went first to whoever could take oil soonest, then by volume; a later return period broke ties. The Q&A states "This Exchange uses a fixed premium."
- **Amendments:** none of the four changes the premium table (offer form, email address, letter of credit valuation and terms).
- **Not from primary sources:** Argus reports (read only as search summaries) that DOE later modified contracts to delay returns, including about 15.3 million barrels pushed to 2026, and that contract premiums ran 2.3% to 14.6%. The post-award contract modifications are not on the DOE posting site.

## 2021-22 exchange: later contract changes (secondary sources only)

- **Argus, March 16, 2023, "US delays return of 8mn bl of crude to SPR" (Chris Knight).** Read through a page fetch, not saved. Reports: borrowers took more than 27.4 million barrels between September 2021 and June 2022; original contracts carried an in-kind premium of 2.3% to 14.6% with most oil due back by 2024; DOE revised contracts in February 2022 (ExxonMobil, TotalEnergies, 3.5 million barrels), August 2022 (Chevron, 939,000 barrels, delayed more than a year), four others in 2022 (nearly 4.5 million barrels), and March 2023 (Shell, 3.6 million barrels, to July-August 2025). Argus says it obtained nearly two dozen contracts and modifications through public records requests. No added premium for the delays is mentioned.
- **Argus, May 9, 2024, "US delays return of SPR crude until 2026" (Chris Knight).** Reports at least nine contract modifications signed March 26 to April 16, 2024, with ExxonMobil, Shell and others, delaying about 15.3 million barrels to July-October 2026. DOE's stated reason: to buy oil directly "at a good price for taxpayers" during "stable crude oil market windows." Obtained through a Freedom of Information Act request.
- **Primary documents:** corrected October 12, 2026. The contracts and 30 modifications are public in DOE's FOIA reading room and are now held in `data/raw/doe_foia_2022/`. See the section "2021-22 loan agreements" below. An earlier version of this note said they were not public; the adversarial review found them.
- **Open lead, unverified:** EIA weekly SPR stocks show no weekly increase from March 20 to October 2, 2026, and the total decline (132.46 million barrels) is within 1.1 million of the 133.56 million awarded in 2026. If 15.3 million barrels were returned in July-October 2026, it does not show in the net figures. Returns may have been delayed again, made earlier, or offset by deliveries; the weekly series is net and cannot say which.

## Return schedule bounds (`scripts/return_schedule.py` -> `data/processed/return_schedule.csv`, `dist/returns.html`)

- **What it is:** the earliest and latest dates the RFP return windows allow for the 133,560,000 barrels awarded in rounds 1 to 3. Premium barrels are not counted. Round 4 is not included until DOE posts awards.
- **Why bounds:** award sheets give barrels per firm per round, not the lot (site and pickup month) or the return window chosen.
- **Method:** within each round, awarded barrels are placed lot by lot up to each lot's offered volume (`rfp_terms.csv`). "Earliest" fills the lots whose first window opens soonest and returns the oil the day that window opens. "Latest" fills the lots whose last window closes latest and returns the oil the day that window closes. Round 1 windows use the exact days in the RFP; other rounds use the first and last day of the window months.
- **Limits:** the earliest line ignores DOE's monthly receipt rate at each site, so it is faster than the sites could take oil back. It also starts September 1, 2026, and EIA weekly stocks show no net increase through October 2, 2026. Neither line reflects any later change to return dates.
- **Receipt rates:** `data/reference/site_receipt_rates.csv` holds the nominal monthly rate at which each site can take oil back, from the Section B.1 tables of the RFPs (Bryan Mound 3.0M, West Hackberry 3.3M, Big Hill 3.0M, Bayou Choctaw 1.2M; 10.5M combined). The page uses the sum to say the earliest line is not physically possible. The RFPs add that capacity "may be lower than the table due to previous SPR tenders."

## EIA weekly SPR stocks: coverage check (October 11, 2026)

- **Read:** EIA Weekly Petroleum Status Report, Appendix A, Table A1 (saved as `data/raw/eia_docs/wpsr_appendix_a_2026-10-11.pdf`).
- **What the figure includes:** footnote 3 says "Crude oil stocks in the SPR include non-U.S. stocks held under foreign or commercial storage agreements." So the weekly level counts oil physically stored at the sites, including any held there for others. The appendix does not say that oil owed to the reserve under an exchange is counted, and a loaned barrel leaves the level when it is delivered.
- **Weekly against monthly:** the same table compares weekly-derived and monthly survey figures. For June 2026 the SPR was 321.3 million barrels from weekly data and 322.2 million in the monthly survey, a gap of 0.9 million.
- **Revisions:** a re-pull of the weekly series on October 11, 2026 matched the October 10 pull for all 2,297 weeks.
- **Not read:** the report's explanatory notes on reporting day and survey form. The weekly period label is taken as the week-ending Friday, as EIA's series labels state.

## Background facts in the post from outside sources (not saved as files)

- **Start of the 2026 disruption and the coordinated release:** International Energy Agency news release, "IEA Member countries to carry out largest ever oil stock release amid market disruptions from Middle East conflict" (iea.org). As summarized by search on October 11, 2026: the conflict began February 28, 2026 and impeded flows through the Strait of Hormuz; on March 11 the 32 member countries agreed to make 400 million barrels available. Read as a search summary, not the page itself.
- **U.S. share of 172 million barrels:** DOE press release titles ("...172 Million Barrel Strategic Petroleum Reserve Exchange"), energy.gov.
- **Supertanker rates ($30,000 to $1.4 million a day):** Baltic Exchange weekly tanker reports, route TD3C (Middle East Gulf to China), time-charter equivalent, as collected in the D4TP VLCC project (`github.com/Data4ThePeople/VLCC`, `data/baltic_td3c_weekly.csv`). Week 41 report, October 9, 2026: $1,412,594 a day. "Normal $30,000" is Eric's rounding; the median weekly value in that file from December 2020 through February 27, 2026 is $31,477. Read from that project's file on October 11, 2026, not pulled again here.
- **Front-month WTI closes in the closing section:** $68.55 on July 6, 2026 (lowest close since March 20) and $91.85 on October 9, from `data/raw/futures/CL=F.json`. The close the day before the conflict, February 27, was $67.02.
- **Trafigura and gas stations:** Trafigura's Puma Energy unit bought retail station networks in Puerto Rico in 2011 and 2012, per Trafigura press releases. Current ownership not checked. The post says "Trafigura-branded" for that reason.

## 2022 emergency sales: award reports and notices of sale (U.S. Department of Energy)

**What it is.** For each of the seven emergency crude oil sales of 2022, DOE
posts a Notice of Sale and three reports from its "Sales Offer Evaluation
Program": Offeror Abstract, Apparently Successful Offers, and Successful
Awards. The Successful Awards Report has one page per contract: the buyer, a
contract number, and one line per delivery line item with the unit price
offered, the barrels awarded (in thousands) and the total price.

**Where it comes from.** DOE's folder listing is a JSON feed at
`https://www.spr.doe.gov/posting/SALE/archive/`. `scripts/fetch_doe_sales.py`
downloads everything in the `1-Reports` folder of sale folders 12 to 18
("12-FY22 Emergency Drawdown" to "18-FY23 Emergency Drawdown No. 3D") into
`data/raw/doe_sales_2022/`: 28 PDFs, with `manifest.json` (URL, bytes,
SHA-256) and a dated copy of the listing. Retrieved October 12, 2026.

**Version and vintage.** Award reports are dated March 16, April 21, June 9,
July 10, August 11, October 6 and November 3, 2022 ("RUN DATE" on the report,
which is when DOE ran the report, not a signing date). DOE's listing shows the
files as posted June 26, 2023.

**Coverage.** 300 contracts, 16 buyers, 180,660,000 barrels,
$18,834,706,087 at the prices offered (an average of $104.25 a barrel). The
notices offered 190,100,000 barrels in all. Not included: the sales Congress
ordered by law (DOE folders 10, 11 and 19, "Mandatory Sale"), and oil lent
rather than sold (the December 2021 "FY22 Winter Exchange").

**How it is processed.** `scripts/build_sales_2022.py` reads the seven
Successful Awards Reports into `data/processed/spr_2022_sale_awards.csv`, one
row per line item. The build stops unless every line's price times barrels
equals its total to within one dollar (13 lines differ by 50 cents; DOE rounds some down and some up), every master line item adds to its stated sub-total, and
every contract adds to its "TOTAL OFFER AWARD" line. Buyer names are kept as
DOE printed them; `data/reference/company_map.csv` gives the merged name and
firm type, the same file the 2026 ledger uses.

**Changes over time.** Names vary from 2026 ("Marathon Petroleum Supply and
Trading LLC" in 2022, "Marathon Petroleum Company LP" in 2026; "BP Oil Suppply
a Division of BPPNA", DOE's spelling, and "BP Products North America"). We
merge these under one company name. They may be different legal entities
inside the same group.

**Suppressed, censored or masked values.** None in the award reports. The
reports give a master line item number and a delivery line letter, not the site
or crude stream in words; those are in each notice's Attachment A and are not
used here.

**Missing data.** None found. The line items add to every stated total.

**Revisions.** Each report is marked "V.1". We pin the PDFs in the repo.

**Units and rounding.** Barrels in thousands on the reports, shown here in
barrels. Prices to four decimals. Dollars are unit price times barrels at the
price offered. The contracts adjust that price by an index up to delivery
(Notice of Sale, price adjustment provision), and deliveries can vary by 10%,
so the dollar figures are not cash received.

**Known quirks.** The "MAXQ" column is sometimes blank, and continuation lines
drop the offer and line item numbers; the parser handles both. Awards are not
deliveries, and DOE does not post later contract changes.

**Uncertainty.** None stated by DOE. The gap between awarded and delivered
volumes is not published per contract.

**License and attribution.** U.S. government work, public domain. Credit: U.S.
Department of Energy, Strategic Petroleum Reserve Project Management Office.

### Terms read from the notices (`data/reference/sales_2022.csv`, `program_comparison.csv`)

- **Offered volume per sale:** the sentence "The intent of this sale is to award up to ..." on page 3 of each notice: 30.0, 30.0, 40.1, 45, 20.0, 10.0 and 15 million barrels.
- **Reference price:** "the BRP is $..." in each notice. The base reference price is the average of daily index prices over the five trading days ending two trading days before the notice. Sour crude: $83.856 to $114.208 across the six notices that offered sour oil.
- **How offers are ranked:** "Award on each DLI will be made to the responsible offerors that submit the highest priced offers" (amendment to Standard Sales Provision B.22).
- **Exports:** each notice removes Standard Sales Provision B.6, "Export Limitations and Licensing," and tells offerors to comply with U.S. export laws.
- **2026 side of the table:** from the 2026 RFPs and `data/reference/rounds.csv`, as documented above. "Oil offered" for 2026 adds the five rounds with results (258.5 million barrels). That is more than the 172 million barrels the U.S. committed, so some oil was probably offered more than once; the documents do not say. The page says so and gives no percentage for 2026.

### Firm types added for 2022

| Type | Rule | Firms added |
|---|---|---|
| Refiner | The company, or its parent, refines crude oil in the U.S. | Valero, Motiva (owned by Saudi Aramco), Chevron |
| Trading house | Main business is commodity trading; no U.S. refinery in the group | Glencore |
| Foreign oil company trading arm | U.S. trading company of an oil company based abroad with no U.S. refinery | Equinor Marketing & Trading (Norway), Unipec America (Sinopec, China) |

**How much the shares depend on the labels (from the independent tie-out, October 12, 2026).**

| Reading of the rules | Trading houses 2022 | Trading houses 2026 | Refiners 2022 | Refiners 2026 |
|---|---|---|---|---|
| As published | 5.5% | 45.0% | 77.4% | 38.3% |
| Equinor and Unipec counted as trading houses | 12.8% | 45.0% | 77.4% | 38.3% |
| Majors' trading arms (Shell Trading, Atlantic Trading & Marketing) counted as refiners | 5.5% | 45.0% | 87.2% | 53.1% |
| Majors' trading arms counted as trading houses | 15.3% | 59.8% | 77.4% | 38.3% |
| Macquarie (a financial group) not counted as a trading house | 3.1% | 36.7% | 77.4% | 38.3% |

Marathon, Valero and BP appear in 2022 through supply and trading units
("Marathon Petroleum Supply and Trading LLC", "Valero Marketing and Supply
Company", "BP Oil Suppply a Division of BPPNA"). We count them as refiners
because the group's business is U.S. refining. Those three took 90,920,000
barrels, 50.3% of the 2022 oil; a reader who counts only the entity named would
get a much lower refiner share. The most stable cut is by corporate group:
groups with no U.S. refinery (trading houses, the Equinor and Unipec group, and
the pipeline company) took 12.8% in 2022 and 46.9% in 2026.

The new group is a judgment call. Equinor and Unipec are not trading houses
(their parents produce or refine oil) and do not meet the "major trading arm"
rule (no U.S. refinery). Together they took 7.3% of the 2022 oil. Counted with
trading houses, that group would be 12.8% in 2022 instead of 5.5%. Parent
ownership and refinery holdings in the notes column are from general knowledge
and have not been checked against a primary source.

## Comparison page (`scripts/build_compare_page.py` -> `dist/compare.html`)

- **What it is:** who got the oil in the 2022 emergency sales and the 2026 emergency loans, by firm type and by company, with a feature table of how the two programs work.
- **Inputs:** `spr_2022_sale_awards.csv`, `spr_2026_exchange_awards.csv`, `sales_2022.csv`, `rounds.csv`, `program_comparison.csv`. Numbers in the feature table are slots filled from the data at build time.
- **Shares** are barrels awarded to the group divided by all barrels awarded in that program.
- **Added October 12, 2026:** three sections fed by `design_evidence.json`: what a winner paid in 2022 and owes in 2026 (with the two contract quotations), who bid in the 2022 sales, and the January 2022 loans beside the two programs. The page states that the sale-against-loan explanation is D4TP's reading and that the bids and the January loans fit it without proving it.
- **Limits:** a sale and a loan are different deals; the page compares who received oil, not what they paid. The years differ in price, in the cause of the shortage and in refinery demand, so the page does not say the program design caused the change.
- **Bank guarantee:** not a difference between the December 2021 loan and the 2026 loans. Both require a letter of credit equal to 100% of the oil's value at award (2021 RFP p. 157; 2026 Release No. 4 RFP p. 149).

## 2022 offers, winners and losers (`scripts/build_bids_2022.py` -> `data/processed/spr_2022_sale_offers.csv`)

- **What it is:** every offer filed in the seven 2022 emergency sales, from DOE's "Offeror Abstract Report" for each sale (in `data/raw/doe_sales_2022/`). One page per offer; one row here per offer and master line item (MLI): 583 offers, 777 lines, 20 bidders.
- **Barrels bid** is the report's "MAXQ" for that MLI, or the largest quantity asked for when MAXQ is blank. A company often files several offers for the same oil at different prices, so barrels bid (433,695,000) overstate what bidders wanted. Use it to see who showed up and how often they won.
- **Awarded** is matched from the award ledger on sale, offer number and MLI. The build stops unless every awarded barrel matches an offer; all 180,660,000 do. One line shows more awarded than bid only because its MAXQ is blank and it asked for oil on three delivery lines (Shell Trading, sale No. 3B); summing those instead of taking the largest would raise total barrels bid by 1.2%.
- **Price comparison:** done delivery line by delivery line, because DOE ranked offers that way ("Award on each DLI will be made to the responsible offerors that submit the highest priced offers"). `spr_2022_sale_offer_choices.csv` has one row per offer, MLI and delivery line item (DLI), with its own price and the barrels asked for on that DLI (830 rows). For each sale, MLI and DLI, the lowest winning unit price comes from the award ledger; each choice's price is compared with it, weighted by barrels asked. Choices on a DLI that nobody won (4,925,000 barrels asked) are left out. An earlier version compared each offer's best price with the lowest winner anywhere on the MLI, which set ship bids against pipeline winners; the independent tie-out of October 12, 2026 caught it.
- **Four bidders that won nothing** were added to `company_map.csv`: Monroe Energy (refiner), PetroChina International (America) (foreign oil company trading arm), and Upstream Petroleum and Biomass Energy Services ("Not classified"; business not identified).
- **No 2026 equivalent.** DOE has posted no report of offers for the 2026 exchange, only the one-page award sheets. Who bid and lost in 2026, and at what premium, is not public.
- **Context from EIA weekly data already held (`eia_series.csv`):** refinery utilization averaged 92.1% in March to November 2022 and 94.4% from March 20 to October 2, 2026; refiner crude inputs 16.03 and 16.83 million barrels a day; crude exports 3.65 and 4.28 million barrels a day. Not yet tied out by a second path.

## Evidence on why the two programs drew different companies (`scripts/design_evidence.py` -> `data/processed/design_evidence.json`)

Every figure below is computed by the script; none is typed in.

- **Who bid in 2022 (`bids_2022`).** From `spr_2022_sale_offers.csv`. For each firm type: number of bidders, barrels bid (the "MAXQ" of each offer line, see the section above for why this overstates demand), share of all barrels bid, barrels won, and barrels won as a percentage of barrels bid.
- **Price against the lowest winner.** For each sale, master line item (MLI) and delivery line item (DLI), the lowest winning unit price is the minimum `unit_price` among that DLI's rows in the award ledger. For each delivery choice in `spr_2022_sale_offer_choices.csv` on a DLI that had a winner, the gap is its price minus that lowest winning price. The figure by firm type is the average gap weighted by barrels asked; the second figure is the share of barrels asked on choices whose gap is below zero. The file also names the company with the lowest and the highest average gap in each type, because a few companies drive the group figures (Vitol for trading houses). Laddered offers (one company, the same oil, several prices) pull every group's average down; taking only each company's best bid per sale and MLI, the independent tie-out got refiners $1.13 above and trading houses $2.77 below.
- **Uptake in 2026 (`uptake_2026`).** Barrels offered (`rounds.csv`) and awarded (the ledger) in each 2026 round with results.
- **Winning offers against the reference price (`paf_2022`).** Each MLI's site and crude type (sweet or sour) is read from Attachment A of the Notice of Sale (written to `spr_2022_sale_streams.csv`). The gap is the awarded line's unit price minus that sale's base reference price for that crude type (`sales_2022.csv`). Reported: the barrel-weighted mean, the lowest and highest gap, the share of awarded barrels with a gap of $5 or less in either direction, and the share of awarded barrels delivered by pipeline.
- **Companies in one program and not the other (`firms`).** Merged company names from `company_map.csv`: 2026 borrowers that filed no offer in any 2022 sale, and 2022 buyers with no 2026 award.
- **The loans of January 25, 2022 (`loan_jan_2022`).** Seven awards totaling 13.4 million barrels, hand-keyed in `data/reference/exchange_jan_2022.csv` from DOE's release "DOE Awards 13.4 Million Barrels From Strategic Petroleum Reserve Exchange to Bolster Fuel Supply Chain" (energy.gov; a copy with its SHA-256 is in `data/raw/doe_press/`). These were made under the December 2021 "FY22 Winter Exchange" RFP, which had a fixed premium and awarded by earliest delivery. DOE's release does not list the five earlier loans under that RFP, so this is one round of that program, not all of it.
- **Market backdrop (`market`).** From `eia_series.csv`: the mean of weekly U.S. refinery utilization, refiner net crude inputs and crude exports over March 1 to November 30, 2022 and over March 20 to October 2, 2026; and the daily front-month WTI futures price over the fourth-month price, as a percentage (EIA series RCLC1 and RCLC4, which EIA stopped updating in April 2024, so there is no 2026 figure from this source).

### What the documents say about price (the basis for the "design" reading)

- **2022 sale:** "The unit price for crude oil under the contract shall be the Delivery Reference Price (DRP) adjusted by the Price Adjustment Factor (PAF) as provided in this provision, subject to any additional adjustments provided for elsewhere in the contract." The DRP is "the average ... of the Daily Index Prices for the five trading days surrounding the delivery 'price date'"; the index is Argus's Mars (sour) or WTI Houston (sweet) month-1 price. "The PAF is the purchaser's offered price minus the Base Reference Price (BRP). The PAF may be either positive or negative." (Notice of Sale, Contract Price Adjustment provision, with two worked examples; PDF pages 16 to 20 depending on the notice.) So a buyer pays the market price around the day it takes delivery, plus or minus the gap it bid.
- **2026 loan:** "All Return Oil to SPR sites will include the awarded volume in addition to the premium." (RFP section B.5(b).) The obligation is in barrels, and no index sets a price for the oil lent. Money does appear in other terms: quality adjustments; a cash remedy if a borrower returns less than it owes, priced at "the cost value of the Exchange Oil on the date of the last delivery" (section B.7); and the guarantees, sized from "the five (5) day average of NYMEX WTI from Argus Direct." The words "hedge" and "futures" do not appear in the readable text of the five RFPs (one scanned page in each of four RFPs could not be searched).
- **D4TP's reading, not stated in any document:** under the sale terms there is no gap between today's price and a later price for a buyer to lock in, so the oil is worth most to a company that can use it at the delivery point; under the loan terms the borrower owes a fixed number of barrels years later, which can be bought forward at a known price the day it bids.

## 2021-22 loan agreements (U.S. Department of Energy, FOIA reading room)

**What it is.** The exchange (loan) agreements DOE signed under the December
2021 "FY22 Winter Exchange" RFP, and 30 later modifications. One 374-page PDF
holds ExxonMobil's first contract (pages 1 to 107) and twelve agreements of
about 22 pages each; each modification is its own PDF.

**Where it comes from.** `https://www.spr.doe.gov/FOIA/FY22WtrEx.htm`.
`scripts/fetch_doe_foia_2022.py` downloads every PDF linked there into
`data/raw/doe_foia_2022/` (31 files, 451 pages) with `manifest.json` (URL,
bytes, SHA-256) and a copy of the index page. Retrieved October 12, 2026.

**Reading the scans.** 152 of the 374 pages in the main file, and many of the
modifications, are scanned images with no text. `scripts/ocr_pdf.swift` reads
every page with macOS's built-in text recognition (Vision framework, 200 dots
per inch) and writes `data/processed/doe_foia_2022_text/<file>.txt` with a
"=== page N ===" line per page. Recognized text has errors (a zero for a
capital O in agreement numbers, dropped punctuation), so it is used to find and
confirm terms, not quoted without a look at the page.

**How the ledger is built.** The terms of each agreement were keyed by hand into
`data/reference/exchange_2021_22.csv` with the PDF page it starts on.
`scripts/build_exchange_2021_22.py` then checks that every keyed company name,
barrel count, premium and guarantee amount appears in the recognized text of
that agreement's first four pages, stops if one does not, and writes
`data/processed/spr_2021_22_exchange.csv` with the merged name and firm type.

**Coverage.** 13 agreements, 9 borrowers, 24,420,000 barrels: 21,720,000
barrels of sour crude in 12 agreements signed December 10, 2021 to January 25,
2022, and one ExxonMobil agreement for 2,700,000 barrels of sweet crude at a
14.6% premium, which is outside the RFP's 32 million barrels of sour crude. The
seven agreements signed January 21 to 25, 2022 add to the 13.4 million barrels
in DOE's release of January 25, 2022. By firm type, all 13: refiners 57.1%,
majors' trading arms 22.4%, trading houses 20.5%. Sour only: 51.8%, 25.2%,
23.0%.

**Terms.** The premium is fixed in each agreement ("Contractor agrees to a
fixed 8.6% premium return of sour crude oil"): 2.3%, 6.1%, 8.6% or 9.1% for
sour, 14.6% for the sweet agreement. Each agreement names a letter of credit in
dollars and its expiration date. Ten of the twelve agreements with a return
window we keyed set it in 2024 or later.

**Missing or unread.** ExxonMobil's first contract uses the RFP's contract
form, which gives return period numbers, not dates; its premium and return
dates are not keyed. Agreement 22PO0013's first page was not found in the
recognized text; its number comes from DOE's file names for its modifications
and its date is not keyed. Delivery points were not keyed.

**Modifications (`data/reference/exchange_2021_22_mods.csv` -> `data/processed/spr_2021_22_exchange_mods.csv`).**
All 30 modification files were read and keyed by hand: agreement, the date DOE
signed, the kind of change, any new return window and guarantee date, a plain
description, and a short phrase copied from the document.
`scripts/build_exchange_mods.py` stops unless every file has exactly one row,
every copied phrase is in that file's recognized text, and every date and
barrel count in a description is in the text too. Result: 17 changes moved a
return date (on 10 of the 13 agreements, 6 of the 9 borrowers), 6 set terms for
an early return, 5 are final settlements, 2 changed a delivery point. Ten
changes set a return window in 2026:

| DOE signed | Agreement | Borrower | New return window |
|---|---|---|---|
| March 18, 2024 | 22PO0011 | Macquarie | July to October 2026 |
| March 26, 2024 | 22PO0005 | Atlantic Trading & Marketing (TotalEnergies) | July to October 2026 |
| April 11, 2024 | 22PO0004, 22PO0006 | Shell Trading (US) | May 15 to June 30, 2026 |
| April 15, 2024 | 22PO0007 | ExxonMobil | July to October 2026 |
| April 15, 2024 | 22PO0013 | ExxonMobil | April 1 to May 14, 2026 |
| April 16, 2024 | 22PO0010 | Trafigura | July to October 2026 |
| December 10, 2025 | 22PO0007, DE-AC96-22PO00003 | ExxonMobil | November 1 to December 31, 2026 |
| February 24, 2026 | 22PO0013 | ExxonMobil | October 1 to November 30, 2026 |

Limits: the files show what was scheduled, not whether oil was returned on
those dates; only the five final settlements (Marathon, BP, Phillips 66, one
ExxonMobil agreement, Chevron) record returns. Volumes outstanding are mostly
redacted. Two modifications referred to in later ones (22PO0003 Mod 0001 of
February 28, 2025 and 22PO0008 Mod 0002 of April 3, 2025) are not in DOE's
file. DOE's signature date could not be read on four modifications. Where an
extension was granted, the documents that speak to it say "There is no
adjustment to the premium as a result of this extension"; two December 2025
changes for ExxonMobil reduce the premium barrels owed by a redacted amount.
Whether this file is every modification DOE has signed is not known.

**Units and rounding.** Barrels as written in each agreement, "approximately"
and "plus/minus 10%". These are contract volumes, not delivered volumes; the
modifications give delivered "basis barrels" for some.

**License and attribution.** U.S. government records released under the
Freedom of Information Act. Credit: U.S. Department of Energy, Strategic
Petroleum Reserve Project Management Office.

## Gulf Coast refinery, import and export series (EIA), added October 12, 2026

- **Series** (in `scripts/fetch_eia.py`, raw responses in `data/raw/eia/`, tidy copy in `eia_series.csv`): weekly Gulf Coast (PADD 3) refinery utilization (`PET.W_NA_YUP_R30_PER.W`), refiner net crude inputs (`PET.WCRRIP32.W`), commercial crude stocks (`PET.WCESTP31.W`) and commercial crude imports (`PET.WCEIMP32.W`); monthly Gulf Coast crude exports (`PET.MCREXP32.M`) and U.S. crude imports from Persian Gulf countries (`PET.MCRIMUSPG2.M`).
- **Vintage:** pulled October 12, 2026. Weekly series run through October 2, 2026; monthly exports through July 2026; Persian Gulf imports through June 2026. The series pulled on October 10 were left as saved, so published charts do not shift; `_retrieved.json` records the date per series.
- **How they are compared (`design_evidence.json`, `market`):** weekly series are averaged over the same two windows as the national series (March 1 to November 30, 2022; March 20 to October 2, 2026). Monthly series lag, so the same months are compared in both years: March to July for Gulf Coast exports, March to June for Persian Gulf imports.
- **Figures:** Gulf Coast refinery utilization 95.0% and 96.8%; crude inputs 8.79 and 9.45 million barrels a day; Gulf Coast crude imports 1.27 and 1.33 million barrels a day; Gulf Coast crude exports 3.30 and 4.61 million barrels a day (5.44 in April and 5.60 in May 2026); U.S. crude imports from the Persian Gulf 742,000 and 370,000 barrels a day (113,000 in June 2026).
- **Limits:** EIA weekly figures are estimates and are revised; monthly figures are the firmer ones. PADD 3 covers Texas, Louisiana, Mississippi, Alabama, Arkansas and New Mexico, not only the refineries near SPR sites. Exports are by the district the oil left from, not by who sold it, so they cannot be tied to SPR barrels or to any company. Nothing here separates sour from sweet crude.

## Return delays on the 2021-22 loans (`data/processed/spr_2021_22_return_delays.csv`)

- **What it is:** one row per loan agreement, written by `scripts/build_exchange_mods.py`: the original return window (from the agreement), how many times the window was moved, the latest window on file, and the months between the end of the original window and either the last return recorded in a final settlement or, where there is no settlement, the end of the latest scheduled window.
- **Result:** the window moved on 10 of 13 agreements. On five agreements (6,800,000 barrels) the gap is 24 months or more: Atlantic Trading & Marketing 49 months, Chevron 29, ExxonMobil (22PO0007) 27, Trafigura 25, Macquarie 25. Shell's two loans are 21 months, ExxonMobil's sweet loan 16, ExxonMobil's 22PO0003 15. Marathon, BP and Phillips 66 returned on time or early.
- **Read with care:** only Chevron's 29 months and ExxonMobil's 15 are completed returns recorded in a settlement. The others are scheduled dates; the files do not say whether oil came back then. Atlantic Trading & Marketing's first move, from September 2022 to mid-2024, came three weeks after signing and raised its premium from 2.3% to 8.6%; measured from that 2024 date its gap is 25 months. ExxonMobil's first contract (4,800,000 barrels) has no original date keyed, so it has no gap figure, though its latest window is November to December 2026. Agreement 22PO0013's "original" window is the one in the agreement text on file; its first modification calls the same months an extension, so the true original may have been earlier.
