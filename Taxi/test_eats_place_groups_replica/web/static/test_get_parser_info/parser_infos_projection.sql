insert into place_groups
(
    place_group_id,
    brand_id,
    parser_name,
    stock_reset_limit,
    dev_filter,
    parser_options,
    
    created_at,
    updated_at
)
values
(
    'place_group_id1',
    'brand_id1',
     'parser_name',
    1,
    '{"elem": 1}'::json,
    '{"some_parser_option": "some_parser_option_value"}'::json,
    '2019-08-19 10:00:00',
    '2019-08-19 10:00:00'
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
)
;
