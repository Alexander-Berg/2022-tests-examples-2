INSERT INTO classifier.exceptions_v2 (
    id,
    car_number,
    zones,
    tariffs,
    started_at,
    ended_at,
    updated_at,
    is_deleted
)
VALUES
(
    '0000',
    'number_0',
    ARRAY['city1'],
    ARRAY['econom'],
    '2019-11-20T00:00:00+0000',
    '2019-12-27T00:00:00+0000',
    '2021-12-19T00:00:00+0000',
    TRUE
);

INSERT INTO classifier.exceptions_v2 (
    id,
    car_number,
    zones,
    tariffs,
    started_at,
    ended_at,
    updated_at
)
VALUES
(
    '1111',
    'number_1',
    ARRAY['moscow', 'spb'],
    ARRAY['econom', 'vip'],
    '2019-11-20T00:00:00+0000',
    '2019-12-27T00:00:00+0000',
    '2021-12-19T00:00:00+0000'
),
(
    '2222',
    'number_2',
    ARRAY[]::TEXT[],
    ARRAY['econom', 'vip'],
    '2020-08-16T00:00:00+0000',
    NULL,
    '2021-12-20T00:00:00+0000'
),
(
    '3333',
    'number_3',
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    NULL,
    NULL,
    '2021-12-21T00:00:00+0000'
),
(
    '3334',
    'number_34',
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    NULL,
    NULL,
    '2021-12-22T00:00:00+0000'
);
