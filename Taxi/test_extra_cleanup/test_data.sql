INSERT INTO signal_device_api.events (
    device_id,
    created_at,
    updated_at,
    event_at,
    event_type,
    event_id,
    extra
)
VALUES
(
    1,
    CURRENT_TIMESTAMP - interval '32 hours',
    CURRENT_TIMESTAMP - interval '32 hours',
    CURRENT_TIMESTAMP - interval '33 hours',
    'sleep',
    '1',
    'BlaBlaBla'
),
(
    2,
    CURRENT_TIMESTAMP - interval '27 hours',
    CURRENT_TIMESTAMP - interval '27 hours',
    CURRENT_TIMESTAMP - interval '28 hours',
    'sleep',
    '2',
    'SomeData'
),
(
    3,
    CURRENT_TIMESTAMP - interval '25 hours',
    CURRENT_TIMESTAMP - interval '25 hours',
    CURRENT_TIMESTAMP - interval '26 hours',
    'sleep',
    '3',
    'BlaBlaBla'
),
(
    6,
    CURRENT_TIMESTAMP - interval '40 hours',
    CURRENT_TIMESTAMP - interval '40 hours',
    CURRENT_TIMESTAMP - interval '43 hours',
    'sleep',
    '4',
    NULL
),
(
    4,
    CURRENT_TIMESTAMP - interval '12 hours',
    CURRENT_TIMESTAMP - interval '12 hours',
    CURRENT_TIMESTAMP - interval '13 hours',
    'sleep',
    '4',
    'BlaBlaBla'
),
(
    5,
    CURRENT_TIMESTAMP - interval '4 hours',
    CURRENT_TIMESTAMP - interval '4 hours',
    CURRENT_TIMESTAMP - interval '5 hours',
    'sleep',
    '5',
    'BlaBlaBla'
);
