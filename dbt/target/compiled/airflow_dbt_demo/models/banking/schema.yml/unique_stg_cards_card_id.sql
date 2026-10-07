
    
    

select
    card_id as unique_field,
    count(*) as n_records

from "datawarehouse"."analytics"."stg_cards"
where card_id is not null
group by card_id
having count(*) > 1


