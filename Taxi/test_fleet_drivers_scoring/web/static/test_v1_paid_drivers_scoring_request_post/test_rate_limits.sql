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
    'clid3',
    '2020-02-02',
    'day',
    'paid',
    11,
    9,
    '2019-02-02 01:00:00.0+00',
    '2019-02-02 01:21:00.0+00'
),
(
    'clid1',
    '2020-01-27',
    'week',
    'paid',
    31,
    10,
    '2019-02-02 01:00:00.0+00',
    '2019-02-02 01:21:00.0+00'
)
