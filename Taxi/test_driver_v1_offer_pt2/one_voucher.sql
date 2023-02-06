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

    feeds_payload_history_id,

    created_at,
    updated_at
) VALUES (
    'idemp1',
    'park_id',
    'driver_id',
    'idemp1',

    'feeds-admin-id-1',
    'feed-id-1',
    'promocode_id_1',

    '2.4',
    'RUB',

    'fulfilled',
    NULL,

    'unique_id_1',

    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
);
