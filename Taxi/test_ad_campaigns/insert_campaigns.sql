INSERT INTO eats_restapp_marketing.advert
(   
    created_at,
    updated_at,
    place_id,
    campaign_id,
    group_id,
    ad_id,
    banner_id,
    is_active,
    averagecpc,
    started_at,
    suspended_at,
    experiment
)
VALUES
(NUll, NOW(), 1, 1, 1, 1, 1, True, 10 * 1000000, '2021-01-01 12:05:01.358114+03'::TIMESTAMPTZ, '2021-01-10 12:05:01.358514+03'::TIMESTAMPTZ, ''),
(NULL, NOW(), 2, 2, 2, 2, 2, True, 20 * 1000000, NULL, NULL, ''),
('2019-01-01 13:05:01.358114+03'::TIMESTAMPTZ, NOW(), 3, 3, 3, 3, 3, True, 30 * 1000000, '2020-01-01 13:05:01.358114+03'::TIMESTAMPTZ, NULL, ''),
(NULL, NOW(), 4, 1, 1, 1, 1, True, 10 * 1000000, NULL, NULL, ''),
(NULL, NOW(), 5, 2, 2, 2, 2, True, 20 * 1000000, NULL, NULL, ''),
(NULL, NOW(), 6, 3, 3, 3, 3, True, 30 * 1000000, NULL, NULL, ''),
(NUll, NOW(), 1, 1, 1, 1, 1, True, 30 * 1000000, '2021-01-01 12:05:01.358114+03'::TIMESTAMPTZ, '2021-01-10 12:05:01.358514+03'::TIMESTAMPTZ, 'foo_name_exp');
