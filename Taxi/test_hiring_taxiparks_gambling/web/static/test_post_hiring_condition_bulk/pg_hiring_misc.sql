INSERT INTO hiring_taxiparks_gambling_salesforce.hiring_conditions (
    sf_id,
    sf_name,
    is_acquisition,
    is_deleted,
    rev,
    offers_rent,
    accepts_private_vehicles,
    hiring_territories,
    weight_rent,
    weight_private,
    extra
)
VALUES
(
    'park_1',
    'Park 1',
    TRUE,
    FALSE,
    1,
    TRUE,
    TRUE,
    '{"experiment_territory"}',
    1,
    1,
    '{"park_id": 1}'::jsonb
),
(
    'park_2',
    'Park 2',
    TRUE,
    FALSE,
    1,
    TRUE,
    TRUE,
    '{"experiment_territory"}',
    1,
    1,
    '{"park_id": 2}'::jsonb
),
(
    'park_3',
    'Deleted Park',
    TRUE,
    TRUE,
    1,
    TRUE,
    TRUE,
    '{"experiment_territory"}',
    1,
    1,
    '{"park_id": 3}'::jsonb
)
;
