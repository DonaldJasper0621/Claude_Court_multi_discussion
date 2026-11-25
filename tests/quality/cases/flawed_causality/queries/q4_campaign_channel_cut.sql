-- q4: 30+ DPD by marketing campaign (campaign attributed from acquisition channel and open month) and the spring in-store vintage against the rest of the book
select
  c.campaign_id,
  m.month,
  count(*) filter (where m.status = 'active')                                               as active_accounts,
  count(*) filter (where m.status = 'active' and m.dpd_bucket >= 30)                        as dpd30_plus,
  round(100.0 * count(*) filter (where m.status = 'active' and m.dpd_bucket >= 30)
        / count(*) filter (where m.status = 'active'), 2)                                   as rate_pct
from monthly_performance m
join accounts a using (account_id)
join campaigns c
  on (c.channel = a.acquisition_channel or c.channel = 'mixed')
 and a.open_month between c.start_month and c.end_month
where m.month in ('2026-08', '2026-11')
group by 1, 2
order by 1, 2;

select
  case when a.acquisition_channel = 'partner_instore' and a.open_month between '2026-03' and '2026-05' then 'in-store, opened Mar-May 2026'
       when a.open_month between '2026-03' and '2026-05' then 'other channels, opened Mar-May 2026'
       else 'rest of book' end                                                              as segment,
  m.month,
  count(*) filter (where m.status = 'active')                                               as active_accounts,
  round(100.0 * count(*) filter (where m.status = 'active' and m.dpd_bucket >= 30)
        / count(*) filter (where m.status = 'active'), 2)                                   as rate_pct
from monthly_performance m
join accounts a using (account_id)
where m.month in ('2026-05', '2026-08', '2026-11')
group by 1, 2
order by 1, 2;
