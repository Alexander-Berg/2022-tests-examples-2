INSERT INTO contractor_merch_payments.payments(
    id,
    idempotency_token,

    park_id,
    contractor_id,
    merchant_id,

    price,
    status,

    integrator,
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
    NULL,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-merchant_accepted',
    'payment_idempotency-token-3',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '40',
    'merchant_accepted',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-merchant_accepted-v2',
    'payment_idempotency-token-33',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '40',
    'merchant_accepted',

    'integration-api-mobi',
    NULL,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-target_success',
    'payment_idempotency-token-2',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '40',
    'target_success',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-target_failed',
    'payment_idempotency-token-target-failed',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '40',
    'target_failed',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-target_contractor_declined',
    'payment_idempotency-token-4',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '500',
    'target_contractor_declined',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-success',
    'payment_idempotency-token-success',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '40',
    'success',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-failed',
    'payment_idempotency-token-failed',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '40',
    'failed',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-contractor_declined',
    'payment_idempotency-token-contractor_declined',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '40',
    'contractor_declined',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-merchant_canceled',
    'payment_idempotency-token-merchant_canceled',

    'park-id-2',
    'contractor-id-5',
    'merchant-id-10',

    NULL,
    'merchant_canceled',

    NULL,
    NULL,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-merchant_accepted-v3',
    'payment_idempotency-token-45',

    'park-id-1',
    'contractor-id-1',
    'merchant-id-2',

    '40',
    'merchant_accepted',

    'integration-api-universal',
    NULL,
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
);
