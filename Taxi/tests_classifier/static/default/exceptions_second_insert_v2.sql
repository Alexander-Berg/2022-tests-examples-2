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
    '4444',
    'number_4',
    ARRAY['moscow', 'spb'],
    ARRAY['econom', 'vip'],
    '2019-11-20T00:00:00+0000',
    '2019-12-27T00:00:00+0000',
    '2021-12-23T00:00:00+0000'
);
