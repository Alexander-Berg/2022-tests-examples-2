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
    'payment_id-draft',
    'payment_idempotency-token-1',

    'park-id-1',
    'contractor-id-1',
    NULL,

    NULL,
    'draft',

    NULL,
    
    NOW(),
    NOW()
), (
    'payment_id-target_success',
    'payment_idempotency-token-2',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '50',
    'target_success',

    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    NOW(),
    NOW()
), (
    'payment_id-success',
    'payment_idempotency-token-3',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '40',
    'success',

    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    NOW(),
    NOW()
);


INSERT INTO contractor_merch_payments.transactions (
    id,
    idempotency_token,

    payment_id,
    metadata,
    amount,
    type, 

    created_at,
    updated_at
) VALUES (
    'refund-id',
    'idempotency_token-0123456789',

    'payment_id-target_success',
    '{
        "mobi_id": "123"
    }'::jsonb,
    '-10',
    'yandex_subsidy_refund',

    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
);
