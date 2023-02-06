INSERT INTO contractor_merch.promocodes (
  id,
  feeds_admin_id,
  status,
  number,
  created_at,
  updated_at
) VALUES (
    'p1',
    'feeds-admin-id-1',
    'available',
    '100500',
    NOW(),
    NOW()
);

INSERT INTO contractor_merch.vouchers(
    id,
    park_id,
    driver_id,
    idempotency_token,
    
    feeds_admin_id,
    feed_id,
    promocode_id,

    price,
    currency,

    status,
    status_reason,

    created_at,
    updated_at
) VALUES (
    'idemp1',
    'park_id',
    'one_offer_total_limit_excceded',
    'idemp1',

    'feeds-admin-id-1',
    'some_id',
    'p1',

    '2.4',
    'RUB',

    'fulfilled',
    NULL,

    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
),
(
    'idemp2',
    'park_id',
    'driver_has_pending_purchases',
    'idemp2',

    'feeds-admin-id-1',
    'some_id',
    'p1',

    '2.4',
    'RUB',

    'pending',
    NULL,

    NOW(),
    NOW()
),
(
    'idemp1',
    'park_id2',
    'some_driver',
    'idemp1',

    'feeds-admin-id-1',
    'some_id',
    'p2',
    
    '2.4',
    'RUB',

    'pending',
    NULL,

    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
);
