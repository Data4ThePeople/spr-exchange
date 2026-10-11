---
title:
subtitle:
slug: spr-exchange
date: 2026-10-12
section: Data 4 Thought
hero: images/spr-exchange-hero-1680x1080.png
hero_alt:
meta_title:
description:
keywords:
schema_type: article
drop_cap: true
heading_spacer: 20px
caption_spacer: 20px
dividers: false
---

# Title TBD

If you’ve been following our work, you know that I am fascinated by oil markets, especially when they are disrupted in such spectacular fashion. This is why I have [written so extensively about them](https://www.data4thepeople.com/p/rip-us-energy-strategy/). Oil markets are, in my view, the ultimate complex system. Plus, not only do we complacently consume the products of this system, but we have them to thank for our entire standard of living, at least in the developed world (I designed and taught an entire class on this called “The Carbon Economy.”) Getting us all to a base understanding is critical.

But I still have blind spots. One of them was the Strategic Petroleum Reserve (SPR). Over the past few months, I have watched the U.S. drain its SPR, right alongside you, using our free EIA inventory data visualization tool.

![Line chart titled U.S. Petroleum Inventories, Weekly Seasonality, set to the Strategic Reserve. One line per year since 1982 shows the reserve by week of the year, in million barrels. Most years sit between 500 and 700 million. The bold red 2026 line starts near 415 million, falls from about week 13, and ends near 283 million at week 40, below every other year on the chart at that point.](images/01-spr-inventory.png)
*The Strategic Petroleum Reserve by week of the year, 1982 to 2026. The red line is 2026. Source: EIA weekly stocks, from our petroleum inventory tool.*

But I honestly didn’t know how this all worked. I hadn’t done the analysis to – as Cuba Gooding Jr. iconically says in Jerry Maguire – “Show me the money!”

Well, over the weekend I did that analysis, and was shocked at what I found.

The U.S. SPR is not what we thought it was. Maybe it’s just me, but I thought this was oil of last resort to protect Americans from crises. That’s not quite how it works – at least not the way we are drawing it down in 2026. Rather it’s more like an auction, with an auction room where a bidder can lock in a profit the day it bids. Where this oil goes? The government doesn’t say.

All we know is the demand for our emergency oil is being driven by math.

We’ll show you this today. We will… show you the money.

## A brief history of the SPR

Congress created the Strategic Petroleum Reserve in 1975, after the 1973-74 oil embargo. The government stores crude oil in underground salt caverns along the Gulf Coast, at four sites in Texas and Louisiana. The first oil went in during 1977. By the end of 2009 the reserve held 726.6 million barrels, the most it has ever held.

The law lets the President order oil released during a "severe energy supply interruption." The largest release before this year came in 2022, when the government sold 180 million barrels after Russia invaded Ukraine. By June 2023 the reserve was down to 347.2 million barrels, less than half its peak. It was then refilled slowly, to 415.4 million barrels by February 2026.

Then came this year. U.S. crude oil averaged $64.51 a barrel in February and reached $114.58 on April 7. In March, the Energy Department began releasing oil again, as part of a coordinated release with other countries. By October 2 the reserve held 283.0 million barrels, the lowest weekly level since October 1982. Seven of the ten largest weekly withdrawals in the reserve's history came in May and June of this year.

There is one big difference from 2022. That oil was sold. This oil is being lent.

## How the loan works

The Energy Department calls it an "exchange." A company borrows crude oil from the reserve now and promises to return the same amount of oil later, plus extra barrels. The extra is called a premium. It works like interest, paid in oil.

Here is where the auction comes in. For each batch of oil, the department sets a minimum premium. Companies bid by offering to return more than the minimum, and the highest offers win. In the first rounds this spring, the minimum ran from 17% to 24%. The department has said the winning bids averaged about 25%.

## Who took the barrels

After each round, the department posts a one-page sheet listing the winners. We combined every sheet into one ledger, shown below, that you can search and download.

<iframe src="https://data4thepeople.github.io/spr-exchange/dist/ledger.html" width="100%" height="1400" loading="lazy" style="border:0" title="Who took the barrels: every contract in the 2026 Strategic Petroleum Reserve exchange"></iframe>

Thirteen companies won 31 contracts for 133.56 million barrels. Trading houses, which buy and sell oil but do not refine it, took 45.0%. Refiners took 38.3%. The trading arms of two oil majors took 14.8%, and a pipeline company took the rest. The largest borrower was Trafigura, a trading house, with 34.35 million barrels, or 25.7% of the total.

The contracts do not say where the oil has to go. Ownership passes to the borrower when the oil leaves the reserve, and nothing in the terms limits resale or export. The department told bidders as much in writing: "The goal of the Emergency Exchange Release is to get barrels onto the market." Which market? The department's own announcements say the goal is to stabilize GLOBAL oil supply, and nothing in the contracts keeps the oil here.

## Why pay 20% interest in oil?

Returning 120 barrels for every 100 borrowed sounds like a bad deal. The chart below walks through one barrel in three of the six rounds to show when it is a good one.

<iframe src="https://data4thepeople.github.io/spr-exchange/dist/trade.html" width="100%" height="1300" loading="lazy" style="border:0" title="How borrowing oil from the reserve can make money"></iframe>

Take the April round. On April 13, the day bids were due, a barrel for quick delivery sold for $99.08. On the same day, a company could sign a contract to buy oil for late 2028 at $68.37. Oil for later delivery was cheaper, which is common when supply is short today. A borrower that owed 20% extra needed 1.2 barrels in 2028, at a cost of $82.05. That left $17.03 for each barrel borrowed, before shipping and other costs.

What matters is the gap between the two prices. In April, oil sold now cost 44.9% more than oil for late 2028, and the government asked for 20%. When the gap is bigger than the premium, borrowing pays. Companies snapped up 86.8% of the oil offered in that round.

By June the gap had shrunk to 14.4%. As the math changed, the department cut its minimum premium to between 8% and 9%, and companies still took only 500,000 of the 40 million barrels offered. 

Remember this cut. In the 2021 and 2022 loans the premium was fixed and never changed. We will come back to it tomorrow.

Trading houses borrowed 16.03 million barrels in the April round. If each locked in both prices on the day bids were due, the group's profit before transportation costs comes to about $273 million. That is our estimate of what the terms allowed, not what any company earned. Bids are not public, and a company that locked in prices on a different day could have made much less or much more.

The cool thing here is that now that we understand the general math, we can get a sense of what to expect. Results for the latest round, with bids due on October 6, have not been posted. But we can run the math on this round and find that the same math shows $9.87 a barrel there for the longest return dates. So on paper this round pays far better than June's, but well short of April's.

## When does the oil come back?

Each contract lets the borrower pick from a set of return dates, and later dates carry a slightly higher premium. The chart below shows the earliest and the latest that the contracts allow the oil to be returned.

<iframe src="https://data4thepeople.github.io/spr-exchange/dist/returns.html" width="100%" height="1000" loading="lazy" style="border:0" title="When is the borrowed oil due back?"></iframe>

The department has not published which dates each company chose, so the real path is somewhere between the two lines. On the latest dates allowed, 8.48 million barrels, or 6% of the oil awarded, are due back by the end of 2027. About 65% is due by the end of 2028. The last barrels are due July 31, 2029.

## Two risks we have taken on

The Energy Department has a case for all of this. Releasing oil in a supply emergency is what the reserve is for. A loan also brings oil back, which the 2022 sale did not, and the department says the premiums will leave the reserve with more barrels than it lent.

In our view, the design still leaves the country carrying two risks that the borrowers do not.

**The first is 2027.** Most of this oil does not have to come back next year. When we started lending this oil, the market was priced for a short disruption. Oil for 2027 cost about a quarter less than oil that day. That expectation has not aged well. Seven months later, oil still costs about what it did the day the first loans were awarded. So, what if this disruption lasts through 2027? Then the reserve faces it with 283 million barrels and no promise that most of the lent oil is back. We are left holding the bag. If supply gets worse before it gets better, the reserve has less to give. Markets have started to price in a protracted supply crunch since the first loans were awarded. On March 20, oil for delivery in 2027 averaged $74.69 a barrel. On October 9 it averaged $83.46, about 12% higher.

A borrower can protect itself against a move like that. It can lock in its buying price on the day it borrows. The government has no matching tool for the thing it gave up, which is having the oil on hand.

**The second is getting the oil back on time.** The government is owed barrels, not dollars. Its protection is a bank guarantee equal to the oil's value on the day of the award. If prices are higher when the oil comes due, that money buys fewer barrels than were lent. The contracts also excuse late delivery in cases such as war. And return dates can be changed after the fact.

That has happened before. Return dates were pushed back more than once on oil lent in 2021 and 2022, according to reporting by Argus.

## My view

I am very upset by all of this. Look at Trafigura. We have basically outsourced the decision of when our oil comes back and where it goes to companies like this. There is nothing wrong with them per se. But their job is not to care about American energy security in 2027. Their job is to turn a profit on a trade. More than a quarter of the oil we lent this year has gone to this one company. What this tells me is that our government, if it cares about American energy security in 2027, is betting that these companies' financial incentives today align with lower risk for America in 2027. I just don't see how that is the case. To me it seems shortsighted, if we assume our government cares about our energy security. And if it doesn't, this is one more case of handing our energy strategy to corporate interests.

I believe the U.S. should care what is done with its emergency oil. Under these contracts it does not. A regional refiner that borrows a barrel is far more likely to run it through a refinery here. A trading house can sell it anywhere. Less than 1% of this oil went to a small refiner, and nearly half went to trading houses. Once it is sold, we have no idea where it goes. The bet was that our oil would make a difference on the global market. That could have worked if the conflict had ended quickly. It didn't, and now our laissez-faire approach of lending emergency oil to the highest bidder may be backfiring.

This reminds me of something else happening right now. The Treasury Department is working to hold down [rising interest rates on U.S. debt](https://www.bloomberg.com/news/articles/2026-08-19/long-dated-treasuries-rally-as-treasury-boosts-bond-buybacks) (if you aren't up to speed on that, it is worth catching up). So far, rates have kept climbing. In both cases, the government is using the tools it has to steady a market much bigger than it is. At some point those tools may not be enough. To me, that looks like a risk for our debt and our oil at the same time.

[In July I wrote](https://www.data4thepeople.com/p/rip-us-energy-strategy/) that America no longer has an energy strategy, and that we were handing our oil decisions to people who care more about the next earnings report than about our energy security. The reserve is where that shows up in a ledger.

Tomorrow we will look at how the 2021 and 2022 loans worked, and how they compare with this year's.

::: divider

## What this does not tell you

- **What any company earned.** The profit figures are our estimates of what the government's terms allowed. They use the minimum premium, one pricing day, and the best pickup and return dates on offer. Actual bids are not public.
- **The borrowers' costs.** Shipping, pipeline and terminal fees, the bank guarantee, and the lower price of high-sulfur oil are left out. All of them reduce what is left over.
- **Official settlement prices.** Our futures prices are daily closes as relayed by Yahoo Finance.
- **The real return schedule.** The return chart shows the earliest and latest dates the contracts allow. The earliest line is faster than the reserve sites can physically take oil back.
- **Where the oil went.** Crude oil is interchangeable once it enters the market, and the award sheets do not track it.
- **How each company should be labeled.** The firm types in the ledger are our classification, based on the company name the department listed.

The data, code and method notes are public at [github.com/Data4ThePeople/spr-exchange](https://github.com/Data4ThePeople/spr-exchange).
