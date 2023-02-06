INSERT INTO dispatch_airport.drivers_queue AS drivers (
    driver_id,

    state,
    reason,
    entered,
    heartbeated,
    updated,
    filtered_tp,

    queued,
    class_queued,

    airport,
    areas,
    classes,
    taximeter_tariffs,

    old_mode_enabled,
    details
) VALUES
(
    'dbid_uuid0',

    'filtered',
    'offline',
    timestamptz '2021-01-01T10:15:00+00', -- entered
    timestamptz '2021-01-01T10:15:00+00', -- heartbeated
    timestamptz '2021-01-01T10:15:00+00', -- updated
    timestamptz '2021-01-01T10:15:00+00', -- filtered_tp

    NULL,  -- queued
    NULL,  -- class_queued

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom']::text[],

    True,
    '{"session_id": "session_id_0", "lon": 1, "lat": 1, "taximeter_status": "off", "driver_very_busy_status": "verybusy"}'::JSONB
),
(
    'dbid_uuid1',

    'filtered',
    'wrong_client',
    timestamptz '2021-01-01T10:15:00+00', -- entered
    timestamptz '2021-01-01T10:15:00+00', -- heartbeated
    timestamptz '2021-01-01T10:15:00+00', -- updated
    timestamptz '2021-01-01T10:15:00+00', -- filtered_tp

    NULL,  -- queued
    NULL,  -- class_queued

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom']::text[],

    True,
    '{"session_id": "session_id_1", "lon": 1, "lat": 1, "taximeter_status": "off", "driver_very_busy_status": "verybusy"}'::JSONB
),
(
    'dbid_uuid2',

    'filtered',
    'offline',
    timestamptz '2021-01-01T10:15:00+00', -- entered
    timestamptz '2021-01-01T10:15:00+00', -- heartbeated
    timestamptz '2021-01-01T10:15:00+00', -- updated
    timestamptz '2021-01-01T10:15:00+00', -- filtered_tp

    NULL,  -- queued
    NULL,  -- class_queued

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom']::text[],

    True,
    '{"session_id": "session_id_2", "lon": 1, "lat": 1, "taximeter_status": "off", "driver_very_busy_status": "verybusy"}'::JSONB
);
