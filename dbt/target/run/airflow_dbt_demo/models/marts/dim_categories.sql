
  
    

  create  table "datawarehouse"."analytics"."dim_categories__dbt_tmp"
  
  
    as
  
  (
    

select
    id as category_id,
    name as category_name,
    description as category_description
from "datawarehouse"."raw"."categories"
  );
  