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
    'park_0',
    'Park 0',
    TRUE,
    FALSE,
    1,
    TRUE,
    TRUE,
    '{"35"}',
    1,
    1,
    '{"db_id__c": "ddd", "GrantsRentalToSelfEmployed__c": true,"private_tariffs__c": ""}'::jsonb
),
(
    'park_1',
    'Park 1',
    TRUE,
    FALSE,
    1,
    TRUE,
    TRUE,
    '{"35"}',
    1,
    1,
    '{"db_id__c": "aaa", "GrantsRentalToSelfEmployed__c": true, "private_tariffs__c": "park_1;econom;comfort;comfort_plus;children;business","rent_tariffs__c": "park_1;econom;children"}'::jsonb
),
(
    'park_2',
    'Park 2',
    TRUE,
    FALSE,
    1,
    TRUE,
    TRUE,
    '{"35"}',
    1,
    1,
    '{"db_id__c": "ccc", "GrantsRentalToSelfEmployed__c": true,"private_tariffs__c": "park_2;econom;comfort;comfort_plus;children;business","rent_tariffs__c": "park_2;econom"}'::jsonb
),
(
    'park_3',
    'Park 3',
    TRUE,
    FALSE,
    1,
    TRUE,
    TRUE,
    '{"35"}',
    1,
    1,
    '{"db_id__c": "yyy", "GrantsRentalToSelfEmployed__c": false,"private_tariffs__c": "park_3;econom;comfort;comfort_plus;children;business","rent_tariffs__c": "park_3;econom"}'::jsonb
),
(
    'park_4',
    'Park 4',
    TRUE,
    FALSE,
    1,
    TRUE,
    TRUE,
    '{"101"}',
    1,
    1,
    '{"db_id__c": "kkk", "GrantsRentalToSelfEmployed__c": true,"private_tariffs__c": "park_4;econom"}'::jsonb
),
(
    'park_not_offers_rent',
    'Park not_offers_rent',
    TRUE,
    FALSE,
    1,
    FALSE,
    TRUE,
    '{"35"}',
    1,
    1,
    '{"db_id__c": "nnn", "GrantsRentalToSelfEmployed__c": true,"private_tariffs__c": "park_not_offers_rent;econom;comfort;comfort_plus;children;business","rent_tariffs__c": "park_not_offers_rent;econom"}'::jsonb
),
(
    'park_not_accepts_private_vehicles',
    'Park not_accepts_private_vehicles',
    TRUE,
    FALSE,
    1,
    TRUE,
    FALSE,
    '{"35"}',
    1,
    1,
    '{"db_id__c": "ttt", "GrantsRentalToSelfEmployed__c": true,"private_tariffs__c": "park_not_accepts_private_vehicles;econom;comfort;comfort_plus;children;business","rent_tariffs__c": "park_not_accepts_private_vehicles;econom"}'::jsonb
),
(
    'park_deleted',
    'Deleted Park',
    TRUE,
    TRUE,
    1,
    TRUE,
    TRUE,
    '{"35"}',
    1,
    1,
    '{"db_id__c": "vvv", "GrantsRentalToSelfEmployed__c": true,"private_tariffs__c": "deleted","rent_tariffs__c": "deleted"}'::jsonb
);

INSERT INTO hiring_taxiparks_gambling_salesforce.territories (
    sf_id,
    sf_name,
    is_deleted,
    rev,
    city_rus,
    region_id
)
VALUES
(
    'big_city',
    'big city',
    FALSE,
    1,
    'Большой город',
    '35'
),
(
    'some_region',
    'some city',
    FALSE,
    1,
    'Город с неуникальным region_id',
    '90'
),
(
    'some_region_dubl',
    'some city dubl',
    FALSE,
    1,
    'Город с неуникальным region_id дубль',
    '90'
),
(
    'city_without_parks',
    'city without parks',
    FALSE,
    1,
    'Город без парков',
    '75'
),
(
    'city_without_self_employed',
    'city without self employed',
    FALSE,
    1,
    'Город без саморегистрации',
    '101'
);
