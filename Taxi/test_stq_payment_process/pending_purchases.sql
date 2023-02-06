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
    'payment_idempotency-token-1',

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
    
    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
), (
    'payment_id-target_success',
    'payment_idempotency-token-2',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '40',
    'target_success',

    'with_approval',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
), (
    'payment_id-merchant_accepted2',
    'payment_idempotency-token-4',

    'park-id-1',
    'contractor-id-2',
    'merchant-id-2',

    '40',
    'merchant_accepted',

    'with_approval',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
), (
    'payment_id-success',
    'payment_idempotency-token-5',

    'park-id-1',
    'contractor-id-2',
    'merchant-id-2',

    '40',
    'success',

    'with_approval',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
)
