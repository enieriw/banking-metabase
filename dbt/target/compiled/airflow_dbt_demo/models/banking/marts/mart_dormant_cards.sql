select
    c.card_id,
    c.user_id,
    c.card_brand,
    c.card_type,
    c.acct_open_date,
    count(t.transaction_id) as txn_count,
    min(t.transaction_at) as first_transaction_at,
    max(t.transaction_at) as last_transaction_at,
    count(t.transaction_id) = 0 as is_dormant
from "datawarehouse"."analytics"."stg_cards" c
left join "datawarehouse"."analytics"."stg_transactions" t on t.card_id = c.card_id
group by 1, 2, 3, 4, 5