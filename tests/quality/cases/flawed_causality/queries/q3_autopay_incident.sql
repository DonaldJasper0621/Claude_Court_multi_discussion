-- q3: size of the PAY-4471 autopay incident and how many of each month's 30+ accounts had a failed debit that month
select
  count(distinct account_id)                                      as accounts_with_failed_debit,
  count(*)                                                        as failed_debits,
  count(distinct account_id) filter (where month = '2026-08')     as failed_aug,
  count(distinct account_id) filter (where month = '2026-09')     as failed_sep
from monthly_performance
where autopay_failed = 1;

with affected as (select distinct account_id from monthly_performance where autopay_failed = 1)
select m.month,
       count(*)                                                              as affected_on_book,
       round(100.0 * count(*) filter (where m.dpd_bucket >= 30) / count(*), 2) as affected_dpd30_rate_pct
from monthly_performance m join affected using (account_id)
where m.month between '2026-06' and '2026-11'
group by 1 order by 1;

select
  month,
  count(*) filter (where dpd_bucket >= 30)                          as dpd30_plus_open,
  count(*) filter (where dpd_bucket >= 30 and autopay_failed = 1)   as dpd30_plus_autopay_incident,
  count(*) filter (where dpd_bucket >= 30)
    - count(*) filter (where dpd_bucket >= 30 and autopay_failed = 1) as dpd30_plus_other
from monthly_performance
where status in ('active','open_no_balance') and month between '2026-05' and '2026-11'
group by month
order by month;
