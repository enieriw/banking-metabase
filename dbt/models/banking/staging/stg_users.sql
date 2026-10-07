select
    id as user_id,
    current_age,
    retirement_age,
    birth_year,
    birth_month,
    gender,
    address,
    cast(latitude as double precision) as latitude,
    cast(longitude as double precision) as longitude,
    per_capita_income,
    yearly_income,
    total_debt,
    credit_score,
    num_credit_cards
from {{ source('banking_raw', 'users') }}
