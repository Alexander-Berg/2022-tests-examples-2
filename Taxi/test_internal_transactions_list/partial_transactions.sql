INSERT INTO contractor_merch_payments.payments(
    id,
    idempotency_token,

    park_id,
    contractor_id,
    merchant_id,

    price,

    status,
    status_reason,

    integrator,

    created_at,
    updated_at
) VALUES (
    'payment_id-success-0',
    'idempotency_token-2',

    'park_id-1',
    'contractor_id-1',
    'merchant_id-1',

    '50',

    'success',
    NULL,

    'payments-bot',
    
    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
    'payment_id-success-2',
    'idempotency_token-3',

    'park_id-1',
    'contractor_id-1',
    'merchant_id-1',

    '100',

    'success',
    NULL,

    'payments-bot',
    
    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
    'payment_id-success-1',
    'idempotency_token-4',

    'park_id-2',
    'contractor_id-2',
    'merchant_id-1',

    '100',

    'success',
    NULL,

    'payments-bot',
    
    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
);

INSERT INTO contractor_merch_payments.transactions(
    id,
    idempotency_token,

    payment_id,
    amount,
    type,

    created_at,
    updated_at
) VALUES (
    'refund_id-1',
    'idempotency_token-1',

    'payment_id-success-1',
    '-20',
    'yandex_subsidy_refund',

    '2021-11-12T14:00:00Z'::timestamptz,
    NOW()
), (
    'refund_id-2',
    'idempotency_token-2',

    'payment_id-success-1',
    '-30',
    'yandex_subsidy_refund',

    '2021-11-12T15:00:00Z'::timestamptz,
    NOW()
);
