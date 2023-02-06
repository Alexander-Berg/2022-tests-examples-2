INSERT INTO dispatch_airport.drivers_queue AS drivers (
    driver_id,

    state,
    reason,
    entered,
    heartbeated,
    updated,
    last_freeze_started_tp,
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

    'entered',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'old_session_id1',
    '{"unique_driver_id": "udid1", "session_id": "old_session_id1", "lon": 35, "lat": 25, "session_orders": {"order_id_0": false}}'::JSONB
),
(
    'dbid_uuid2',

    'queued',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NOW(),
    jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'old_session_id2',
    '{"unique_driver_id": "udid2", "session_id": "old_session_id2", "lon": 35, "lat": 25,
      "session_orders": {"order_id_0": false, "order_id_4": true}}'::JSONB
),
(
    'dbid_uuid3',

    'queued',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NOW(),
    jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'old_session_id3',
    '{"unique_driver_id": "udid3", "session_id": "old_session_id3", "lon": 35, "lat": 25,
      "session_orders": {"order_id_5": true, "order_id_7": false, "order_id_3": true}}'::JSONB
),
(
    'dbid_uuid4',

    'queued',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NOW(),
    jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

    'old_session_id4',
    '{"unique_driver_id": "udid4", "session_id": "old_session_id4", "lon": 35, "lat": 25,
      "in_terminal_area": true}'::JSONB
);
