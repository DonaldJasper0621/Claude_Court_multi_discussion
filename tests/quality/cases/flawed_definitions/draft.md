# Co-brand card 30+ DPD: draft diagnosis (day 4, work in progress)

**Status:** working draft for the Director. Numbers come from `kpi_report_as_published.csv`, `monthly_performance.csv` and `accounts.csv`; every figure is traceable to a query in `queries/`. Tables `accounts` and `monthly_performance` are the two CSVs loaded into DuckDB.

## Headline

The 30+ DPD rate rose from 1.79% in May 2026 to 3.24% in November 2026, a rise of 1.45 points, with a spike to 4.58% in September. The KPI pack moved to reporting definitions v2 in June (denominator restricted to active accounts); I have checked the effect and the definition change does not materially change the picture, so the published series is used as the headline throughout this note.

The book was improving before the summer: the published rate fell from 2.28% in February to 1.96% in March and 1.67% in April, the lowest level in the 18 months of history, and was still 1.79% in May. The deterioration is therefore a June-onwards event, and the question is what changed in the summer.

## Reconciliation of the published series

`queries/q2_published_recon.sql` rebuilds the pack series from `monthly_performance`. It reproduces the published v1 series through May 2026 and the v2 series from June onwards; the November denominator is 5,591 accounts, matching the pack to the account. The pack numbers are therefore trustworthy and the rise is not a reporting artefact; it is in the account-level data.

## Driver 1: the August payments-platform migration (the spike)

Autopay scheduling moved to a new vendor on 4 August; ticket PAY-4471 ("subset of scheduled autopay debits not submitted") was opened on 19 August and the fix was deployed on 27 September (ops notes). The data shows exactly this (`queries/q4_autopay_and_cure.sql`, first statement):

| Month | Autopay debits attempted | Failed | Fail % | 30+ rate, autopay accounts | 30+ rate, non-autopay accounts |
|---|---|---|---|---|---|
| 2026-07 | 2,948 | 0 | 0.0% | 1.28% | 3.35% |
| 2026-08 | 3,025 | 359 | 11.9% | 3.09% | 3.47% |
| 2026-09 | 3,134 | 373 | 11.9% | 4.35% | 3.64% |
| 2026-10 | 3,102 | 0 | 0.0% | 2.41% | 3.99% |
| 2026-11 | 3,114 | 0 | 0.0% | 1.77% | 4.23% |

Autopay-enrolled customers are normally the best-paying part of the book (about 1.1 to 1.3% 30+ through July). For two cycles their rate more than tripled while the non-autopay rate moved by a few tenths. 416 distinct accounts had at least one failed debit. Accounts that hit a failed debit account for 61 of the 206 accounts 30+ in August (30%) and 93 of the 260 in September (36%); by November they are 14 of 181 (8%). Impacted accounts span all tiers (117 A, 152 B, 100 C, 47 D), which is what an operational failure looks like and a credit problem does not. This is the whole of the September spike and most of the August step.

## Driver 2: the spring 2026 in-store vintage (the part that stays)

The spring in-store promotion (CMP-2026-SPRING-INSTORE, March to May, instant approval at the register with the score floor lowered 20 points) booked 542 accounts with an average origination FICO of 675 against 711 for the rest of the book. Including organic in-store traffic, 1,467 accounts were opened in March to May 2026 versus a normal run-rate of about 150 a month. In November these spring accounts are 22% of the open book (1,412 of 6,358) and run at 3.97% 30+ against 2.53% for the rest of the book. Inside the vintage, the campaign accounts run at 5.33% versus 3.16% for organic accounts opened in the same months, so the lowered floor is the specific issue, not in-store acquisition in general. This vintage, not the autopay incident, is why November (3.24%) is still well above May.

Seasoning matters for how much further this goes. `queries/q3_vintage_seasoning.sql` gives the 30+ rate by months on book for the vintages opened since June 2025: 0.38% at 2 months on book, 1.36 to 1.76% at 4 to 5 months, 2.04% at 6, 2.46% at 7, 2.21% at 8, then climbing through 3.11% at 11 months to 3.58% at 15 months on book. The curve is still rising at 15 months. The spring vintage is at 6 to 8 months on book in November, so it has not reached its seasoning peak; on this curve its rate should rise a further 1.1 to 1.5 points over the next six to nine months before it levels off, which would add roughly 0.3 points to the portfolio rate.

## Which customers

By credit tier (`queries/q1_segment_rates.sql`, first statement), 30+ rate in May / September / November 2026:

| Tier | May | Sep | Nov | Nov accounts |
|---|---|---|---|---|
| A | 0.65% | 2.33% | 0.76% | 1,831 |
| B | 1.20% | 2.67% | 1.83% | 2,407 |
| C | 2.51% | 6.37% | 4.96% | 1,431 |
| D | 4.85% | 7.82% | 7.04% | 739 |

Tiers A and B spiked in September and are back near their May level; the lasting deterioration is in C and D, where the spring campaign accounts concentrate. By acquisition channel (second statement) the rise is broad and roughly even: bank_direct 1.81% to 2.54%, partner_instore 1.82% to 2.91%, partner_online 1.75% to 2.88%, affiliate 1.57% to 3.20% on a base of 344 accounts. Channel as such is not a driver; the campaign vintage inside the in-store channel is. The rise is also spread across the ten largest states, so geography is not a driver.

## The September cohort has cured

`queries/q4_autopay_and_cure.sql` (second statement) follows the 260 accounts that were 30+ in September. By November, 220 of them (85%) are no longer delinquent; for the 93 autopay-impacted accounts it is 84 of 93 (90%), with only 9 still past due and in collections. The autopay part of the September cohort has fully cured, which is the pattern of a payments failure rather than a credit event, and supports telling the partner that the spike is behind us.

## Open item

Credit line program wave 3 (April, policy memo P-2026-04-CLI) increased lines for 867 accounts (221 tier B, 646 tier C). Their 30+ rate went from 3.02% in May to 5.44% in November against 1.59% to 2.46% for the rest of the book. Three quarters of the wave is tier C, so part of that gap is tier mix; I have not yet separated the line-increase effect from tier and utilization at selection. Day 5.

## Recommendations, ordered by impact

1. **To Risk and the partner: close out PAY-4471.** Confirm the fix is holding (zero failed debits in October and November), finish the collections outreach and fee reversals for the 416 impacted accounts, and give the partner the August to October explanation with the autopay table above. Cost: fee reversals already processed; otherwise negligible.
2. **To the partner and Marketing: withdraw the lowered score floor for in-store instant approval**, or restrict it to applicants who would land in tiers A and B, before the next in-store promotion. Re-review the 542 campaign accounts at 12 months on book. Cost: fewer approvals on in-store promotions; the spring campaign added about 540 accounts, of which the marginal 20-point band is the part that would be lost.
3. **To Risk: a book-wide 10% credit line decrease across all open accounts, effective with the December cycle**, to bring exposure down while the rate normalises over the next two quarters. Cost: lower spend and interchange across the portfolio and a partner conversation about customer experience; this is the fastest way to protect the loss forecast.

Next steps for day 5: close the CLI open item, build the one-pager, and quantify expected losses for the spring vintage.
