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
  'dbid_uuid3',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW()),

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
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_4", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid5',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
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
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid7',

  'entered',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['notification']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
);
