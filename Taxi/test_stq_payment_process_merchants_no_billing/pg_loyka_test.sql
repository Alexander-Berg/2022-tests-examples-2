INSERT INTO contractor_merch_payments.payments(
    id,
    idempotency_token,

    park_id,
    contractor_id,
    merchant_id,

    price,
    status,

    metadata,

    created_at,
    updated_at
) VALUES (
    'payment_id-merchant_accepted-2',
    'payment_idempotency-token-2',

    'park-id-2',
    'contractor-id-2',
    'loyka',

    '100',
    'merchant_accepted',

    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
)
