
  create view "datawarehouse"."analytics"."stg_mcc_codes__dbt_tmp"
    
    
  as (
    select
    mcc_id,
    description as mcc_description
from "datawarehouse"."raw"."mcc_codes"
  );