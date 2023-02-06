INSERT INTO dispatch_airport.drivers_queue AS drivers (
  driver_id,

  state,
  reason,
  entered,
  heartbeated,
  updated,
  offline_started_tp,
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
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- offline_started_tp
  NULL,
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus']::text[],
  ARRAY['comfortplus']::text[],

  '{"session_id": "session_id_3", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid5',

  'entered',
  'old_mode',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- offline_started_tp
  NULL,
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus']::text[],
  ARRAY['business2', 'comfortplus']::text[],

  '{"session_id": "session_id_5", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid6',

  'queued',
  'old_mode',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- offline_started_tp
  NOW() - INTERVAL '1 minute',
  jsonb_build_object('econom', NOW() - INTERVAL '1 minute'),

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
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- offline_started_tp
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_7", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid10',

  'queued',
  'old_mode',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- offline_started_tp
  NOW(),
  jsonb_build_object('econom', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_10", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid11',

  'entered',
  'old_mode',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NOW(),  -- offline_started_tp
  NULL,
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_11", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid12',

  'queued',
  'old_mode',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- offline_started_tp
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['comfortplus', 'econom']::text[],

  '{"session_id": "session_id_12", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid13',

  'queued',
  'old_mode',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- offline_started_tp
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY['econom']::text[],

  '{"session_id": "session_id_13", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid14',

  'queued',
  'old_mode',
  NOW(), -- entered
  NOW(), -- heartbeated
  NOW(), -- updated
  NULL,  -- offline_started_tp
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'econom']::text[],
  ARRAY[]::text[],

  '{"session_id": "session_id_14", "lon": 1, "lat": 1}'::JSONB
);
