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
    'dbid_uuid1',

    'queued',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NOW(),
    jsonb_build_object('econom', NOW()),

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"session_id": "session1", "lon": 1, "lat": 1, "unique_driver_id": "udid1"}'::JSONB
),
(
    'dbid_uuid2',

    'queued',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NOW(),
    jsonb_build_object('econom', NOW()),

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"session_id": "session2", "lon": 1, "lat": 1, "unique_driver_id": "udid2"}'::JSONB
),
(
    'dbid_uuid3',

    'entered',
    '',
    NOW(),
    NOW(),
    NOW(),
    NOW(),
    jsonb_build_object('econom', NOW()),

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"session_id": "session3", "lon": 1, "lat": 1, "unique_driver_id": "udid3"}'::JSONB
),
(
    'dbid_uuid4',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NOW(),
    jsonb_build_object('econom', NOW()),

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    'enter_repo_session_id4',
    '{"session_id": "session4", "lon": 1, "lat": 1, "unique_driver_id": "udid4"}'::JSONB
),
(
    'dbid_uuid5',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NOW(),
    jsonb_build_object('econom', NOW()),

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    'enter_repo_session_id5',
    '{"session_id": "session5", "lon": 1, "lat": 1, "unique_driver_id": "udid5"}'::JSONB
),
(
    'dbid_uuid6',

    'queued',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NOW(),
    jsonb_build_object('econom', NOW()),

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"session_id": "session6", "lon": 1, "lat": 1, "unique_driver_id": "udid6", "parking_relocation_session": "old_relo_session6"}'::JSONB
),
(
    'dbid_uuid7',

    'queued',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NOW(),
    jsonb_build_object('econom', NOW()),

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"session_id": "session7", "lon": 1, "lat": 1, "unique_driver_id": "udid7", "parking_relocation_session": "old_relo_session7"}'::JSONB
),
(
    'dbid_uuid8',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NOW(),
    jsonb_build_object('econom', NOW()),

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    'enter_repo_session_id8',
    '{"session_id": "session8", "lon": 1, "lat": 1, "unique_driver_id": "udid8"}'::JSONB
);
