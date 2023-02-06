INSERT INTO signal_device_tracks.events
(
    device_id,
    device_serial_number,
    event_id,
    event_at,
    event_type,
    park_id
)
VALUES
(
    1,
    'serial1',
    'd58841a1f4b7816b84ccf4fcb7d886f7',
    '2020-02-25T23:57:00+00', -- event at
    'driver_lost',
    'p2'
),
(
    1,
    'serial1',
    'd68841a1f4b7816b84ccf4fcb7d886f7',
    '2020-02-25T23:57:00+00', -- event at
    'lol',
    'p2'
),
(
    1,
    'serial1',
    '0a252859f6e1e3942eed9b5f16bd9bf5',
    '1999-12-31T23:59:59+00', -- event at
    'distraction',
    'p2'
),
(
    1,
    'serial1',
    '0ef0466e6e1331b3a7d35c5859830666',
    '2090-12-06T13:00:00+00', -- event at
    'driver_lost',
    'p6'
),
(
    1,
    'serial1',
    '0ef0466e6e1331b3a7d35c5859830777',
    '2090-12-06T12:00:00+00', -- event at
    'sleep',
    'p6'
);
