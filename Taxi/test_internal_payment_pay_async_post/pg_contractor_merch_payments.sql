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
    'payment_id-1',
    'payment_idempotency-token-1',

    'park-id-1',
    'contractor-id-1',
    NULL,

    NULL,
    'draft',

    NULL,
    NULL,
    
    NOW(),
    NOW()
);
