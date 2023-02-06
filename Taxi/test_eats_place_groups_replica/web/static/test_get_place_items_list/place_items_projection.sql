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
)
;
