INSERT INTO dispatch_airport.drivers_queue AS drivers (
    driver_id,

    state,
    input_order_id,
    details,

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
    taximeter_tariffs
) VALUES
(
    'dbid0_uuid0', -- driver_id

    'entered', -- state
    '000000', -- input_order_id
    '{"session_id": "session_id_0", "lon": 1, "lat": 1, "unique_driver_id": "0000"}'::JSONB,-- details

    'old_mode', -- reason
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NOW() - INTERVAL '5 seconds',  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp
    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued
    'svo', -- airport
    ARRAY['notification']::dispatch_airport.area_t[], -- areas
    ARRAY[]::text[], --classes
    ARRAY['econom']::text[] -- taximeter_tariffs
),
(
    'dbid1_uuid1', -- driver_id

    'queued', -- state
    NULL, -- input_order_id
    '{"session_id": "session_id_1", "lon": 1, "lat": 1, "unique_driver_id": "1111", "contractor_statistics_view_notifications": ["parking_queued"]}'::JSONB, -- details

    'old_mode', -- reason
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NOW() - INTERVAL '5 seconds',  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp
    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued
    'svo', -- airport
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[], -- areas
    ARRAY[]::text[], --classes
    ARRAY['econom']::text[] -- taximeter_tariffs
),
(
    'dbid2_uuid2', -- driver_id

    'queued', -- state
    NULL, -- input_order_id
    '{"session_id": "session_id_2", "lon": 1, "lat": 1, "unique_driver_id": "2222"}'::JSONB, -- details

    'on_action', -- reason
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NOW() - INTERVAL '5 seconds',  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp
    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued
    'svo', -- airport
    ARRAY['notification']::dispatch_airport.area_t[], -- areas
    ARRAY[]::text[], --classes
    ARRAY['econom']::text[] -- taximeter_tariffs
),
(
    'dbid3_uuid3', -- driver_id

    'queued', -- state
    NULL, -- input_order_id
    '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB, -- details

    'old_mode', -- reason
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NOW() - INTERVAL '5 seconds',  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp
    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued
    'svo', -- airport
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[], -- areas
    ARRAY[]::text[], --classes
    ARRAY['econom']::text[] -- taximeter_tariffs
),
(
    'dbid4_uuid4', -- driver_id

    'queued', -- state
    NULL, -- input_order_id
    '{"session_id": "session_id_4", "lon": 1, "lat": 1, "unique_driver_id": "4444"}'::JSONB, -- details

    'old_mode', -- reason
    NOW(), -- entered
    NOW(), -- heartbeated
    NOW(), -- updated
    NULL,  -- last_freeze_started_tp
    NULL,  -- left_queue_started_tp
    NOW() - INTERVAL '5 seconds',  -- no_classes_started_tp
    NULL,  -- forbidden_by_partner_started_tp
    NOW() - INTERVAL '10 minutes',  -- queued
    jsonb_build_object('econom', NOW() - INTERVAL '10 minutes'),  -- class_queued
    'ekb', -- airport
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[], -- areas
    ARRAY[]::text[], --classes
    ARRAY['econom']::text[] -- taximeter_tariffs
);
