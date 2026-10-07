
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select card_id
from "datawarehouse"."analytics"."stg_cards"
where card_id is null



  
  
      
    ) dbt_internal_test