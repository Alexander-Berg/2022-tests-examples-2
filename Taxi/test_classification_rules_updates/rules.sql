INSERT INTO classifier.rules (
    classifier_id,
    tariff_id,
    started_at,
    ended_at,
    is_allowing,
    brand,
    model,
    price_from,
    price_to,
    year_from,
    year_to,
    vehicle_before,
    updated_at
)
VALUES
(   
    'classifier_id_1',  -- classifier_id
    'tariff_id_1',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- ended_at
    TRUE,  -- is_allowing
    NULL,  -- brand
    NULL,  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL,   -- vehicle_before
    '2011-01-01T10:00:00'  -- updated_at
),
(   
    'classifier_id_2',  -- classifier_id
    'tariff_id_2',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- ended_at
    TRUE,  -- is_allowing
    NULL,  -- brand
    NULL,  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL,   -- vehicle_before
    '2012-01-01T10:00:00'  -- updated_at
),
(
    'classifier_id_3',  -- classifier_id
    'tariff_id_3',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- ended_at
    TRUE,  -- is_allowing
    NULL,  -- brand
    NULL,  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL,   -- vehicle_before
    '2013-01-01T10:00:00'  -- updated_at
),
(
    'classifier_id_4',  -- classifier_id
    'tariff_id_4',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- ended_at
    TRUE,  -- is_allowing
    NULL,  -- brand
    NULL,  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL,   -- vehicle_before
    '2014-01-01T10:00:00'  -- updated_at
),
(
    'classifier_id_5',  -- classifier_id
    'tariff_id_5',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- ended_at
    TRUE,  -- is_allowing
    NULL,  -- brand
    NULL,  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL,   -- vehicle_before
    '2015-01-01T10:00:00'  -- updated_at
),
(
    'classifier_id_6',  -- classifier_id
    'tariff_id_6',  -- tariff_id
    '2015-01-01T00:00:00+0000',  -- started_at
    '2015-01-01T00:00:00+0000',  -- ended_at
    TRUE,  -- is_allowing
    'McLaren',  -- brand
    'F1',  -- model
    3000000,  -- price_from
    6000000,  -- price_to
    1998,  -- year_from
    2025,  -- year_to
    '2015-01-01T00:00:00+0000',   -- vehicle_before
    '2016-01-01T10:00:00'  -- updated_at
),
(
    'classifier_id_7',  -- classifier_id
    'econom',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- ended_at
    TRUE,  -- is_allowing
    'AUDI',  -- brand
    'A*',  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL,   -- vehicle_before
    '2016-01-01T10:00:00' -- updated_at
),
(
    'classifier_id_8',  -- classifier_id
    'econom',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- ended_at
    TRUE,  -- is_allowing
    'bmw',  -- brand
    '*',  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL,   -- vehicle_before
    '2016-01-01T10:00:00' -- updated_at
),
(
    'classifier_id_9',  -- classifier_id
    'econom',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- ended_at
    TRUE,  -- is_allowing
    'Lada (Ваз)',  -- brand
    'к*',  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL,   -- vehicle_before
    '2016-01-01T10:00:00' -- updated_at
),
(
    'classifier_id_10',  -- classifier_id
    'econom',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- ended_at
    TRUE,  -- is_allowing
    'гАз',  -- brand
    'нн*',  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL,   -- vehicle_before
    '2016-01-01T10:00:00' -- updated_at
);
