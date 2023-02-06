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
  details,
  car_number
) VALUES
(
  'dbid_uuid1',

  'entered',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  'old_session_id1',
  '{"unique_driver_id": "udid1", "session_id": "old_session_id1", "lon": 35, "lat": 25, "reposition_session_mode": "Sintegro"}'::JSONB,
  'a123bc'
),
(
    'dbid_uuid2',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,
    NULL,

    'svo',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],
    'old_session_id2',
    '{"unique_driver_id": "udid2", "session_id": "old_session_id2", "lon": 65, "lat": 25, "reposition_session_mode": "Sintegro"}'::JSONB,
    'a123de'
),
(
  'dbid_uuid3',

  'queued',
  'on_action',
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
  NULL,
  '{"unique_driver_id": "udid3", "session_id": "old_session_id3", "lon": 30, "lat": 20}'::JSONB,
  'a123fg'
),
(
  'dbid_uuid4',

  'queued',
  'on_action',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus']::text[],
  ARRAY['econom', 'comfortplus']::text[],

  NULL,
  '{"unique_driver_id": "udid4", "session_id": "old_session_id4", "lon": 70, "lat": 20}'::JSONB,
  'a123hi'
),
(
    'dbid_uuid7',

    'filtered',
    'gps',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NOW(),
    NULL,

    'svo',
    ARRAY[]::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

   NULL,
    '{"unique_driver_id": "udid7", "session_id": "old_session_id7", "lon": 50, "lat": 1}'::JSONB,
    'a123jl'
),
(
    'dbid_uuid8',

    'entered',
    'on_reposition',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,
    NULL,

    'svo',
    ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
    ARRAY['comfortplus']::text[],
    ARRAY['comfortplus']::text[],

    'old_session_id8',
    '{"unique_driver_id": "udid8", "session_id": "old_session_id8", "lon": 65, "lat": 25, "reposition_session_mode": "Sintegro"}'::JSONB,
    'a123mn'
),
(
    'dbid_uuid9',

    'filtered',
    'gps',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NOW(),
    NULL,

    'svo',
    ARRAY[]::dispatch_airport.area_t[],
    ARRAY['econom', 'comfortplus']::text[],
    ARRAY['econom', 'comfortplus']::text[],

   NULL,
    '{"unique_driver_id": "udid9", "session_id": "old_session_id9", "lon": 50, "lat": 1}'::JSONB,
    'a123op'
);
