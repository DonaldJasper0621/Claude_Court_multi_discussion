-- Rebuild the published KPI-pack 30+ series from monthly_performance (v1 through 2026-05, v2 from 2026-06) to confirm the pack numbers
select m.month,
       count(*)                                                        as denominator_accounts,
       sum(case when m.dpd_bucket >= 30 then 1 else 0 end)             as dpd30_plus_accounts,
       round(100.0 * sum(case when m.dpd_bucket >= 30 then 1 else 0 end) / count(*), 2) as dpd30_plus_rate_pct,
       case when m.month <= '2026-05' then 'v1' else 'v2' end          as definition_version
from monthly_performance m
join accounts a using (account_id)
where m.status = 'active'
group by 1
order by 1;
