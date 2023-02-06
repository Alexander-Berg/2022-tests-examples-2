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
    'Москва',  -- classifier_id
    'econom',  -- tariff_id
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
),
(   
    'Москва',  -- classifier_id
    'econom',  -- tariff_id
    NULL,  -- started_at
    NULL,  -- endede_at
    TRUE,  -- is_allowing
    NULL,  -- brand
    NULL,  -- model
    NULL,  -- price_from
    NULL,  -- price_to
    NULL,  -- year_from
    NULL,  -- year_to
    NULL   -- vehicle_before
);
