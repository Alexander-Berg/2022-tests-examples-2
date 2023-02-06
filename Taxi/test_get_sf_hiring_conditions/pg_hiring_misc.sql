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
) VALUES
(
    'rent_park',
    'Rent Park',
    TRUE,
    FALSE,
    1,
    TRUE,
    FALSE,
    '{"some_territory"}',
    2,
    1,
    '{
        "is_paid_acquisition_rent__c": true,
        "GrantsRentalToSelfEmployed__c": false
    }'::jsonb
),
(
    'rent_park_2',
    'Rent Park 2',
    TRUE,
    FALSE,
    1,
    TRUE,
    FALSE,
    '{"some_territory"}',
    2,
    1,
    '{
        "is_paid_acquisition_rent__c": true,
        "GrantsRentalToSelfEmployed__c": false
    }'::jsonb
),
(
    'private_park',
    'Private Park',
    TRUE,
    FALSE,
    1,
    FALSE,
    TRUE,
    '{"some_territory"}',
    1,
    2,
    '{
        "is_paid_acquisition_private__c": true,
        "GrantsRentalToSelfEmployed__c": true
    }'::jsonb
),
(
    'rent_and_private_park',
    'Rent & Private Park',
    TRUE,
    FALSE,
    1,
    TRUE,
    TRUE,
    '{"some_territory"}',
    2,
    1,
    '{
        "Address__c": "some",
        "DispatchPhone__c": "some",
        "LinkToGarageAd__c": "some",
        "is_paid_acquisition_rent__c": true,
        "GrantsRentalToSelfEmployed__c": true,
        "is_paid_acquisition_private__c": true
    }'::jsonb
),
(
    'excluded_park',
    'Excluded Park',
    TRUE,
    FALSE,
    1,
    TRUE,
    FALSE,
    '{"some_territory"}',
    1,
    1,
    NULL
),
(
    'other_territory_park',
    'Other Territory Park',
    TRUE,
    FALSE,
    1,
    TRUE,
    FALSE,
    '{"other_territory"}',
    1,
    1,
    '{
        "is_paid_acquisition_rent__c": true,
        "GrantsRentalToSelfEmployed__c": true
    }'::jsonb
);
