INSERT INTO contractor_merch.feed_payloads_history (
        id,
        feed_id,
        locale,
        feed_payload,
        created_at
    )
VALUES (
    'unique_id_1',
    'feed-id-1',
    'en',
    '{
        "feeds_admin_id": "feeds-admin-id-1",
        "price": "123.0000",
        "category": "tire",
        "name": "RRRR",
        "partner": {
            "name": "Apple"
        },
        "balance_payment": true,
        "title": "Специальный оффер для СМЗ",
        "meta_info": {
            "priority_params": {
                "duration_minutes": 60,
                "tag_name": "gold"
          }
        }
    }'::jsonb,
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
    'idemp1',
    'park_id',
    'driver_id',
    'idemp1',

    'feeds-admin-id-1',
    'feed-id-1',
    NULL,

    '123.0000',
    'RUB',

    'fulfilled',
    NULL,

    'unique_id_1',

    '2021-07-02T14:00:00Z'::timestamptz,
    '2021-07-02T14:00:00Z'::timestamptz
);

INSERT INTO contractor_merch.feed_payloads_history (
        id,
        feed_id,
        locale,
        feed_payload,
        created_at
    )
VALUES (
    'unique_id_2',
    'feed-id-2',
    'en',
    '{
        "feeds_admin_id": "feeds-admin-id-2",
        "price": "123.0000",
        "category": "tire",
        "name": "RRRR",
        "partner": {
            "name": "Apple"
        },
        "balance_payment": true,
        "title": "Gift card (tire)",
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
    'promocode_id_2',
    'feeds-admin-id-2',
    'bought',
    'Very_good_promocode',
    '2021-07-02T14:00:00Z'::timestamptz,
    '2021-07-02T14:00:01Z'::timestamptz
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
    'idemp2',
    'park_id',
    'driver_id',
    'idemp2',

    'feeds-admin-id-2',
    'feed-id-2',
    'promocode_id_2',

    '123.0000',
    'RUB',

    'fulfilled',
    NULL,

    'unique_id_2',

    '2021-07-02T14:00:00Z'::timestamptz,
    '2021-07-02T14:00:00Z'::timestamptz
);

