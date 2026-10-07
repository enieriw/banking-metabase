
  
    

  create  table "datawarehouse"."analytics"."mart_credit_utilization__dbt_tmp"
  
  
    as
  
  (
    with monthly_spend as (
    select
        card_id,
        date_trunc('month', transaction_at) as month,
        sum(amount) filter (where amount > 0) as total_spend
    from "datawarehouse"."analytics"."stg_transactions"
    group by 1, 2
)
select
    s.card_id,
    c.user_id,
    s.month,
    c.credit_limit,
    s.total_spend,
    s.total_spend / nullif(c.credit_limit, 0) as utilization_ratio
from monthly_spend s
join "datawarehouse"."analytics"."stg_cards" c on c.card_id = s.card_id
where lower(c.card_type) = 'credit'
  );
  