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

    details
) VALUES
(
    'dbid_uuid1',

    'entered',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,  -- queued
    NULL,  -- class_queued

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid2',

    'queued',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NOW() - INTERVAL '20 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '20 minutes', 'comfortplus', NOW() - INTERVAL '20 minutes'), -- class_queued

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid3',

    'entered',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,  -- queued
    NULL,  -- class_queued

    'svo',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid4',

    'queued',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NOW() - INTERVAL '20 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '20 minutes', 'comfortplus', NOW() - INTERVAL '20 minutes'), -- class_queued

    'svo',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
);
