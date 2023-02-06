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
), (
    'park1',
    '00000000-0000-0000-0000-000000000002',
    'offer2',
    'offer',
    TRUE,
    2,
    0,
    'token2',
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
    '2020-01-01T00:00:00+03:00'
), (
    'park1',
    '00000000-0000-0000-0000-000000000001',
    1,
    '2020-01-01T00:00:00+03:00'
), (
    'park1',
    '00000000-0000-0000-0000-000000000001',
    2,
    '2020-01-01T00:00:00+03:00'
), (
    'park1',
    '00000000-0000-0000-0000-000000000002',
    0,
    '2020-01-01T00:00:00+03:00'
);
 
INSERT INTO
    fleet_offers.accepted_offers (
        park_id,
        id,
        client_id,
        rev,
        number,
        passport_pd_id,
        created_at,
        updated_at
    )
VALUES (
    'park1',
    '00000000-0000-0000-0000-000000000001',
    'driver1',
    1,
    1,
    'pd_id1',
    '2020-01-01T00:00:00+03:00',
    '2020-01-01T00:00:00+03:00'
);

INSERT INTO
    fleet_offers.offer_numbers_seq (
        park_id,
        offer_id,
        last_number
    )
VALUES (
    'park1',
    '00000000-0000-0000-0000-000000000001',
    100
), (
    'park1',
    '00000000-0000-0000-0000-000000000002',
    200
);
