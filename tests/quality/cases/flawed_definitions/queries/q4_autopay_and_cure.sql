-- Autopay migration (PAY-4471): failed debits by month, 30+ rate for autopay vs non-autopay accounts, share of 30+ accounts that hit a failed debit, and cure of the September 30+ cohort
with impacted as (
    select distinct account_id from monthly_performance where autopay_failed = 1
)
select m.month,
       sum(m.autopay_attempted)                                                                         as attempted,
       sum(m.autopay_failed)                                                                            as failed,
       round(100.0 * sum(m.autopay_failed) / nullif(sum(m.autopay_attempted), 0), 2)                   as fail_pct,
       round(100.0 * sum(case when m.autopay_flag = 1 and m.dpd_bucket >= 30 and m.status in ('active', 'open_no_balance') then 1 else 0 end)
             / sum(case when m.autopay_flag = 1 and m.status in ('active', 'open_no_balance') then 1 else 0 end), 2) as rate_autopay,
       round(100.0 * sum(case when m.autopay_flag = 0 and m.dpd_bucket >= 30 and m.status in ('active', 'open_no_balance') then 1 else 0 end)
             / sum(case when m.autopay_flag = 0 and m.status in ('active', 'open_no_balance') then 1 else 0 end), 2) as rate_non_autopay,
       sum(case when m.dpd_bucket >= 30 and m.status in ('active', 'open_no_balance') then 1 else 0 end) as dpd30_plus,
       sum(case when i.account_id is not null and m.dpd_bucket >= 30 and m.status in ('active', 'open_no_balance') then 1 else 0 end) as dpd30_plus_impacted
from monthly_performance m
left join impacted i using (account_id)
where m.month >= '2026-05'
group by 1
order by 1;

with impacted as (
    select distinct account_id from monthly_performance where autopay_failed = 1
),
sep as (
    select m.account_id,
           case when i.account_id is not null then 'autopay_impacted' else 'other' end as grp
    from monthly_performance m
    left join impacted i using (account_id)
    where m.month = '2026-09' and m.dpd_bucket >= 30 and m.status in ('active', 'open_no_balance')
)
select s.grp,
       count(distinct s.account_id)                                                                      as sep_dpd30_plus,
       sum(case when n.month = '2026-10' and n.dpd_bucket >= 30 and n.status = 'active' then 1 else 0 end) as still_dpd30_oct,
       sum(case when n.month = '2026-11' and n.dpd_bucket >= 30 and n.status = 'active' then 1 else 0 end) as still_dpd30_nov,
       count(distinct s.account_id)
         - sum(case when n.month = '2026-11' and n.dpd_bucket >= 30 and n.status = 'active' then 1 else 0 end) as cured_by_nov
from sep s
left join monthly_performance n on n.account_id = s.account_id and n.month in ('2026-10', '2026-11')
group by 1
order by 1;
