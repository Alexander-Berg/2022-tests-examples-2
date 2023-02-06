INSERT INTO contractor_merch_payments.payments(
    id,
    idempotency_token,
    external_id,

    park_id,
    contractor_id,

    merchant_id,
    seller,

    price,
    status,

    integrator,
    metadata,

    created_at,
    updated_at
) VALUES (
    'payment_id-0',
    'payment_idempotency-token-0',
    'external_id-0',

    'park-id-0',
    'contractor-id-0',

    'merchant-id-0',
    NULL,

    '100',
    'success',

    'integration-api-mobi',
    NULL,
    
    NOW(),
    NOW()
), (
    'payment_id-1',
    'payment_idempotency-token-1',
    NULL,

    'park-id-1',
    'contractor-id-1',

    NULL,
    NULL,

    NULL,
    'draft',

    NULL,
    NULL,
    
    NOW(),
    NOW()
), (
    'payment_id-2',
    'payment_idempotency-token-2',
     NULL,

    'park-id-2',
    'contractor-id-2',

    'merchant-id-2',
    NULL,

    '250',
    'target_success',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    NOW(),
    NOW()
), (
    'payment_id-3',
    'payment_idempotency-token-3',
     NULL,

    'park-id-1',
    'contractor-id-1',

    'merchant-id-4',
    NULL,

    '40',
    'target_success',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    NOW(),
    NOW()
), (
    'payment_id-4',
    'payment_idempotency-token-4',
     NULL,

    'park-id-3',
    'contractor-id-1',

    'merchant-id-4',
    NULL,

    '500',
    'contractor_declined',

    'payments-bot',
    '{
        "telegram_chat_id": 0,
        "telegram_personal_id": "telegram-personal-id-0"
    }'::jsonb,
    
    NOW(),
    NOW()
), (
    'payment_id-5',
    'payment_idempotency-token-5',
     NULL,

    'park-id-5',
    'contractor-id-5',

    'merchant-id-5',
    NULL,

    NULL,
    'draft',

    NULL,
    NULL,

    NOW(),
    NOW()
), (
    'payment_id-6',
    'payment_idempotency-token-6',
     NULL,

    'park-id-6',
    'contractor-id-6',

    'merchant-id-6',
    ROW('Пятёрочка', 'Москва, ул. Пушкина, д. Колотушкина'),

    '200',
    'target_success',

    'integration-api-mobi',
    NULL,

    NOW(),
    NOW()
), (
    'payment_id-7',
    'payment_idempotency-token-7',
     NULL,

    'park-id-7',
    'contractor-id-7',

    NULL,
    NULL,

    NULL,
    'draft',

    NULL,
    NULL,
    
    NOW() - INTERVAL '500' SECOND,
    NOW() - INTERVAL '200' SECOND
), (
    'payment_id-8',
    'payment_idempotency-token-8',
     NULL,

    'park-id-8',
    'contractor-id-8',

    NULL,
    NULL,

    NULL,
    'draft',

    NULL,
    NULL,
    
    NOW(),
    NOW()
), (
    'payment_id-9',
    'payment_idempotency-token-9',
     NULL,

    'park-id-4',
    'contractor-id-4',

    NULL,
    NULL,

    NULL,
    'draft',

    NULL,
    NULL,
    
    NOW(),
    NOW()
), (
    'payment_id-10',
    'payment_idempotency-token-10',
     NULL,

    'park-id-9',
    'contractor-id-9',

    'merchant-id-9',
    NULL,

    '500',
    'merchant_accepted',

    'payments-bot',
    '{
        "telegram_chat_id": 124,
        "telegram_personal_id": "telegram-personal-id-10"
    }'::jsonb,
    
    NOW(),
    NOW()
), (
    'payment_id-11',
    'payment_idempotency-token-11',
     NULL,

    'park-id-11',
    'contractor-id-11',

    'merchant-id-11',
    NULL,

    NULL,
    'merchant_canceled',

    'integration-api-mobi',
    NULL,
    
    NOW(),
    NOW()
), (
    'payment_id-12',
    'payment_idempotency-token-12',
     NULL,

    'park-id-12',
    'contractor-id-12',

    NULL,
    NULL,

    NULL,
    'draft',

    NULL,
    NULL,
    
    NOW(),
    NOW()
);
