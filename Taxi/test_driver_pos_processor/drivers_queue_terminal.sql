INSERT INTO dispatch_airport.drivers_queue AS drivers (
    driver_id,

    state,
    reason,
    entered,
    heartbeated,
    updated,

    airport,
    areas,
    classes,
    taximeter_tariffs,

    details
) VALUES
(
    'dbid_uuid2',

    'entered',
    '',
    '2021-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY[]::text[],

    '{"session_id": "", "lon": 1, "lat": 1, "in_terminal_area": false}'::JSONB
),
(
    'dbid_uuid3',

    'entered',
    '',
    '2021-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY[]::text[],

    '{"session_id": "", "lon": 1, "lat": 1, "in_terminal_area": true}'::JSONB
),
(
    'dbid_uuid4',

    'entered',
    '',
    '2021-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',
    '2021-01-01T00:00:00+00:00',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY[]::text[],

    '{"session_id": "", "lon": 1, "lat": 1, "in_terminal_area": false}'::JSONB
);
