INSERT INTO
    fleet_offers.active_offers (
        park_id,
        id,
        name,
        kind,
        is_enabled,
        rev,
        base_rev,
        idempotency_token,
        created_at,
        updated_at,
        published_at
    )
VALUES (
    'park1',
    '00000000-0000-0000-0000-000000000001',
    'offer1',
    'offer',
    TRUE,
    2,
    0,
    'token1',
    '2020-01-01T00:00:00+03:00',
    '2020-01-01T00:00:00+03:00',
    '2020-01-01T00:00:00+03:00'
);
 
INSERT INTO
    fleet_offers.offers (
        park_id,
        id,
        rev,
        created_at
    )
VALUES (
    'park1',
    '00000000-0000-0000-0000-000000000001',
    0,
    '2020-01-01T12:00:00+03:00'
), (
    'park1',
    '00000000-0000-0000-0000-000000000001',
    1,
    '2020-02-01T12:00:00+03:00'
), (
    'park1',
    '00000000-0000-0000-0000-000000000001',
    2,
    '2020-03-01T12:00:00+03:00'
);
