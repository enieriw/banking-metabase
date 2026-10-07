
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select mcc_id
from "datawarehouse"."analytics"."stg_mcc_codes"
where mcc_id is null



  
  
      
    ) dbt_internal_test