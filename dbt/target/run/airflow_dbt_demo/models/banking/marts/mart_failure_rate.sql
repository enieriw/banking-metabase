
  
    

  create  table "datawarehouse"."analytics"."mart_failure_rate__dbt_tmp"
  
  
    as
  
  (
    select
    date_trunc('month', transaction_at) as month,
    transaction_method,
    count(*) as total_transactions,
    count(*) filter (where is_failed) as failed_transactions,
    round(100.0 * count(*) filter (where is_failed) / count(*), 2) as failure_rate_pct
from "datawarehouse"."analytics"."stg_transactions"
group by 1, 2
  );
  