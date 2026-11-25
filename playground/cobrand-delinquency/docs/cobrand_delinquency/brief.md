# Brief: co-brand card 30+ DPD rate has risen over the last six months

**From:** Director, Co-brand Card Portfolio
**To:** Business Analyst
**Date:** 2026-11-20 (synthetic practice scenario)

The monthly KPI pack shows the co-brand card 30+ days-past-due rate going from
about 1.8% in the spring to over 3% by November, with a spike to 4.6% in
September. The partner's finance team has noticed and is asking whether this
is a credit problem with the card or something on our side. I need to answer
them in two weeks.

What I want from you:

1. **What is actually driving this?** Not a list of everything that moved;
   the two or three things that explain most of the rise, with evidence, and
   a clear statement of what is not a driver even if it looks like one.
2. **How much of the rise is real.** The KPI pack had a reporting change this
   year; I want to know what the trend looks like on a consistent basis.
3. **Which customers.** Is this a book-wide deterioration or concentrated in
   a cohort, channel, or program?
4. **What we do about it.** Actions I can take to Risk and to the partner,
   ordered by impact, with what each one would cost us.
5. **A one-page summary** I can forward, plus the analysis behind it.

Constraints: the data you have is in `data/cobrand_delinquency/`. Use the
data dictionary; definitions matter here. I will ask where every number comes
from. Keep the partner conversation in mind: anything that blames their
customers needs to be airtight.

What the pack shows (30+ DPD rate, as published):

| Month | Rate |
|---|---|
| 2026-05 | 1.79% |
| 2026-06 | 2.34% |
| 2026-07 | 2.53% |
| 2026-08 | 3.70% |
| 2026-09 | 4.58% |
| 2026-10 | 3.54% |
| 2026-11 | 3.24% |

## Suggested working order (you decide)

1. Problem statement and the questions you will answer, in `docs/cobrand_delinquency/problem_statement.md`.
2. Metric definitions you will use and why, in `docs/cobrand_delinquency/metric_definitions.md`.
3. Queries and analysis in `analysis/cobrand_delinquency/` (SQL via DuckDB or pandas; keep the queries).
4. Diagnosis and recommendation in `docs/cobrand_delinquency/diagnosis.md`.
5. One-page summary in `docs/cobrand_delinquency/one_pager.md`.

Rehearse at each step with `/rehearse` (framing, method, review, preread).
Grade the final diagnosis with `/rehearse grade`.
