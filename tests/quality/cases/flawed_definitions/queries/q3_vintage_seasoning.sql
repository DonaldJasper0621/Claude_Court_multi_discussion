-- Seasoning curve: 30+ DPD rate by months on book, built from the vintages opened 2025-06 onwards
select a.open_month,
       max(m.months_on_book)                                                                               as months_on_book,
       sum(case when m.status in ('active', 'open_no_balance') then 1 else 0 end)                           as open_accounts,
       sum(case when m.dpd_bucket >= 30 and m.status in ('active', 'open_no_balance') then 1 else 0 end)    as dpd30_plus,
       round(100.0 * sum(case when m.dpd_bucket >= 30 and m.status in ('active', 'open_no_balance') then 1 else 0 end)
             / sum(case when m.status in ('active', 'open_no_balance') then 1 else 0 end), 2)                as rate_pct
from monthly_performance m
join accounts a using (account_id)
where a.open_month >= '2025-06'
group by a.open_month
order by months_on_book;
