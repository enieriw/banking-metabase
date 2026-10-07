select
    mcc_id,
    description as mcc_description
from {{ source('banking_raw', 'mcc_codes') }}
