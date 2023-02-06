INSERT INTO integration_tasks
(
    id,
    place_id,
    type,
    status,
    reason,
    data_file_url,
    data_file_version,
    stacktrace,
    created_at,
    updated_at
)
VALUES
(
    'task',
    'place_id',
    'price',
    'finished',
    'test_reason: test_subreason: Test fail error',
    'test_data_file_url',
    'v1',
    null,
    '2022-05-25 12:01:50.385598 +00:00',
    '2022-05-26 12:01:50.385598 +00:00'
);

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
    'place_group_id',
    'brand_id',
    'parser_name',
    1,
    '{"elem": 1}'::json,
    '2022-05-25 12:01:50.385598 +00:00',
    '2022-05-26 12:01:50.385598 +00:00'
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
    'place_id',
    'place_group_id',
    'external_id',
    '2021-08-16 10:00:00',
    '2021-08-16 10:00:00'
),
('place_id2',
 'place_group_id',
 '',
 '2021-08-16 10:00:00',
 '2021-08-16 10:00:00'
 )
;
