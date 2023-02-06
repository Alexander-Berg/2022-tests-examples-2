INSERT INTO dispatch_airport.drivers_queue AS drivers (
    driver_id,

    state,
    reason,
    entered,
    heartbeated,
    updated,
    queued,

    airport,
    areas,
    classes,
    taximeter_tariffs,

    reposition_session_id,
    details
) VALUES
-- all drivers have
--     entered,
--     heartbeated,
--     updated,
--     queue
-- 15 seconds before the time of the test '2021-08-19T10:04:00+0000'
(
    'dbid_uuid1',

    'entered',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid1", "session_id": "old_session_id1", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid2',

    'entered',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid2", "session_id": "old_session_id2", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid3',

    'entered',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid3", "session_id": "old_session_id3", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid4',

    'entered',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid4", "session_id": "old_session_id4", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid5',

    'entered',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid5", "session_id": "old_session_id5", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid6',

    'queued',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid6", "session_id": "old_session_id6", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid7',

    'queued',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid7", "session_id": "old_session_id7", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid8',

    'queued',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid8", "session_id": "old_session_id8", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid9',

    'queued',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid9", "session_id": "old_session_id9", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid10',

    'entered',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'svo',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid10", "session_id": "old_session_id10", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid11',

    'queued',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'svo',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid11", "session_id": "old_session_id11", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid12',

    'queued',
    'old_mode',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid12", "session_id": "old_session_id12", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid13',

    'filtered',
    'gps',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',
    '2021-08-19T10:03:45+0000',

    'ekb',
    ARRAY['notification', 'waiting', 'main']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    NULL,
    '{"unique_driver_id": "udid13", "session_id": "old_session_id13", "lon": 1, "lat": 1}'::JSONB
);
