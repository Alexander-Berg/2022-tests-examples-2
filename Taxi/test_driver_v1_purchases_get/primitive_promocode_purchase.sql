INSERT INTO contractor_merch.feed_payloads_history (
        id,
        feed_id,
        locale,
        feed_payload,
        created_at
    )
VALUES (
    'unique_id-1',
    'feed_id-1',
    'en',
    '{
        "feeds_admin_id": "feeds-admin-id-1",
        "price": "200.0000",
        "category": "tire",
        "name": "Just an offer",
        "partner": {
            "name": "Apple"
        },
        "balance_payment": true,
        "title": "Gift card (tire)",
        "categories": ["tire"],
        "actions": [
          {
            "data": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "text": "Rick Astley",
            "type": "link"
          }
        ],
        "place_id": 1,
        "meta_info": {
            "daily_per_driver_limit": 1,
            "total_per_driver_limit": 2,
            "total_per_unique_driver_limit": 3,
            "barcode_params": {
                "is_send_enabled": true,
                "type": "ean13"
            }
        },
        "offer_id": "metric"
    }'::jsonb,
    NOW()
), (
    'unique_id-2',
    'feed_id-2',
    'en',
    '{
        "feeds_admin_id": "feeds-admin-id-2",
        "price": "150.0000",
        "category": "tire",
        "name": "KFC",
        "partner": {
            "name": "Apple"
        },
        "categories": ["tire"],
        "actions": [
          {
            "data": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "text": "Rick Astley",
            "type": "link"
          }
        ],
        "place_id": 1,
        "balance_payment": true,
        "title": "Gift card (tire)",
        "meta_info": {},
        "offer_id": "metric"
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
    'feeds_admin_id-1',
    'bought',
    '100/500',
    '2021-06-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:01Z'::timestamptz
), (
    'promocode_id-2',
    'feeds_admin_id-2',
    'bought',
    'PROMOCODE_NUMBER-1',
    '2021-06-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:01Z'::timestamptz
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
    'idempotency_token-1',
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

    'unique_id-1',

    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
), (
    'idempotency_token-2',
    'park_id-1',
    'driver_id-1',
    'idempotency_token-2',

    'feeds_admin_id-2',
    'feed_id-2',
    'promocode_id-2',

    '300',
    'RUB',

    'fulfilled',
    NULL,

    'unique_id-2',

    '2021-07-01T14:00:00Z'::timestamptz,
    '2021-07-01T14:00:00Z'::timestamptz
);
