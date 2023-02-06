insert into place_groups
(
    place_group_id,
    brand_id,
    parser_name,
    stock_reset_limit
)
values
(
    'place_group_id1',
    'brand_id1',
    'parser1',
    1
),
(
    'place_group_id2',
    'brand_id1',
    'parser1',
    3
),
(
    'place_group_id3',
    'brand_id2',
    'parser11',
    4
),
(
    'place_group_id4',
    'brand_id3',
    'parser2',
    5
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
    '000',
    'place_group_id1',
    'external000',

    '2021-08-19 10:00:00',
    '2021-08-19 10:00:00'
),
(
    '001',
    'place_group_id1',
    'external001',

    '2021-08-19 10:00:01',
    '2021-08-19 10:00:00'
),
(
    '002',
    'place_group_id2',
    'external002',

    '2021-08-19 10:00:02',
    '2021-08-19 10:00:00'
),
(
    '003',
    'place_group_id3',
    'external003',

    '2021-08-19 10:00:03',
    '2021-08-19 10:00:00'
),
(
    '004',
    'place_group_id4',
    'external004',

    '2021-08-19 10:00:04',
    '2021-08-19 10:00:00'
),
(
    '005',
    'place_group_id1',
    'external005',

    '2021-06-20 10:00:05',
    '2021-08-19 10:00:00'
),
(
    '006',
    'place_group_id1',
    'external006',

    '2021-06-19 10:00:06',
    '2021-08-19 10:00:00'
),
(
    '007',
    'place_group_id1',
    'external007',

    '2021-08-19 10:00:07',
    '2021-06-20 10:00:03'
),
(
    '008',
    'place_group_id1',
    'external008',

    '2021-08-19 10:00:08',
    '2021-06-19 10:00:03'
)
;
