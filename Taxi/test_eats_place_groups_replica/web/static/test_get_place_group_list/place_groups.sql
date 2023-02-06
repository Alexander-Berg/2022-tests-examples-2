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
    'id1',
    'brand1',
    'parser_name',
    1,
    '{"elem": 1}'::json,
    '{"some_parser_option": "some_parser_option_value"}'::json,
    '2021-08-19 10:00:00',
    '2021-08-19 10:00:00'
),

(
    'id2',
    'brand2',
    'parser_name2',
    2,
    '{"elem": 2}'::json,
    '{"some_parser_option_2": "some_parser_option_value_2"}'::json,
    '2021-08-19 10:00:01',
    '2021-08-19 10:00:00'
)
;
