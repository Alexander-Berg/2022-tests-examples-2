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
    vehicle_before
)
VALUES
(   
    'classifier_id_1',  -- classifier_id
    'econom',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- endede_at
    FALSE,  -- is_allowing
    'BMW',  -- brand
    'X1',  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL   -- vehicle_before
),
(   
    'classifier_id_1',  -- classifier_id
    'econom',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- endede_at
    TRUE,  -- is_allowing
    'Pagani',  -- brand
    'Huayra',  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL   -- vehicle_before
),
(   
    'classifier_id_2',  -- classifier_id
    'econom_2',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- endede_at
    TRUE,  -- is_allowing
    'Pagani',  -- brand
    'Zonda',  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL   -- vehicle_before
),
(   
    'classifier_id_1',  -- classifier_id
    'vip',  -- tariff_id
    '2019-12-27T00:00:00+0000', -- started_at
    '2020-12-27T00:00:00+0000', -- endede_at
    TRUE,   -- is_allowing
    'Pagani', -- brand
    'Zonda',  -- model
    3000000,    -- price_from
    6000000,    -- price_to
    0,  -- year_from
    3,  -- year_to
    '2018-01-01T00:00:00+0000'  -- vehicle_before
);
