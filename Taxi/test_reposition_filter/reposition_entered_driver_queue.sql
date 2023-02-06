INSERT INTO dispatch_airport.drivers_queue AS drivers (
    driver_id,

    state,
    reason,
    entered,
    heartbeated,
    updated,
    queued,
    class_queued,

    airport,
    areas,
    classes,
    taximeter_tariffs,

    reposition_session_id,
    details
) VALUES
(
    'dbid_uuid12',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    'session_dbid_uuid12',
    '{"session_id": "session_id_12", "lon": 1, "lat": 1, "reposition_session_mode": "Sintegro"}'::JSONB
),
(
    'dbid_uuid13',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'business']::text[],
    ARRAY['econom', 'business']::text[],

    'session_dbid_uuid13',
    '{"session_id": "session_id_13", "lon": 1, "lat": 1, "reposition_session_mode": "Sintegro"}'::JSONB
),
(
    'dbid_uuid14',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    'session_dbid_uuid14',
    '{"session_id": "session_id_14", "lon": 1, "lat": 1, "reposition_session_mode": "Sintegro"}'::JSONB
),
(
    'dbid_uuid15',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    'session_dbid_uuid15',
    '{"session_id": "session_id_15", "lon": 1, "lat": 1, "reposition_session_mode": "Airport"}'::JSONB
),
(
    'dbid_uuid16',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    'session_dbid_uuid16',
    '{"session_id": "session_id_16", "lon": 1, "lat": 1, "reposition_session_mode": "Airport"}'::JSONB
),
(
    'dbid_uuid18',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'session_dbid_uuid18',
    '{"session_id": "session_id_18", "lon": 1, "lat": 1, "reposition_session_mode": "Sintegro"}'::JSONB
),
(
    'dbid_uuid19',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'session_dbid_uuid19',
    '{"session_id": "session_id_19", "lon": 1, "lat": 1, "reposition_session_mode": "Sintegro"}'::JSONB
),
(
    'dbid_uuid20',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'session_dbid_uuid20',
    '{"session_id": "session_id_20", "lon": 1, "lat": 1, "reposition_session_mode": "Sintegro"}'::JSONB
),
(
    'dbid_uuid21',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'session_dbid_uuid21',
    '{"session_id": "session_id_21", "lon": 1, "lat": 1, "reposition_session_mode": "Sintegro"}'::JSONB
),
(
    'dbid_uuid22',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'session_dbid_uuid22',
    '{"session_id": "session_id_22", "lon": 1, "lat": 1, "reposition_session_mode": "Sintegro"}'::JSONB
);
