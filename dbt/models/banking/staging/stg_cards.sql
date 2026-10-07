select
    id as card_id,
    client_id as user_id,
    card_brand,
    card_type,
    expires as expires_at,
    upper(has_chip) = 'YES' as has_chip,
    num_cards_issued,
    credit_limit,
    acct_open_date,
    year_pin_last_changed
from {{ source('banking_raw', 'cards') }}
