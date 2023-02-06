INSERT INTO dispatch_airport.drivers_queue AS drivers (
    driver_id,

    state,
    reason,
    entered,
    heartbeated,
    updated,

    last_freeze_started_tp,
    left_queue_started_tp,
    no_classes_started_tp,
    forbidden_by_partner_started_tp,

    queued,
    class_queued,

    airport,
    areas,
    classes,
    taximeter_tariffs,

    details
) VALUES
(
    'dbid_uuid0',

    'queued',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated

    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NOW() - INTERVAL '5 seconds',  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp

    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid2',

    'entered',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated

    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NULL,  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp

    NULL,  -- queued
    NULL,  -- class_queued

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid3',

    'queued',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated

    NULL,  -- last_freeze_started_tp
    NOW() - INTERVAL '5 minutes',  -- left_queue_started_tp
    NULL,  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp

    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued

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

    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NULL,  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp

    NULL,  -- queued
    NULL,  -- class_queued

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid5',

    'entered',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated

    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NULL,  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp

    NULL,  -- queued
    NULL,  -- class_queued

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY[]::text[],

    '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid6',

    'queued',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated

    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NULL,  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp

    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY[]::text[],

    '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid7',

    'queued',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated

    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NULL,  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp

    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid8',

    'queued',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated

    NOW() - INTERVAL '5 seconds',  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NULL,  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp

    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued

    'ekb',
    ARRAY['notification', 'main', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_8", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid9',

    'entered',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated

    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NOW() - INTERVAL '5 seconds',  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp

    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_9", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid10',

    'queued',
    'old_mode',
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated

    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NOW() - INTERVAL '5 seconds',  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp

    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued

    'ekb',
    ARRAY['notification', 'main', 'waiting']::dispatch_airport.area_t[],
    ARRAY[]::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_10", "lon": 1, "lat": 1, "force_polling_order": true}'::JSONB
);
