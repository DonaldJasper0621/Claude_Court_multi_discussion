-- q1: 30+ DPD series restated on one definition (pre-June basis: all open accounts in numerator and denominator), with the active-only denominator alongside
select
  month,
  count(*) filter (where status in ('active','open_no_balance'))                         as open_accounts,
  count(*) filter (where status = 'active')                                               as active_accounts,
  count(*) filter (where status in ('active','open_no_balance') and dpd_bucket >= 30)     as dpd30_plus_open,
  round(100.0 * count(*) filter (where status in ('active','open_no_balance') and dpd_bucket >= 30)
        / count(*) filter (where status in ('active','open_no_balance')), 2)              as rate_consistent_pct,
  round(100.0 * count(*) filter (where status in ('active','open_no_balance') and dpd_bucket >= 30)
        / count(*) filter (where status = 'active'), 2)                                   as rate_as_pack_v2_pct
from monthly_performance
where month >= '2026-05'
group by month
order by month;
