
      update "datawarehouse"."analytics"."source_data_snapshot"
    set dbt_valid_to = DBT_INTERNAL_SOURCE.dbt_valid_to
    from "source_data_snapshot__dbt_tmp101407792777" as DBT_INTERNAL_SOURCE
    where DBT_INTERNAL_SOURCE.dbt_scd_id::text = "datawarehouse"."analytics"."source_data_snapshot".dbt_scd_id::text
      and DBT_INTERNAL_SOURCE.dbt_change_type::text in ('update'::text, 'delete'::text)
      
        and "datawarehouse"."analytics"."source_data_snapshot".dbt_valid_to is null;
      


    insert into "datawarehouse"."analytics"."source_data_snapshot" ("id", "category_id", "name", "value", "status", "metadata", "created_at", "updated_at", "dbt_updated_at", "dbt_valid_from", "dbt_valid_to", "dbt_scd_id")
    select DBT_INTERNAL_SOURCE."id",DBT_INTERNAL_SOURCE."category_id",DBT_INTERNAL_SOURCE."name",DBT_INTERNAL_SOURCE."value",DBT_INTERNAL_SOURCE."status",DBT_INTERNAL_SOURCE."metadata",DBT_INTERNAL_SOURCE."created_at",DBT_INTERNAL_SOURCE."updated_at",DBT_INTERNAL_SOURCE."dbt_updated_at",DBT_INTERNAL_SOURCE."dbt_valid_from",DBT_INTERNAL_SOURCE."dbt_valid_to",DBT_INTERNAL_SOURCE."dbt_scd_id"
    from "source_data_snapshot__dbt_tmp101407792777" as DBT_INTERNAL_SOURCE
    where DBT_INTERNAL_SOURCE.dbt_change_type::text = 'insert'::text;

  