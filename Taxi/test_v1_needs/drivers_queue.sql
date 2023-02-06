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
  'dbid_uuid1',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('econom', NOW(), 'comfortplus', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus', 'vip']::text[],
  ARRAY['econom', 'comfortplus', 'vip']::text[],

  '{"session_id": "session_id_1", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid2',

  'queued',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('business', NOW(), 'vip', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['business', 'vip']::text[],
  ARRAY['business', 'vip']::text[],

  '{"session_id": "session_id_2", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid3',

  'entered',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NULL,
  NULL,

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['econom', 'comfortplus', 'vip']::text[],
  ARRAY['econom', 'comfortplus', 'vip']::text[],

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
  jsonb_build_object('business', NOW(), 'vip', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['business', 'vip']::text[],
  ARRAY['business', 'vip']::text[],

  '{"session_id": "session_id_4", "lon": 1, "lat": 1, "taximeter_status": "order_free"}'::JSONB
),
(
  'dbid_uuid5',

  'queued',
  'old_mode',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('comfortplus', NOW(), 'vip', NOW()),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus', 'vip']::text[],
  ARRAY['comfortplus', 'vip']::text[],

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
  jsonb_build_object('comfortplus', NOW()),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus']::text[],
  ARRAY['comfortplus']::text[],

  '{"session_id": "session_id_6", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid9',

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

  '{"session_id": "session_id_9", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid10',

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

  '{"session_id": "session_id_10", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid11',

  'entered',
  'on_action',
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

  'entered',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('vip', NOW()),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['vip', 'comfortplus']::text[],
  ARRAY['vip', 'comfortplus']::text[],

  '{"session_id": "session_id_12", "lon": 1, "lat": 1, "reposition_session_mode": "Sintegro"}'::JSONB
),
(
  'dbid_uuid13',

  'entered',
  'on_tag',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('comfortplus', NOW()),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus']::text[],
  ARRAY['comfortplus']::text[],

  '{"session_id": "session_id_13", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid14',

  'entered',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('comfortplus', NOW()),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus']::text[],
  ARRAY['comfortplus']::text[],

  '{"session_id": "session_id_14", "lon": 1, "lat": 1, "reposition_session_mode": "Airport"}'::JSONB
),
(
  'dbid_uuid15',

  'entered',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('comfortplus', NOW()),

  'svo',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['comfortplus']::text[],
  ARRAY['comfortplus']::text[],

  '{"session_id": "session_id_15", "lon": 1, "lat": 1}'::JSONB
),
(
  'dbid_uuid16',

  'entered',
  'on_reposition',
  NOW(),
  NOW(),
  NOW(),
  NOW(),
  jsonb_build_object('vip', NOW()),

  'ekb',
  ARRAY['notification', 'waiting']::dispatch_airport.area_t[],
  ARRAY['vip']::text[],
  ARRAY['vip']::text[],

  '{"session_id": "session_id_16", "lon": 1, "lat": 1, "reposition_session_mode": "Sintegro"}'::JSONB
);
