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
    fleet_type,
    extra
) VALUES
(
    'must_not_update',
    'MustNotUpdate',
    TRUE,
    FALSE,
    1,
    TRUE,
    FALSE,
    NULL,
    1,
    5,
    'taximeter',
    NULL
),
(
    'must_delete',
    'MustDelete',
    TRUE,
    FALSE,
    1,
    FALSE,
    TRUE,
    NULL,
    2,
    4,
    'taximeter',
    NULL
),
(
    'must_update',
    'MustUpdate',
    TRUE,
    FALSE,
    1,
    TRUE,
    TRUE,
    NULL,
    3,
    3,
    'taximeter',
    NULL
);

INSERT INTO hiring_taxiparks_gambling_salesforce.last_update (
    id,
    last_update,
    last_delete
) VALUES (
    1,
    '2019-01-01',
    '2019-01-01'
);

SELECT setval('hiring_taxiparks_gambling_salesforce.hiring_conditions_revision', 123);
