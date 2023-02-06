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
    'p1',
    'd1',
    'idemp1',

    'feeds-admin-id-1',
    'some_id',
    'p1',
    
    '2.4',
    'RUB',

    'pending',
    NULL,

    NOW(),
    NOW()
);
