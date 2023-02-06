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
    'created',
    null,
    'test_data_file_url',
    'v1',
    null,
    '2021-08-16 10:00:00',
    '2021-08-16 10:00:00'
);

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
    'task_2',
    'place_id_2',
    'availability',
    'created',
    null,
    'test_data_file_url',
    'v1',
    null,
    '2021-08-16 10:00:00',
    '2021-08-16 10:00:00'
);

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
    'task_3',
    'place_id_3',
    'stock',
    'created',
    null,
    'test_data_file_url',
    'v1',
    null,
    '2021-08-16 10:00:00',
    '2021-08-16 10:00:00'
),
(
    'task_4',
    'place_id_4',
    'price',
    'created',
    null,
    'test_data_file_url',
    'v1',
    null,
    '2021-08-16 10:00:00',
    '2021-08-16 10:00:00'
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
    'brand',
    'parser_name',
    1,
    '{"elem": 1}'::json,
    '2021-08-16 10:00:00',
    '2021-08-16 10:00:00'
)
;

INSERT INTO places
(
    place_id,
    place_group_id,
    external_id,
    business_type,
    created_at,
    updated_at,
    brand_id
)
VALUES
(
    'place_id',
    'place_group_id',
    'external_id',
    null,
    '2021-08-16 10:00:00',
    '2021-08-16 10:00:00',
    'brand'
),
(
    'place_id_3',
    'place_group_id',
    'external_id',
    null,
    '2021-08-16 10:00:00',
    '2021-08-16 10:00:00',
    'brand'
),
(
    'place_id_4',
    'place_group_id',
    'external_id',
    'restaurant',
    '2021-08-16 10:00:00',
    '2021-08-16 10:00:00',
    'brand'
);
