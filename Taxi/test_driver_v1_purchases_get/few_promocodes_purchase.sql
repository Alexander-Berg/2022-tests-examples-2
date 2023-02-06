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
        "price": "123.0000",
        "category": "tire",
        "name": "SMZ",
        "partner": {
            "name": "Apple"
        },
        "balance_payment": true,
        "title": "Специальный оффер для СМЗ",
        "meta_info": {
            "is_offer_with_few_promocodes": true
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

    'available',

    '[{"number": "WSFWF151", "caption": "Макдоналдс"}, {"number": "WSFWF132", "caption": "Автомойка"}, {"number": "WSFWF21323", "caption": "Шаверма"}]',

    '2021-07-02T14:00:00Z'::timestamptz,
    '2021-07-02T14:00:00Z'::timestamptz
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

    '123.0000',
    'RUB',

    'fulfilled',
    NULL,

    'unique_id-1',

    '2021-07-02T14:00:00Z'::timestamptz,
    '2021-07-02T14:00:00Z'::timestamptz
);
