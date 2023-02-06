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
    'success_park',
    'Success Park',
    TRUE,
    FALSE,
    1,
    TRUE,
    TRUE,
    '{"experiment_territory"}',
    1,
    1,
    '{"test_field": 1}'::jsonb
),
(
    'deleted_park',
    'Deleted Park',
    TRUE,
    TRUE,
    1,
    TRUE,
    TRUE,
    '{"experiment_territory"}',
    1,
    1,
    '{"test_field": 1}'::jsonb
)
;
