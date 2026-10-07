
    
    

select
    mcc_id as unique_field,
    count(*) as n_records

from "datawarehouse"."analytics"."stg_mcc_codes"
where mcc_id is not null
group by mcc_id
having count(*) > 1


