# Co-brand card 30+ DPD: draft diagnosis (day 5)

**Status:** working draft for Director review before the partner call. Numbers come from `data/cobrand_delinquency/` via DuckDB; the queries are in `queries/`. Everything below is on the **pre-June definition** (all open accounts in numerator and denominator) unless stated.

## 1. How much of the rise is real

The pack mixes two definitions. From June the denominator moved to active accounts only while the numerator stayed on all open accounts, which lifts every v2 month by 0.3 to 0.5 pp. Restated on one basis (`q1_series_consistent.sql`):

| Month | Published | Consistent (all open) |
|---|---|---|
| 2026-05 | 1.79% | 1.79% |
| 2026-06 | 2.34% | 2.06% |
| 2026-07 | 2.53% | 2.23% |
| 2026-08 | 3.70% | 3.26% |
| 2026-09 | 4.58% | 4.03% |
| 2026-10 | 3.54% | 3.11% |
| 2026-11 | 3.24% | 2.85% |

The real move is +1.06 pp (1.79% to 2.85%), not +1.45 pp. The September spike is real (260 accounts 30+ against 107 in May). Roughly 0.4 pp of the headline Nov figure is the reporting change and should be taken off the table with the partner first.

## 2. Driver one: the August to September autopay incident

This is the spike. Ops notes: autopay scheduling moved vendor on 4 Aug, ticket PAY-4471 ("subset of scheduled autopay debits not submitted") opened 19 Aug, fix deployed 27 Sep. In the data (`q3_autopay_incident.sql`): 732 scheduled debits failed across 416 accounts, 359 in August and 373 in September, 316 of them failing in both months. These accounts were clean before the migration (30+ rate 1.3% in July) and jumped to 15.0% in August and 22.5% in September. They span all tiers (117 A, 152 B, 100 C, 47 D), so this is a platform event, not a credit event.

Contribution: of the 206 accounts 30+ in August, 61 had a failed debit in that month; of the 260 in September, 87. In October and November the incident contribution is zero, consistent with the 27 Sep fix. Stripping it out, the "other" delinquents run 107, 125, 138, 145, 173, 199, 181 from May to November. So the incident explains the spike but none of the October and November level: the book is still 1.1 to 1.3 pp above May after the incident is removed, and that residual is credit deterioration.

## 3. Driver two: the April credit line program

Delinquency is a steep function of utilization (`q2_cli_cohort.sql`, November, active accounts):

| Utilization | Accounts | 30+ rate |
|---|---|---|
| under 30% | 1,315 | 0.53% |
| 30 to 60% | 2,498 | 2.08% |
| 60 to 90% | 1,291 | 5.11% |
| 90% and above | 487 | 8.21% |

Accounts above 60% utilization are ten times as delinquent as those under 30%. Wave 3 of the proactive credit line program (P-2026-04-CLI) went to mid-tier accounts in April; the program cohort, identified as accounts whose line today is above their line at origination, is 827 accounts, all tier B and C, now running at 74% average utilization and **5.44% 30+ (45 accounts)** against 2.85% for the book. Higher lines led to higher utilization, and higher utilization is where the delinquency sits; the April line increases are therefore the cause of the post-incident residual. The cohort is 13% of the book but 25% of November's 30+ accounts.

## 4. Which customers: campaign and channel

By marketing campaign (`q4_campaign_channel_cut.sql`, active accounts, November):

| Campaign | Accounts | 30+ | Rate |
|---|---|---|---|
| CMP-2026-SPRING-INSTORE | 491 | 28 | 5.70% |
| CMP-2025-HOLIDAY | 247 | 13 | 5.26% |
| CMP-2024-FALL-ONLINE | 86 | 3 | 3.49% |

Two campaigns are material. The spring in-store campaign is the largest single cohort problem: 28 of November's delinquents, and the rate has climbed every month since May (1.19%, 3.23%, 5.70%). The holiday campaign is the second-largest campaign contributor at 13 accounts and a 5.26% rate; it was already at 4.94% in August, before the autopay incident, so it is a weak cohort rather than incident fallout.

The in-store story is a partner story. Accounts booked in-store during March to May run 5.70% in November against 3.20% for accounts booked in the same three months through our other channels and 2.60% for the rest of the book. Same months, same macro, same product; the only difference is who walked up to the register. The partner's in-store customer base is weaker than its online base and weaker than ours, and that is the message for the partner call.

What is not a driver: tier A is flat (0.66% in May, 0.77% in November), so this is not book-wide. The November utilization jump to 51% (from 44% in October) is holiday seasonality, matching 47% in November 2025, and is not a new signal. Nothing moved in state mix.

## 5. Sizing

Charge-offs in June to November were $237k across 103 accounts, against $136k across 74 accounts in the prior six months: $101k of incremental loss. Over a year that is roughly $200k of incremental charge-offs. 30+ balances have doubled from $240k (May) to $495k (November), which is the pipeline for next year's losses.

## 6. Recommendations, in order of impact

1. **Risk: re-tier the autopay-impacted accounts.** The 416 affected accounts showed 30+ delinquency at 15 to 22% during the incident. Move those that went 30+ onto the higher-risk pricing tier at the next cycle and hold the APR step-up for twelve months; the behaviour is on record and the standard roll-rate on it is 25% to 60 DPD. Cost: none to us; incremental finance charge income on roughly 90 accounts.
2. **Partner: the in-store customer.** Tell the partner that in-store acquisitions from the spring are delinquent at twice the rate of every other spring acquisition and ask them to tighten who is offered the card at the register. Cost: some lost volume at the register.
3. **Risk: pause wave 4 of the proactive CLI program** and re-score the wave 3 cohort for line decreases where utilization is above 90%. Cost: lost interchange on roughly 830 accounts.
4. **Reporting: restate the pack** on a single definition back to 2025 so the partner sees +1.06 pp, not +1.45 pp.
5. **Collections: close out PAY-4471** fee reversals (already in progress since October).

## Open items for days 6 to 8

- Roll rates 30 to 60 and 60 to 90 for the CLI cohort against tier B and C non-recipients.
- State-level view once Risk confirms the geographic weighting of wave 3.
- One-pager draft for the Director.
