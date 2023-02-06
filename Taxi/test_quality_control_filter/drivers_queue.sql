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

  details
) VALUES
(
  'dbid_uuid3',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['waiting', 'main']::dispatch_airport.area_t[],
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
  NULL,
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['waiting', 'main']::dispatch_airport.area_t[],
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
  NOW() - INTERVAL '10 minutes',
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['waiting', 'main']::dispatch_airport.area_t[],
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
  NOW() - INTERVAL '10 minutes',
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['waiting', 'main']::dispatch_airport.area_t[],
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
  NOW() - INTERVAL '35 minutes',
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['waiting', 'main']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
);
