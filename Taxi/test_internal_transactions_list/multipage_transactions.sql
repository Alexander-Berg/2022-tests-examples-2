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
    'payment_id-draft',
    'idempotency_token-1',

    'park_id-1',
    'contractor_id-1',
    NULL,

    NULL,

    'draft',
    NULL,

    'payments-bot',
    
    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
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
    'payment_id-failed-0',
    'idempotency_token-3',

    'park_id-1',
    'contractor_id-1',
    'merchant_id-2',

    '100',

    'failed',
    'not_enough_money_on_drivers_balance',

    'payments-bot',
    
    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
    'payment_id-contractor_declined',
    'idempotency_token-4',

    'park_id-1',
    'contractor_id-1',
    'merchant_id-1',

    '150',

    'contractor_declined',
    NULL,

    'payments-bot',
    
    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
    'payment_id-merchant_canceled',
    'idempotency_token-5',

    'park_id-1',
    'contractor_id-1',
    'merchant_id-1',

    '120',

    'merchant_canceled',
    NULL,

    'payments-bot',
    
    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
    'payment_id-merchant_canceled_draft',
    'idempotency_token-6',

    'park_id-1',
    'contractor_id-1',
    'merchant_id-3',

    NULL,

    'merchant_canceled',
    NULL,

    'payments-bot',
    
    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
    'payment_id-success-1',
    'idempotency_token-7',

    'park_id-1',
    'contractor_id-1',
    'merchant_id-2',

    '100',

    'success',
    NULL,

    'payments-bot',
    
    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
    'payment_id-success-2',
    'idempotency_token-8',

    'park_id-2',
    'contractor_id-2',
    'merchant_id-2',

    '100',

    'success',
    NULL,

    'payments-bot',
    
    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
    'payment_id-failed-1',
    'idempotency_token-9',

    'park_id-1',
    'contractor_id-1',
    'merchant_id-2',

    '150',

    'failed',
    'not_enough_money_on_drivers_balance',

    'payments-bot',
    
    '2021-11-12T14:00:00Z'::timestamptz,
    NOW()
), (
    'payment_id-success-3',
    'idempotency_token-10',

    'park_id-1',
    'contractor_id-1',
    'merchant_id-5',

    '200',

    'success',
    NULL,

    'payments-bot',
    
    '2021-11-12T22:00:00Z'::timestamptz,
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

    'payment_id-success-0',
    '-20',
    'yandex_subsidy_refund',

    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
    'refund_id-3',
    'idempotency_token-3',

    'payment_id-success-1',
    '-80',
    'yandex_subsidy_refund',

    '2021-11-12T14:00:00Z'::timestamptz,
    NOW()
), (
    'refund_id-2',
    'idempotency_token-2',

    'payment_id-success-0',
    '-10',
    'yandex_subsidy_refund',

    '2021-11-12T14:00:00Z'::timestamptz,
    NOW()
), (
    'refund_id-4',
    'idempotency_token-4',

    'payment_id-success-3',
    '-60',
    'yandex_subsidy_refund',

    '2021-11-12T14:00:00Z'::timestamptz,
    NOW()
), (
    'refund_id-5',
    'idempotency_token-5',

    'payment_id-success-2',
    '-60',
    'yandex_subsidy_refund',

    '2021-11-12T15:00:00Z'::timestamptz,
    NOW()
), (
    'refund_id-6',
    'idempotency_token-6',

    'payment_id-success-3',
    '-60',
    'yandex_subsidy_refund',

    '2021-11-12T15:00:00Z'::timestamptz,
    NOW()
);
