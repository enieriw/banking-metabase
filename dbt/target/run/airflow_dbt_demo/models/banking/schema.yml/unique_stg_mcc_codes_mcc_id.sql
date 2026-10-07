
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

select
    mcc_id as unique_field,
    count(*) as n_records

from "datawarehouse"."analytics"."stg_mcc_codes"
where mcc_id is not null
group by mcc_id
having count(*) > 1



  
  
      
    ) dbt_internal_test