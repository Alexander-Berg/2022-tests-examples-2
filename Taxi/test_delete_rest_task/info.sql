INSERT INTO place_groups(
    place_group_id,
    brand_id,
    parser_name,
    parser_hours,
    price_parser_times,
    stock_reset_limit,
    dev_filter
)
VALUES
(
    'place_group_id1',
    'brand_id',
    'parser_name',
    '09:00',
    '9:20',
    1,
    '{"elem": 2}'::json
);

INSERT INTO places(
    place_id,
    place_group_id,
    business_type,
    brand_id,
    external_id
)
VALUES
(
    'place1',
    'place_group_id1',
    'restaurant',
    'brand_id',
    'external_place_id1'
),
(
    'place2',
    'place_group_id1',
    'shop',
    'brand_id',
    'external_place_id1'
);

INSERT INTO integration_tasks(
    id,
    place_id,
    type,
    status,
    created_at,
    updated_at
)
VALUES
(
    '7511b40f-c1b8-5deb-0000-2a80f85e0204',
    'place1',
    'stock',
    'finished',
    '2019-08-19 10:00:00',
    '2019-08-19 10:00:00'
),
(
    '7511b40f-c1b8-5deb-0000-2a80f85e0203',
    'place2',
    'stock',
    'finished',
    '2019-08-19 10:00:00',
    '2019-08-19 10:00:00'
);
