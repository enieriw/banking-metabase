
  create view "datawarehouse"."analytics"."stg_transactions__dbt_tmp"
    
    
  as (
    select
    id as transaction_id,
    "date" as transaction_at,
    client_id as user_id,
    card_id,
    amount,
    use_chip as transaction_method,
    merchant_id,
    merchant_city,
    merchant_state,
    zip as merchant_zip,
    mcc as mcc_id,
    nullif(trim(errors), '') as error_message,
    coalesce(trim(errors), '') <> '' as is_failed
from "datawarehouse"."raw"."transactions"
  );