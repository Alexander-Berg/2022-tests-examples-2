INSERT INTO contractor_merch.feed_payloads_history (
    id,
    feed_id,
    locale,
    feed_payload,
    created_at
) VALUES (
    'feed_payload_id-1',
    'feed_id-1',
    'en-GB',
    '{
        "feeds_admin_id": "feeds-admin-id-1",
        "price": "200.0000",
        "category": "tire",
        "name": "Iphone 13 PRO Max",
        "partner": {
            "name": "Apple"
        },
        "balance_payment": true,
        "title": "Iphone 13 PRO Max",
        "meta_info": {
            "daily_per_driver_limit": 1,
            "total_per_driver_limit": 2,
            "total_per_unique_driver_limit": 3,
            "barcode_params": {
                "is_send_enabled": true,
                "type": "ean13"
            }
        }
    }'::jsonb,
    NOW()
);

INSERT INTO contractor_merch.promocodes (
  id,
  feeds_admin_id,
  status,
  number,
  created_at,
  updated_at
) VALUES (
    'promocode_id-1',
    'feeds_admin_id',
    'bought',
    'PROMOCODE1',
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

    feeds_payload_history_id,

    created_at,
    updated_at
) VALUES (
    'voucher_id-1',
    'park_id-1',
    'driver_id-1',
    'idempotency_token-1',

    'feeds_admin_id-1',
    'feed_id-1',
    'promocode_id-1',

    '2.4',
    'RUB',

    'fulfilled',
    NULL,

    'feed_payload_id-1',

    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
    'voucher_id-2',
    'park_id-1',
    'driver_id-1',
    'idempotency_token-2',

    'feeds_admin_id-1',
    'feed_id-1',
    'promocode_id-1',

    '2.4',
    'RUB',

    'fulfilled',
    NULL,

    'feed_payload_id-1',

    '2021-11-12T17:00:00Z'::timestamptz,
    NOW()
), (
    'zvoucher_id-2',
    'park_id-1',
    'driver_id-1',
    'idempotency_token-3',

    'feeds_admin_id-1',
    'feed_id-1',
    'promocode_id-1',

    '2.4',
    'RUB',

    'fulfilled',
    NULL,

    'feed_payload_id-1',

    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
), (
    'avoucher_id-2',
    'park_id-1',
    'driver_id-1',
    'idempotency_token-4',

    'feeds_admin_id-1',
    'feed_id-1',
    'promocode_id-1',
    
    '2.4',
    'RUB',

    'fulfilled',
    NULL,

    'feed_payload_id-1',

    '2021-11-12T13:00:00Z'::timestamptz,
    NOW()
);
