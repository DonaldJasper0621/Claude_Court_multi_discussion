# Data dictionary: co-brand card practice dataset

Synthetic data. All accounts, people and figures are invented.

## accounts.csv (one row per account)
| column | definition |
|---|---|
| account_id | Unique account key |
| open_month | Month the account was opened (YYYY-MM) |
| acquisition_channel | partner_instore, partner_online, bank_direct, affiliate |
| campaign_id | Marketing campaign credited with the acquisition; ORGANIC if none |
| credit_tier | Internal risk tier at origination: A (best) to D |
| fico_at_origination | Bureau score at origination |
| state | Billing state |
| initial_credit_line | Line assigned at origination, USD |
| autopay_enrolled_at_open | 1 if the customer enrolled in autopay at onboarding |

## monthly_performance.csv (one row per account per month while on book)
| column | definition |
|---|---|
| month | Performance month (YYYY-MM) |
| status | active (statement balance > 0), open_no_balance, closed, charged_off |
| statement_balance | Statement balance at cycle end, USD |
| credit_line | Credit line in effect that month, USD |
| utilization | statement_balance / credit_line |
| min_payment_due | Minimum payment due for the cycle |
| payment_received | Total payments received in the cycle |
| dpd_bucket | Days past due bucket at cycle end: 0, 30, 60, 90 |
| autopay_flag | 1 if autopay is enrolled that month |
| autopay_attempted | 1 if an autopay debit was scheduled for the cycle |
| autopay_failed | 1 if the scheduled autopay debit was not submitted or was rejected |
| months_on_book | Months since open_month |

## campaigns.csv
One row per marketing campaign with channel, dates, offer and approval policy.

## kpi_report_as_published.csv
The 30+ DPD rate as it appeared in the monthly portfolio KPI pack.

- `dpd30_plus_rate_pct` = dpd30_plus_accounts / denominator_accounts.
- `definition_version`: v1 through 2026-05, v2 from 2026-06.
  - v1 denominator: all open accounts (active + open_no_balance).
  - v2 denominator: active accounts only (statement balance > 0), per reporting definitions v2 adopted portfolio-wide in June 2026.

## ops_notes.md
Monthly change log extracts relevant to the card portfolio.
