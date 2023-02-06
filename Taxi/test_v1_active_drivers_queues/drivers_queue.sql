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

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('business', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['business']::text[],
  ARRAY['business']::text[],

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
  jsonb_build_object('vip', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['vip']::text[],
  ARRAY['vip']::text[],

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
  '{}'::JSONB,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY[]::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid6',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW() - INTERVAL '2 minutes',
  jsonb_build_object('econom', NOW() - INTERVAL '2 minutes'),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
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
  NOW() - INTERVAL '1 minutes',
  jsonb_build_object('econom', NOW() - INTERVAL '1 minutes'),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid8',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW()),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_8", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid9',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW() - INTERVAL '3 minutes',
  NULL, -- updated from test

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'business']::text[],
  ARRAY['econom', 'business']::text[],

  '{"session_id": "session_id_9", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid10',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW() - INTERVAL '1 minutes',
  jsonb_build_object('econom', NOW() - INTERVAL '1 minutes'),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_10", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid11',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('vip', NOW()),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['vip']::text[],
  ARRAY['vip']::text[],

  '{"session_id": "session_id_11", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid12',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW() - INTERVAL '3 minutes',
  jsonb_build_object('vip', NOW() - INTERVAL '3 minutes'),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['vip']::text[],
  ARRAY['vip']::text[],

  '{"session_id": "session_id_12", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid13',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW() - INTERVAL '2 minutes',
  jsonb_build_object('vip', NOW() - INTERVAL '2 minutes'),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['vip']::text[],
  ARRAY['vip']::text[],

  '{"session_id": "session_id_13", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid14',

  'filtered',
  'user_cancel',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_14", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid15',

  'filtered',
  'driver_cancel',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_15", "lon": 1, "lat": 1}'::JSONB
);
