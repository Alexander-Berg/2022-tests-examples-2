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

  '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid3',

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

  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid4',

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

  '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid6',

    'entered',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
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

    '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
),
(
    'dbid_uuid8',

    'entered',
    'old_mode',
    NOW(),
    NOW(),
    NOW(),
    NULL,
    NULL,

    'ekb',
    ARRAY['notification']::dispatch_airport.area_t[],
    ARRAY['econom']::text[],
    ARRAY['econom']::text[],

    '{"session_id": "session_id_8", "lon": 1, "lat": 1}'::JSONB
);
