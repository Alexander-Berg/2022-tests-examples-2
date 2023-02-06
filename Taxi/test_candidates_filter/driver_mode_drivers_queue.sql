INSERT INTO dispatch_airport.drivers_queue AS drivers (
    driver_id,

    state,
    reason,
    entered,
    heartbeated,
    updated,
    queued,
    class_queued,

    driver_mode,

    airport,
    areas,
    classes,
    taximeter_tariffs,

    details
) VALUES
(
    'dbid_uuid0',

    'entered',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY[]::text[],

    '{"session_id": "session_id_0", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid2',

    'entered',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY[]::text[],

    '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid3',

    'queued',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NOW() - INTERVAL '1 minute',
    jsonb_build_object('econom', NOW() - INTERVAL '1 minute'),
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid4',

    'entered',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,
    NULL,
    'old',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid5',

    'queued',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NOW() - INTERVAL '1 minute',
    jsonb_build_object('econom', NOW() - INTERVAL '1 minute'),
    'old',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid6',

    'queued',
    'on_action',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NOW() - INTERVAL '1 minute',
    jsonb_build_object('comfortplus', NOW() - INTERVAL '1 minute'),
    'new',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['comfortplus']::text[],
    ARRAY['comfortplus']::text[],

    '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid7',

    'entered',
    'on_action',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,
    NULL,
    'new',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['comfortplus']::text[],
    ARRAY['comfortplus']::text[],

    '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid8',

    'entered',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,
    NULL,
    'mixed',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_8", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid9',

    'entered',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,
    NULL,
    'mixed',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_9", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid10',

    'entered',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,
    NULL,
    'mixed',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_10", "lon": 1, "lat": 1}'::JSONB
);
