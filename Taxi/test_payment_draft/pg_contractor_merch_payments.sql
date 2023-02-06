INSERT INTO contractor_merch_payments.payments(
    id,
    idempotency_token,

    park_id,
    contractor_id,
    merchant_id,

    price,
    status,

    created_at,
    updated_at
) VALUES (
    'payment_id-1',
    'payment_idempotency-token-1',

    'park-id-1',
    'contractor-id-draft-and-success',
    NULL,

    NULL,
    'draft',
    
    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:06Z'::timestamptz
), (
    'payment_id-2',
    'payment_idempotency-token-2',

    'park-id-1',
    'contractor-id-target_success',
    'merchant-id-2',

    '40',
    'target_success',
    
    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
), (
    'payment_id-3',
    'payment_idempotency-token-3',

    'park-id-1',
    'contractor-id-draft-and-success',
    'merchant-id-2',

    '40',
    'success',
    
    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
), (
    'payment_id-4',
    'payment_idempotency-token-4',

    'park-id-1',
    'contractor-id-contractor_declined',
    NULL,

    '500',
    'contractor_declined',
    
    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
);
