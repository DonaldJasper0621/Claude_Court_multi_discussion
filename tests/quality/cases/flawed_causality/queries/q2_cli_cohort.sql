-- q2: delinquency by utilization band (Nov 2026) and the April credit-line program cohort, identified as accounts whose current line is above their origination line
select
  case when utilization < 0.30 then '1. under 30%'
       when utilization < 0.60 then '2. 30-60%'
       when utilization < 0.90 then '3. 60-90%'
       else '4. 90% and above' end                                        as utilization_band,
  count(*)                                                                as accounts,
  count(*) filter (where dpd_bucket >= 30)                                as dpd30_plus,
  round(100.0 * count(*) filter (where dpd_bucket >= 30) / count(*), 2)   as rate_pct
from monthly_performance
where month = '2026-11' and status = 'active'
group by 1
order by 1;

with cli_cohort as (
  select m.account_id
  from monthly_performance m
  join accounts a using (account_id)
  where m.month = '2026-11'
    and m.credit_line > a.initial_credit_line
)
select
  'April program cohort'                                                  as segment,
  count(*)                                                                as accounts,
  count(*) filter (where m.dpd_bucket >= 30)                              as dpd30_plus,
  round(100.0 * count(*) filter (where m.dpd_bucket >= 30) / count(*), 2) as rate_pct,
  round(avg(m.utilization), 3)                                            as avg_utilization,
  string_agg(distinct a.credit_tier, ',' order by a.credit_tier)          as tiers
from monthly_performance m
join cli_cohort using (account_id)
join accounts a using (account_id)
where m.month = '2026-11' and m.status in ('active','open_no_balance');
