insert into place_groups
(
    place_group_id,
    brand_id
)
values
(
    'place_group_id1',
    'brand_id1'
)
;

insert into places
(
    place_id,
    place_group_id,
    external_id
)
values
(
    'place_id1',
    'place_group_id1',
    'external_place_id1'
)
;

insert into place_items
(
    place_item_id,
    external_id,
    place_id,
    created_at,
    updated_at
)
values
(
    'id1',
    'external_id1',
    'place_id1',

    '2021-08-19 10:00:00',
    '2021-08-19 10:00:00'
),
(
    'id2',
    'external_id2',
    'place_id1',

    '2021-08-19 10:00:01',
    '2021-08-19 10:00:00'
),
(
    'id3',
    'external_id4',
    'place_id1',

    '2021-08-19 10:00:02',
    '2021-08-19 10:00:00'
),
(
    'id4',
    'external_id4',
    'place_id1',

    '2021-08-19 10:00:03',
    '2021-08-19 10:00:00'
),
(
    'id5',
    'external_id5',
    'place_id1',

    '2021-08-19 10:00:04',
    '2021-08-19 10:00:00'
),
(
    'id6',
    'external_id6',
    'place_id1',

    '2021-08-19 10:00:05',
    '2021-08-19 10:00:00'
),
(
    'id7',
    'external_id7',
    'place_id1',

    '2021-08-19 10:00:06',
    '2021-08-19 10:00:00'
),
(
    'id8',
    'external_id8',
    'place_id1',

    '2021-08-19 10:00:07',
    '2021-08-19 10:00:00'
),
(
    'id9',
    'external_id9',
    'place_id1',

    '2021-08-19 10:00:08',
    '2021-08-19 10:00:00'
),
(
    'id0',
    'external_id0',
    'place_id1',

    '2021-08-19 10:00:09',
    '2021-08-19 10:00:00'
)
;
