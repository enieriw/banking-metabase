
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    card_id as unique_field,
    count(*) as n_records

from "datawarehouse"."analytics"."stg_cards"
where card_id is not null
group by card_id
having count(*) > 1



  
  
      
    ) dbt_internal_test