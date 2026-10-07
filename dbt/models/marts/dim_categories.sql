{{ config(materialized='table') }}

select
    id as category_id,
    name as category_name,
    description as category_description
from {{ source('raw', 'categories') }}
