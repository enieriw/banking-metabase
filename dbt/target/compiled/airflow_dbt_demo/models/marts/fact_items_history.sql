

with item_history as (
    select * from "datawarehouse"."analytics"."source_data_snapshot"
),

categories as (
    select * from "datawarehouse"."analytics"."dim_categories"
)

select
    h.dbt_scd_id as fact_id,
    h.id as item_id,
    h.name as item_name,
    h.value,
    h.status,
    h.metadata,
    h.category_id,
    c.category_name,
    h.dbt_valid_from as valid_from,
    h.dbt_valid_to as valid_to,
    case when h.dbt_valid_to is null then true else false end as is_active
from item_history h
left join categories c on h.category_id = c.category_id