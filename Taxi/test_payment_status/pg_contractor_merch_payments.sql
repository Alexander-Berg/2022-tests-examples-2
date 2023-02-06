INSERT INTO contractor_merch_payments.payments(
    id,
    idempotency_token,

    park_id,
    contractor_id,

    merchant_id,
    seller,

    price,

    status,
    status_reason,

    integrator,

    created_at,
    updated_at
) VALUES (
    'payment_id-draft',
    'payment_idempotency-token-1',

    'park-id-1',
    'contractor-id-1',

    NULL,
    NULL,

    NULL,

    'draft',
    NULL,

    'payments-bot',
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-merchant_accepted',
    'payment_idempotency-token-3',

    'park-id-1',
    'contractor-id-1',

    'merchant-id-2',
    ROW('Пятёрочка', 'Москва, ул. Пушкина, д. Колотушкина'),

    '40',

    'merchant_accepted',
    NULL,

    'payments-bot',
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-merchant_canceled',
    'payment_idempotency-token-merchant_canceled',

    'park-id-5',
    'contractor-id-10',

    'merchant-id-5',
    NULL,

    NULL,

    'merchant_canceled',
    NULL,

    'payments-bot',
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-target_success',
    'payment_idempotency-token-2',

    'park-id-2',
    'contractor-id-2',

    'merchant-id-2',
    NULL,

    '40',

    'target_success',
    NULL,

    'payments-bot',
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-target_failed',
    'payment_idempotency-token-target_failed',

    'park-id-2',
    'contractor-id-2',

    'merchant-id-2',
    NULL,

    '40',

    'target_failed',
    NULL,

    'integration-api-mobi',
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-target_contractor_declined',
    'payment_idempotency-token-target_contractor_declined',

    'park-id-2',
    'contractor-id-2',

    'merchant-id-2',
    NULL,

    '40',

    'target_contractor_declined',
    NULL,
    
    'payments-bot',

    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-success',
    'payment_idempotency-token-5',

    'park-id-3',
    'contractor-id-1',

    'merchant-id-1',
    NULL,

    '500',
    
    'success',
    NULL,
    
    'payments-bot',

    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-failed',
    'payment_idempotency-token-6',

    'park-id-3',
    'contractor-id-1',

    'merchant-id-1',
    NULL,

    '500',

    'failed',
    NULL,
    
    'integration-api-mobi',

    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-contractor_declined',
    'payment_idempotency-token-4',

    'park-id-3',
    'contractor-id-1',

    'merchant-id-1',
    NULL,

    '500',

    'contractor_declined',
    NULL,
    
    'payments-bot',

    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
), (
    'payment_id-cannot_buy',
    'payment_idempotency-token-cannot_buy',

    'park-id-3',
    'contractor-id-1',

    'merchant-id-1',
    NULL,

    '500',

    'failed',
    'park_has_not_enough_money',
    
    'integration-api-mobi',
    
    '2021-11-12T12:00:00Z'::timestamptz,
    '2021-11-12T12:00:00Z'::timestamptz
);
