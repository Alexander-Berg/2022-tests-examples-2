insert into place_groups
(
    place_group_id,
    brand_id,
    parser_name,
    stock_reset_limit,
    dev_filter,

    created_at,
    updated_at
)
values
(
    'place_group_id1',
    'brand1',
    'parser_name',
    1,
    '{"elem": 1}'::json,
    '2021-08-19 10:00:00',
    '2021-08-19 10:00:00'
),

(
    'place_group_id2',
    'brand2',
    'parser_name2',
    2,
    '{"elem": 2}'::json,
    '2021-08-19 10:00:00',
    '2021-08-19 10:00:00'
)
;

insert into places
(
    place_id,
    place_group_id,
    external_id,
    created_at,
    updated_at
)
values
(
    'id1',
    'place_group_id1',
    'external_id1',
    '2021-08-19 10:00:00',
    '2021-08-19 10:00:00'
),
(
    'id2',
    'place_group_id1',
    'external_id2',
    '2021-08-19 10:00:01',
    '2021-08-19 10:00:00'
),
(
    'id3',
    'place_group_id2',
    'external_id3',
    '2021-08-19 10:00:02',
    '2021-08-19 10:00:00'
)
;
