{% snapshot source_data_snapshot %}

{{
    config(
      target_database='datawarehouse',
      target_schema='analytics',
      unique_key='id',
      strategy='timestamp',
      updated_at='updated_at'
    )
}}

select * from {{ source('raw', 'source_data') }}

{% endsnapshot %}
