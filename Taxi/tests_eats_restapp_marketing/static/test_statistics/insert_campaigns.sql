INSERT INTO eats_restapp_marketing.advert
(
    updated_at,
    place_id,
	averagecpc,
    campaign_id,
    ad_id,
    content_id,
    banner_id,
    is_active,
    passport_id,
    error
)
VALUES
    (NOW() - INTERVAL '1000 DAYS',      1, 10, NULL, 11,   NULL, NULL, TRUE,  11,   NULL),
    (NOW(),                             2, 10, NULL, 22,   NULL, 4527, TRUE,  12,   'Bad long error'),
    (NOW() - INTERVAL '100 DAYS',       3, 10, NULL, NULL, NULL, NULL, TRUE,  13,   NULL),
    (NOW(),                             4, 10, NULL, NULL, NULL, NULL, FALSE, 14,   NULL),
    (NOW() - INTERVAL '10 HOURS',       5, 10, NULL, 55,   NULL, 1552, FALSE, 15,   'Short err'),
    (DATE(NOW()) - INTERVAL '31 DAYS',  6, 10, NULL, 66,   NULL, 7123, FALSE, 16,   NULL),
    (NOW(),                             7, 10, NULL, 77,   NULL, 6124, TRUE,  17,   ''), -- Error with empty message
    (NOW() - INTERVAL '3 DAYS',         8, 10, 1234, 88,   2345, NULL, TRUE,  18,   'Some old error'),
    (NOW() - INTERVAL '23 HOURS',       9, 10, NULL, 99,   NULL, 2873, FALSE, NULL, ''), -- Also empty message error
    (NOW(),                            10, 10, 1234, 89,   NULL, NULL, FALSE, NULL, NULL),
    (NOW(),                            11, 10, NULL, 90,   NULL, NULL, FALSE, NULL, NULL);

INSERT INTO eats_restapp_marketing.advert_for_create
(
    updated_at,
    creation_started,
    advert_id,
    token_id,
    averagecpc
)
VALUES
       -- не попадают в метрику
    (NOW(), false, 1, 111, 25000000),
    ((NOW() - '23 hour'::interval), false, 2, 222, 25000000),
    ((NOW() - '23 hour'::interval), true, 3, 333, 25000000),
       -- попадают, но значения creation_started = true
    ((NOW() - '25 hour'::interval), true, 4, 444, 25000000),
    ((NOW() - '5 days'::interval), true, 5, 555, 25000000),
       -- попадают
    ((NOW() - '25 hour'::interval), false, 6, 666, 25000000),
    ((NOW() - '3 days'::interval), false, 7, 777, 25000000),
    ((NOW() - '6 days'::interval), false, 8, 888, 25000000);


INSERT INTO eats_restapp_marketing.keywords (keyword_id, keyword, advert_id, status, state)
VALUES
    (1, NULL, 1, 'draft', 'on'),
    (2, NULL, 1, 'accepted', 'suspended'),
    (3, NULL, 1, 'accepted', 'off'),
    (4, NULL, 2, 'draft', 'off'),
    (5, NULL, 2, 'accepted', 'on'),
    (6, NULL, 3, 'rejected', 'off'),
    (7, NULL, 3, 'rejected', 'on'),
    (8, NULL, 4, 'rejected', 'off'),
    (9, NULL, 4, 'rejected', 'suspended'),
    (10, NULL, 4, 'unknown', 'off');

