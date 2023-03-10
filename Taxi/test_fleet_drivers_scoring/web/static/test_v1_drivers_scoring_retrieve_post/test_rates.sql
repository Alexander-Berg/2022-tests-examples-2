INSERT INTO fleet_drivers_scoring.rates
(
    clid,
    day,
    period,
    type,
    amount,
    rate_limit,
    created_at,
    updated_at
)
VALUES
(
    'clid1',
    '2020-02-02',
    'day',
    'free',
    9,
    1,
    '2019-02-02 01:00:00.0+00',
    '2019-02-02 01:21:00.0+00'
),
(
    'clid1',
    '2020-01-27',
    'week',
    'free',
    11,
    -1,
    '2019-02-02 01:00:00.0+00',
    '2019-02-02 01:21:00.0+00'
),
(
    'clid3',
    '2020-02-02',
    'day',
    'free',
    9,
    1,
    '2019-02-02 01:00:00.0+00',
    '2019-02-02 01:21:00.0+00'
),
(
    'clid3',
    '2020-01-27',
    'week',
    'free',
    30,
    1,
    '2019-01-30 01:00:00.0+00',
    '2019-02-02 01:21:00.0+00'
)
