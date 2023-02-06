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
    'dbid_uuid2',

    'entered',
    'on_reposition',
    '2021-01-01T10:15:00+00:00', -- entered
    '2021-01-01T10:15:00+00:00', -- heartbeated
    '2021-01-01T10:15:00+00:00', -- updated
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['comfortplus']::text[],
    ARRAY['comfortplus']::text[],

    'rsid2',
    '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid3',

    'entered',
    'old_mode',
    '2021-01-01T10:15:00+00:00', -- entered
    '2021-01-01T10:15:00+00:00', -- heartbeated
    '2021-01-01T10:15:00+00:00', -- updated
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['comfortplus', 'econom']::text[],
    ARRAY['comfortplus', 'econom']::text[],

    NULL,
    '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid4',

    'entered',
    'old_mode',
    '2021-01-01T10:15:00+00:00', -- entered
    '2021-01-01T10:15:00+00:00', -- heartbeated
    '2021-01-01T10:15:00+00:00', -- updated
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['comfortplus', 'econom']::text[],
    ARRAY['comfortplus', 'econom']::text[],

    NULL,
    '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid5',

    'entered',
    'on_tag',
    '2021-01-01T10:15:00+00:00', -- entered
    '2021-01-01T10:15:00+00:00', -- heartbeated
    '2021-01-01T10:15:00+00:00', -- updated
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['comfortplus', 'econom']::text[],
    ARRAY['comfortplus', 'econom']::text[],

    NULL,
    '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid6',

    'entered',
    'on_repeat_queue',
    '2021-01-01T10:15:00+00:00', -- entered
    '2021-01-01T10:15:00+00:00', -- heartbeated
    '2021-01-01T10:15:00+00:00', -- updated
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['comfortplus', 'econom']::text[],
    ARRAY['comfortplus', 'econom']::text[],

    NULL,
    '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid7',

    'queued',
    'on_action',
    '2021-01-01T10:15:00+00:00', -- entered
    '2021-01-01T10:15:00+00:00', -- heartbeated
    '2021-01-01T10:15:00+00:00', -- updated
    '2021-01-01T10:14:55+00:00',
    jsonb_build_object('econom', '2021-01-01T10:15:00+00:00', 'comfortplus', '2021-01-01T10:15:00+00:00'),  -- class_queued,

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['comfortplus', 'econom']::text[],
    ARRAY['comfortplus', 'econom']::text[],

    NULL,
    '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid8',

    'queued',
    'on_reposition_old_mode',
    '2021-01-01T10:15:00+00:00', -- entered
    '2021-01-01T10:15:00+00:00', -- heartbeated
    '2021-01-01T10:15:00+00:00', -- updated
    '2021-01-01T10:15:00+00:00',
    NULL,  -- class_queued,

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['comfortplus', 'econom']::text[],
    ARRAY['comfortplus', 'econom']::text[],

    NULL,
    '{"session_id": "session_id_8", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid9',

    'queued',
    'old_mode',
    '2021-01-01T10:15:00+00:00', -- entered
    '2021-01-01T10:15:00+00:00', -- heartbeated
    '2021-01-01T10:15:00+00:00', -- updated
    '2021-01-01T10:15:00+00:00',
    jsonb_build_object('econom', '2021-01-01T09:55:00+00:00', 'comfortplus', '2021-01-01T09:55:00+00:00'),  -- class_queued,

    'ekb',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['comfortplus', 'econom']::text[],
    ARRAY['comfortplus', 'econom']::text[],

    NULL,
    '{"session_id": "session_id_9", "lon": 1, "lat": 1}'::JSONB
);
