INSERT INTO classifier.exceptions (
    car_number,
    zones,
    tariffs,
    started_at,
    ended_at
)
VALUES
(
    'number_1',
    ARRAY['moscow', 'spb'],
    ARRAY['econom', 'vip'],
    '2019-11-20T00:00:00+0000',
    '2019-12-27T00:00:00+0000'
),
(
    'number_2',
    ARRAY[]::TEXT[],
    ARRAY['econom', 'vip'],
    '2020-08-16T00:00:00+0000',
    NULL
),
(
    'number_3',
    ARRAY[]::TEXT[],
    ARRAY[]::TEXT[],
    NULL,
    NULL
);
