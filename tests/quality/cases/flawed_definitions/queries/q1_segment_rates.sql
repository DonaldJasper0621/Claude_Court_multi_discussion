-- 30+ DPD rate by credit tier and by acquisition channel, May / Sep / Nov 2026 ("which customers")
select a.credit_tier,
       m.month,
       count(*)                                                                                        as accounts,
       sum(case when m.dpd_bucket >= 30 and m.status in ('active', 'open_no_balance') then 1 else 0 end) as dpd30_plus,
       round(100.0 * sum(case when m.dpd_bucket >= 30 and m.status in ('active', 'open_no_balance') then 1 else 0 end)
             / count(*), 2)                                                                            as rate_pct
from monthly_performance m
join accounts a using (account_id)
where m.month in ('2026-05', '2026-09', '2026-11')
group by 1, 2
order by 1, 2;

select a.acquisition_channel,
       m.month,
       count(*)                                                                                        as accounts,
       sum(case when m.dpd_bucket >= 30 and m.status in ('active', 'open_no_balance') then 1 else 0 end) as dpd30_plus,
       round(100.0 * sum(case when m.dpd_bucket >= 30 and m.status in ('active', 'open_no_balance') then 1 else 0 end)
             / count(*), 2)                                                                            as rate_pct
from monthly_performance m
join accounts a using (account_id)
where m.month in ('2026-05', '2026-11')
group by 1, 2
order by 1, 2;
