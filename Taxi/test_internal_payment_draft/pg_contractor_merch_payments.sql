INSERT INTO contractor_merch_payments.payments(
    id,
    idempotency_token,

    park_id,
    contractor_id,
    merchant_id,

    price,
    status,

    method,

    integrator,
    metadata,

    created_at,
    updated_at
) VALUES (
    'payment_id-merchant_accepted',
    'payment_idempotency-token-3',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '40',
    'merchant_accepted',

    'with_approval',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
);
