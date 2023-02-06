INSERT INTO dispatch_airport.driver_events (
    udid,
    event_id,
    event_type,

    driver_id,
    airport_id,
    inserted_ts,
    details
) VALUES
(
    'udid1',
    'old_session_id1_1',
    'entered_marked_area',

    'dbid_uuid1',
    'ekb',
    NOW(),
    NULL
),
(
    'udid2',
    'old_session_id2_1',
    'entered_marked_area',

    'dbid_uuid2',
    'ekb',
    NOW() - INTERVAL '3 seconds',
    NULL
),
(
    'udid2',
    'old_session_id2_2',
    'entered_marked_area',

    'dbid_uuid2',
    'ekb',
    NOW() - INTERVAL '2 seconds',
    NULL
),
(
    'udid2',
    'old_session_id2_1_4',
    'got_order_when_reached_enter_limit',

    'dbid_uuid2',
    'ekb',
    NOW(),
    '{
      "enter_exceeded_order_id": "order_id_4"
    }'::JSONB
),
(
    'udid3',
    'old_session_id3_1',
    'entered_marked_area',

    'dbid_uuid3',
    'ekb',
    NOW() - INTERVAL '3 seconds',
    NULL
),
(
    'udid3',
    'old_session_id3_2',
    'entered_marked_area',

    'dbid_uuid3',
    'ekb',
    NOW() - INTERVAL '5 seconds',
    NULL
),
(
    'udid3',
    'old_session_id3_4',
    'entered_marked_area',

    'dbid_uuid3',
    'ekb',
    NOW() - INTERVAL '7 seconds',
    NULL
),
(
    'udid3',
    'old_session_id2_1_5',
    'got_order_when_reached_enter_limit',

    'dbid_uuid3',
    'ekb',
    NOW() - INTERVAL '5 seconds',
    '{
      "enter_exceeded_order_id": "order_id_5"
    }'::JSONB
),
(
    'udid3',
    'old_session_id3_2_3',
    'got_order_when_reached_enter_limit',

    'dbid_uuid3',
    'ekb',
    NOW(),
    '{
      "enter_exceeded_order_id": "order_id_3"
    }'::JSONB
),
(
    'udid4',
    'old_session_id4_1',
    'entered_marked_area',

    'dbid_uuid4',
    'ekb',
    NOW() - INTERVAL '1 seconds',
    NULL
),
(
    'udid4',
    'old_session_id4_2',
    'entered_marked_area',

    'dbid_uuid4',
    'ekb',
    NOW() - INTERVAL '2 seconds',
    NULL
),
(
    'udid4',
    'old_session_id4_3',
    'entered_marked_area',

    'dbid_uuid4',
    'ekb',
    NOW() - INTERVAL '3 seconds',
    NULL
);
