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
    '3f719db4-5d6b-5463-99a9-ac33e9ae5e17',
    'offer_name',
    'offer',
    TRUE,
    0,
    0,
    'token1',
    '2020-01-01T15:00:00+03:00',
    '2020-01-01T15:00:00+03:00',
    '2020-01-01T15:00:00+03:00'
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
    '3f719db4-5d6b-5463-99a9-ac33e9ae5e17',
    0,
    '2020-01-01T15:00:00+03:00'
);
